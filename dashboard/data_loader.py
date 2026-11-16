from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.adapters import DynamicSchemaAdapter
from src.config import PIPELINE_CONFIG


def discover_matches(log_root: str = "logs") -> list[str]:
    """Lists all match directories and Phase 1 capture files available on disk."""
    root = Path(log_root)
    # Also check listener/logs if root logs is empty or has nothing
    alt_root = Path("listener/logs")
    targets = [root]
    if alt_root.exists():
        targets.append(alt_root)

    items: list[str] = []
    phase1_files: list[str] = []
    for r in targets:
        if r.exists():
            items.extend([p.name for p in sorted(r.iterdir()) if p.is_dir()])
            phase1_files.extend([p.name for p in sorted(r.glob("*.jsonl"))])

    all_matches = sorted(list(set(items + phase1_files)))
    return all_matches if all_matches else ["default"]


def _read_jsonl_safe(path: Path) -> list[dict[str, Any]]:
    """Reads append-only JSONL safely, ignoring any half-written trailing line during live rounds."""
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def load_dashboard_frames(match_or_file: str, log_root: str = "logs") -> dict[str, pd.DataFrame]:
    """Parses raw telemetry into 4 normalized DataFrames: rounds_df, lots_df, buyers_df, bids_df."""
    root = Path(log_root)
    target = root / match_or_file
    if not target.exists():
        alt_target = Path("listener/logs") / match_or_file
        if alt_target.exists():
            target = alt_target

    events_path = target if target.is_file() else target / "raw_events.jsonl"
    events = _read_jsonl_safe(events_path)

    adapter = DynamicSchemaAdapter(PIPELINE_CONFIG["schema_map"])
    round_rows: list[dict[str, Any]] = []
    lot_rows: list[dict[str, Any]] = []
    buyer_rows: list[dict[str, Any]] = []
    bid_rows: list[dict[str, Any]] = []

    settlement_by_round: dict[int, dict[str, Any]] = {}
    for ev in events:
        if ev.get("event_type") == "ROUND_SETTLEMENT":
            settlement_by_round[int(ev.get("round", -1))] = ev.get("payload", {})

    for ev in events:
        etype = ev.get("event_type", "")
        r_num = int(ev.get("round", 0))
        payload = ev.get("payload") or {}

        # Handle sniffer capture format (HTTP_GET, HTTP_POST, etc.)
        if "method" in ev and "path" in ev:
            proto = ev.get("protocol", "HTTP")
            req_p = ev.get("request_payload") or {}
            resp_p = ev.get("response_payload") or {}
            if "/board" in ev.get("path", "") and isinstance(resp_p, dict):
                etype = "BOARD_POLL"
                payload = resp_p
                r_num = int(resp_p.get("round", r_num or 1))
            elif "/bid" in ev.get("path", ""):
                etype = "DECISION_AND_BID"
                payload = {"stats": {}, "bids": req_p if isinstance(req_p, list) else [req_p]}

        if etype == "BOARD_POLL" and isinstance(payload, dict):
            norm_lots = adapter.normalize_lots(payload.get("lots", []))
            for lot in norm_lots:
                hum = float(lot.get("humidity", 10.0))
                lot_rows.append({
                    "round": r_num,
                    "lot_id": lot["lot_id"],
                    "lot_grade": lot["lot_grade"],
                    "bean_size": lot["bean_size"],
                    "defect_ratio": lot["defect_ratio"],
                    "humidity": hum,
                    "humidity_band": "IN_BAND_9_11" if 9.0 <= hum <= 11.0 else "OUT_OF_BAND",
                    "process": lot.get("process", "UNKNOWN"),
                    "remaining_sacks": lot["remaining_sacks"],
                })

            norm_buyers = adapter.normalize_buyers(payload.get("buyers", []))
            settle = settlement_by_round.get(r_num, {})
            clear_map = settle.get("clearing_prices", {})
            won_map = settle.get("won_by_buyer", {})
            for b in norm_buyers:
                b_id = b["buyer_id"]
                buyer_rows.append({
                    "round": r_num,
                    "buyer_id": b_id,
                    "min_grade": b["min_grade"] or "ANY",
                    "max_defect": b["max_defect"],
                    "required_process": b.get("required_process") or "ANY",
                    "demand_sacks": b["demand_sacks"],
                    "clearing_price": float(clear_map[b_id]) if b_id in clear_map else None,
                    "our_won": bool(won_map.get(b_id, False)),
                })

        elif etype == "DECISION_AND_BID" and isinstance(payload, dict):
            stats = payload.get("stats", {})
            valuations = payload.get("valuations", {})
            bids_list = payload.get("bids", [])
            round_rows.append({
                "round": r_num,
                "market_stage": stats.get("market_stage", "UNKNOWN"),
                "season_state": stats.get("season_state", "NORMAL"),
                "cpr_t": float(stats.get("cpr_t", 1.0)),
                "slope_t": float(stats.get("slope_t", 0.0)),
                "cv_t": float(stats.get("cv_t", 0.0)),
                "dir_t": float(stats.get("dir_t", 1.0)),
                "iur_t": float(stats.get("iur_t", 0.0)),
                "q_max": int(stats.get("q_max", 0)),
                "bids_submitted": len(bids_list),
                "sacks_offered": sum(int(b.get("sacks", 0)) for b in bids_list if isinstance(b, dict)),
            })

            settle = settlement_by_round.get(r_num, {})
            clear_map = settle.get("clearing_prices", {})
            won_map = settle.get("won_by_buyer", {})
            for b in bids_list:
                if not isinstance(b, dict):
                    continue
                l_id = str(b.get("lot_id", ""))
                b_id = str(b.get("buyer_id", ""))
                v_i = float(valuations.get(l_id, 120.0))
                price = float(b.get("price_per_kg", 0.0))
                margin_pct = ((price - v_i) / v_i * 100.0) if v_i > 0 else 0.0
                bid_rows.append({
                    "round": r_num,
                    "lot_id": l_id,
                    "buyer_id": b_id,
                    "sacks": int(b.get("sacks", 0)),
                    "v_i": v_i,
                    "price_per_kg": price,
                    "margin_over_vi_pct": round(margin_pct, 2),
                    "clearing_price": float(clear_map[b_id]) if b_id in clear_map else None,
                    "won": bool(won_map.get(b_id, False)),
                })

    frames = {
        "rounds_df": pd.DataFrame(round_rows),
        "lots_df": pd.DataFrame(lot_rows),
        "buyers_df": pd.DataFrame(buyer_rows),
        "bids_df": pd.DataFrame(bid_rows),
        "raw_df": pd.DataFrame(events),
    }

    # Enrich bids_df with lot_grade, process, and humidity_band when lots_df is available
    if not frames["bids_df"].empty and not frames["lots_df"].empty:
        lot_meta = (
            frames["lots_df"][["round", "lot_id", "lot_grade", "process", "humidity", "humidity_band"]]
            .drop_duplicates(subset=["round", "lot_id"])
        )
        frames["bids_df"] = frames["bids_df"].merge(lot_meta, on=["round", "lot_id"], how="left")

    return frames
