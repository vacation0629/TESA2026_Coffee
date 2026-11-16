from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

import pandas as pd

from dashboard.field_catalog import BUYER_GROUPS, LOT_GROUPS, count, number, read_record

_EVENT_TYPES = {"BOARD_POLL", "DECISION_AND_BID", "ROUND_SETTLEMENT"}
_INDICATORS = ("cpr_t", "slope_t", "cv_t", "dir_t", "iur_t")


def _capture_sources(log_root: str | Path) -> dict[str, Path]:
    root = Path(log_root)
    roots = [root, root.parent / "listener" / "logs"] if root.name == "logs" else [root]
    captures: dict[str, Path] = {}
    for root in roots:
        if not root.is_dir():
            continue
        for item in sorted(root.iterdir()):
            path = item / "raw_events.jsonl" if item.is_dir() else item
            if path.suffix == ".jsonl" and path.is_file():
                name = f"listener/{item.name}" if item.name in captures else item.name
                captures[name] = path
    return captures


def discover_matches(log_root: str | Path = "logs") -> list[str]:
    return list(_capture_sources(log_root))


def _read_jsonl_safe(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    records = []
    try:
        file = path.open(encoding="utf-8-sig", errors="replace")
    except FileNotFoundError:
        return []
    with file:
        for line in file:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)
    return records


def _records(value: Any) -> list[dict[str, Any]]:
    return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _parse_event(
    event: dict[str, Any], board_round: int | None
) -> tuple[str | None, int | None, dict[str, Any]]:
    raw_kind = event.get("event_type")
    kind = raw_kind if isinstance(raw_kind, str) else None
    payload = _mapping(event.get("payload"))
    event_round = count(event.get("round")) or count(payload.get("round"))
    if kind in _EVENT_TYPES:
        return kind, event_round, payload
    if str(payload.get("type", "")).upper() == "SETTLEMENT":
        return "ROUND_SETTLEMENT", event_round, payload

    method, path = event.get("method"), event.get("path")
    if not isinstance(path, str):
        return kind, event_round, payload
    try:
        url = urlsplit(path)
    except ValueError:
        return kind, event_round, payload
    resource = url.path.rstrip("/").split("/")[-1]
    query_round = count(parse_qs(url.query).get("round", [None])[0])
    status = count(event.get("status_code"))
    response = _mapping(event.get("response_payload"))
    ok = status is None or 200 <= status < 300
    if ok and method == "GET" and resource in {"board", "market", "result", "settlement"}:
        event_round = count(response.get("round")) or event_round or query_round
        if resource in {"result", "settlement"}:
            return "ROUND_SETTLEMENT", event_round, response
        if "lots" in response or "buyers" in response:
            return "BOARD_POLL", event_round, response
    if method == "POST" and resource == "bid":
        request = event.get("request_payload")
        request_fields = _mapping(request)
        bid_rows = request if isinstance(request, list) else request_fields.get("bids", [request_fields])
        event_round = count(request_fields.get("round")) or event_round or query_round or board_round
        submission = "Captured" if status is None else ("Submitted" if ok else "Request failed")
        return "BID_CAPTURE", event_round, {"bids": bid_rows, "submission": submission}
    return kind, event_round, payload


def _lot_with_value(lot: dict[str, Any], decision_value: float | None) -> dict[str, Any]:
    lot = lot.copy()
    lot["field_sources"] = lot["field_sources"].copy()
    value = lot["lot_evaluated_value"]
    source = "Board" if value is not None else None
    if value is None and decision_value is not None and decision_value >= 0:
        value, source = decision_value, "Agent decision"
        lot["field_sources"]["lot_evaluated_value"] = "Logged decision valuation"
    lot.update(lot_evaluated_value=value, valuation_source=source, v_i=value)

    # These columns remain available for older analysis views.
    moisture, ripeness = lot["moisture_pct"], lot["ripeness"]
    lot.update(
        moisture=moisture,
        humidity=moisture,
        humidity_band=None if moisture is None else ("IN_BAND_9_11" if 9 <= moisture <= 11 else "OUT_OF_BAND"),
        moisture_band=None if moisture is None else (
            "< 10.0% (Over-dried)" if moisture < 10 else
            "10.0-12.0% (Optimal)" if moisture <= 12 else "> 12.0% (High Moisture)"
        ),
        ripeness_tier=None if ripeness is None else (
            ">= 90% (High Ripeness)" if ripeness >= 90 else
            "80-89% (Standard)" if ripeness >= 80 else "< 80% (Under-Ripe)"
        ),
        value_tier=None if value is None else (
            "< 90 THB/kg (Commercial)" if value < 90 else
            "90-110 THB/kg (Standard)" if value <= 110 else "> 110 THB/kg (Specialty)"
        ),
    )
    return lot


def _buyer_with_settlement(buyer: dict[str, Any], settlement: dict[str, Any]) -> dict[str, Any]:
    buyer = buyer.copy()
    buyer_id = buyer["buyer_id"]
    lower, upper = number(buyer["min_humidity"]), number(buyer["max_humidity"])
    bounds = " – ".join(
        f"{operator} {value:g}%" for operator, value in (("≥", lower), ("≤", upper)) if value is not None
    )
    ripe = number(buyer["min_ripeness"])
    won = _mapping(settlement.get("won_by_buyer")).get(buyer_id)
    buyer.update(
        max_moisture=upper,
        req_moisture_band=bounds or None,
        min_ripeness_tier=None if ripe is None else f"≥ {ripe:g}%",
        clearing_price=number(_mapping(settlement.get("clearing_prices")).get(buyer_id)),
        our_won=won if isinstance(won, bool) else None,
    )
    return buyer


def load_dashboard_frames(match_or_file: str, log_root: str | Path = "logs") -> dict[str, pd.DataFrame]:
    """Build read-only dashboard views from one capture, in log order."""
    path = _capture_sources(log_root).get(match_or_file)
    events = _read_jsonl_safe(path)
    rounds: dict[int, dict[str, Any]] = {}
    lots_by_round: dict[int, dict[str, dict[str, Any]]] = {}
    buyers_by_round: dict[int, dict[str, dict[str, Any]]] = {}
    valuations: dict[int, dict[str, Any]] = {}
    settlements: dict[int, dict[str, Any]] = {}
    complete_boards: set[int] = set()
    bids = []
    raw_rows = []
    last_board_round = None

    for event in events:
        kind, r, payload = _parse_event(event, last_board_round)
        raw_rows.append({
            **event, "event_type": kind or "OTHER", "round": r,
            "endpoint": event.get("endpoint") or event.get("path"),
        })
        if r is None or kind not in {*_EVENT_TYPES, "BID_CAPTURE"}:
            continue
        round_row = rounds.setdefault(r, {"round": r})
        if kind == "BOARD_POLL":
            last_board_round = r
            complete = isinstance(payload.get("lots"), list) and isinstance(payload.get("buyers"), list)
            if not complete and r in complete_boards:
                continue
            if complete:
                complete_boards.add(r)
            lot_records = [read_record(row, LOT_GROUPS) for row in _records(payload.get("lots"))]
            buyer_records = [read_record(row, BUYER_GROUPS) for row in _records(payload.get("buyers"))]
            lots_by_round[r] = {row["lot_id"]: row for row in lot_records if row["lot_id"] is not None}
            buyers_by_round[r] = {row["buyer_id"]: row for row in buyer_records if row["buyer_id"] is not None}
            valuations.pop(r, None)
            round_row["board_seen"] = True
            round_row["snapshot_at"] = event.get("ts_utc")
            round_cap = count(payload.get("max_sacks_per_round", payload.get("q_max")))
            if round_cap is not None:
                round_row["q_max"] = round_cap
                round_row["board_quota"] = True
            total_rounds = count(payload.get("total_rounds"))
            if total_rounds is not None:
                round_row["total_rounds"] = total_rounds
            for field in ("market_status", "season_state"):
                if payload.get(field) is not None:
                    round_row[field] = payload[field]
            continue
        if kind == "ROUND_SETTLEMENT":
            settlement = settlements.setdefault(r, {})
            for key in ("clearing_prices", "won_by_buyer"):
                settlement.setdefault(key, {}).update(_mapping(payload.get(key)))
            round_row["settled"] = True
            continue

        stats = _mapping(payload.get("stats"))
        observed_values = _mapping(payload.get("valuations"))
        if observed_values:
            valuations.setdefault(r, {}).update(observed_values)
        for key in _INDICATORS:
            value = number(stats.get(key))
            if value is not None:
                round_row[key] = value
        for key in ("market_stage", "season_state"):
            if stats.get(key) is not None:
                round_row[key] = stats[key]
        for key in ("total_rounds", "q_max"):
            value = count(stats.get(key))
            if value is not None and (key != "q_max" or not round_row.get("board_quota")):
                round_row[key] = value

        for bid in _records(payload.get("bids")):
            lot_id = str(bid["lot_id"]).strip() if bid.get("lot_id") is not None else ""
            buyer_id = str(bid["buyer_id"]).strip() if bid.get("buyer_id") is not None else ""
            if not lot_id or not buyer_id:
                continue
            lot = lots_by_round.get(r, {}).get(lot_id)
            decision_value = number(observed_values.get(lot_id))
            details = {} if lot is None else _lot_with_value(lot, decision_value)
            value = decision_value if decision_value is not None else details.get("v_i")
            price, sacks = number(bid.get("price_per_kg")), count(bid.get("sacks"))
            if value is not None and value > 0 and price is not None:
                margin = round((price / value - 1) * 100, 2)
            else:
                margin = None
            bids.append({
                "round": r, "lot_id": lot_id, "buyer_id": buyer_id, "sacks": sacks,
                "v_i": value, "price_per_kg": price, "margin_over_vi_pct": margin,
                "submission": payload.get("submission", "Proposed"),
                "bid_valid": bid.get("bid_valid"),
                "bid_outcome_status": bid.get("bid_outcome_status"),
                "bid_failure_reason": bid.get("bid_failure_reason"),
                "won": bid.get("won"),
                **{key: details.get(key) for key in (
                    "process", "moisture", "moisture_band", "humidity", "humidity_band",
                    "ripeness", "ripeness_tier", "bean_shape", "value_tier", "lot_grade",
                )},
            })
            if kind == "BID_CAPTURE" and payload.get("submission") == "Submitted":
                round_row["bids_submitted"] = round_row.get("bids_submitted", 0) + 1
            round_row["sacks_offered"] = round_row.get("sacks_offered", 0) + (sacks or 0)

    lots = [
        {"round": r, **_lot_with_value(lot, number(valuations.get(r, {}).get(lot_id)))}
        for r, rows in lots_by_round.items()
        for lot_id, lot in rows.items()
    ]
    buyers = [
        {"round": r, **_buyer_with_settlement(buyer, settlements.get(r, {}))}
        for r, rows in buyers_by_round.items() for buyer in rows.values()
    ]
    for bid in bids:
        settlement = settlements.get(bid["round"], {})
        bid["clearing_price"] = number(_mapping(settlement.get("clearing_prices")).get(bid["buyer_id"]))
    return {
        "rounds_df": pd.DataFrame(rounds[r] for r in sorted(rounds)),
        "lots_df": pd.DataFrame(lots),
        "buyers_df": pd.DataFrame(buyers),
        "bids_df": pd.DataFrame(bids),
        "raw_df": pd.DataFrame(raw_rows),
    }
