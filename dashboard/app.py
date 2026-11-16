from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
import streamlit as st

from dashboard.components.entity_table import render_entity_table
from dashboard.components.filter_bar import render_dimension_filters
from dashboard.components.kpi_card import render_kpi_row
from dashboard.components.quick_match import render_quick_match
from dashboard.components.time_series_chart import render_trend_chart
from dashboard.data_loader import discover_matches, load_dashboard_frames
from dashboard.field_catalog import BUYER_GROUPS, LOT_GROUPS, Field, count, display_value

VIEWS = ("Quick Match", "Coffee Lots", "Buyers", "Market", "Bids", "Audit")
INDICATORS = {
    "cpr_t": "Price-to-value ratio",
    "dir_t": "Demand intensity",
    "iur_t": "Inventory urgency",
    "cv_t": "Price variation",
    "slope_t": "Price momentum",
}
PRIVATE_KEYS = {
    "authorization", "proxy_authorization", "cookie", "set_cookie", "session_id", "password",
    "token", "access_token", "refresh_token", "team_api_key", "api_key", "apikey", "x_api_key",
    "buyer_reserve_ceiling", "reserve_ceiling",
}


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return df.astype(object).where(df.notna(), None).to_dict("records")


def _at_round(df: pd.DataFrame, selected_round: int | None) -> pd.DataFrame:
    return df[df["round"] == selected_round] if selected_round is not None and "round" in df else df


def _render_fields(record: dict[str, Any], groups: dict[str, tuple[Field, ...]]) -> None:
    sources = record.get("field_sources", {})
    for group, fields in groups.items():
        observed = any(record.get(field.key) is not None for field in fields)
        with st.expander(group, expanded=observed):
            st.dataframe(
                [
                    {"Parameter": field.label, "Value": display_value(field, record.get(field.key)),
                     "Recorded field": sources.get(field.key, "—")}
                    for field in fields
                ],
                hide_index=True, use_container_width=True,
            )


def _render_lots(lots: list[dict[str, Any]], scope: str) -> None:
    if not lots:
        st.info("No inventory was recorded for this round.")
        return
    options = {lot["lot_id"]: lot for lot in lots}
    lot = options[st.selectbox("Lot ID", list(options), key=f"inspect_lot_{scope}")]
    left, right = st.columns(2)
    with left:
        st.subheader("Bean")
        _render_fields(lot, {name.split(" / ")[1]: fields for name, fields in LOT_GROUPS.items() if name.startswith("Bean / ")})
    with right:
        st.subheader("Lot details")
        _render_fields(lot, {name: fields for name, fields in LOT_GROUPS.items() if not name.startswith("Bean / ")})


def _render_buyers(buyers: list[dict[str, Any]], scope: str) -> None:
    if not buyers:
        st.info("No buyers were recorded for this round.")
        return
    options = {buyer["buyer_id"]: buyer for buyer in buyers}
    buyer = options[st.selectbox("Buyer ID", list(options), key=f"inspect_buyer_{scope}")]
    left, right = st.columns(2)
    with left:
        _render_fields(buyer, {"Requirements": BUYER_GROUPS["Requirements"]})
    with right:
        _render_fields(buyer, {"Demand": BUYER_GROUPS["Demand"]})
        with st.expander("Settlement", expanded=buyer.get("clearing_price") is not None or buyer.get("our_won") is not None):
            price = buyer.get("clearing_price")
            won = buyer.get("our_won")
            st.write(f"Clearing price · {price:,.2f} THB/kg" if price is not None else "Clearing price · Unavailable")
            st.write(f"Buyer outcome · {('Won' if won else 'Lost') if won is not None else 'Unavailable'}")


def _render_market(rounds: pd.DataFrame, summary: dict[str, Any], selected_round: int) -> None:
    render_kpi_row([
        {"label": "Market stage", "value": str(summary.get("market_stage") or "Unavailable").replace("_", " ").title()},
        {"label": "Season", "value": str(summary.get("season_state") or "Unavailable").replace("_", " ").title()},
        {"label": "Round cap", "value": f'{int(summary["q_max"])} sacks' if summary.get("q_max") is not None else "Unavailable"},
    ])
    columns = [key for key in INDICATORS if key in rounds and rounds[key].notna().any()]
    if columns:
        history = rounds.loc[rounds["round"] <= selected_round, ["round", *columns]]
        features = history.melt(id_vars="round", var_name="Indicator")
        features["Indicator"] = features["Indicator"].map(INDICATORS)
        render_trend_chart(features, "round", "value", "Indicator", title="Market indicators through the selected round", y_label="Recorded value")
    else:
        st.caption("Market indicators are unavailable for this capture.")


def _render_bids(bids: pd.DataFrame) -> None:
    bids = render_dimension_filters(bids, [("buyer_id", "Buyer"), ("lot_id", "Lot")], key_prefix="bid_ledger")
    labels = {
        "buyer_id": "Buyer", "lot_id": "Lot", "submission": "Submission", "sacks": "Sacks",
        "v_i": "Lot value (THB/kg)", "price_per_kg": "Offer (THB/kg)",
        "margin_over_vi_pct": "Offered margin (%)", "clearing_price": "Buyer clearing (THB/kg)",
        "bid_valid": "Valid", "bid_outcome_status": "Outcome", "bid_failure_reason": "Failure reason",
    }
    render_entity_table(bids.rename(columns=labels), columns=list(labels.values()))


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[redacted]" if key.lower().replace("-", "_") in PRIVATE_KEYS else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _render_audit(raw: pd.DataFrame) -> None:
    if raw.empty:
        st.info("No events were recorded for this selection.")
        return
    metadata = raw.copy()
    if "endpoint" in metadata:
        metadata["endpoint"] = metadata["endpoint"].map(
            lambda endpoint: endpoint.split("?", 1)[0] if isinstance(endpoint, str) else None
        )
    render_entity_table(metadata, columns=["ts_utc", "round", "event_type", "endpoint", "status_code"])
    events = _records(raw)
    index = st.selectbox(
        "Inspect event", range(len(events)), index=len(events) - 1,
        format_func=lambda i: f'{events[i]["event_type"]} · {events[i].get("ts_utc") or "time unavailable"}',
    )
    st.json(_redact({key: events[index][key] for key in ("payload", "request_payload", "response_payload") if events[index].get(key) is not None}))


st.set_page_config(page_title="Robusta Market", layout="wide")
st.markdown(
    """
    <style>
    [data-testid="stMainBlockContainer"] {max-width: 1512px; padding-top: 2.25rem; padding-bottom: 3rem;}
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {gap: 0.7rem;}
    [data-testid="stMetric"] {
        padding: 0.65rem 0.9rem; border: 1px solid #dce6df; border-radius: 0.55rem; background: #f2f6f1;
    }
    [data-testid="stMetricValue"] {font-size: 1.65rem; letter-spacing: -0.035em;}
    [data-testid="stRadio"] [role="radiogroup"] {
        gap: 0.3rem 0.85rem; flex-wrap: wrap; padding: 0.2rem 0;
        border-bottom: 1px solid #dce6df;
    }
    [data-testid="stRadio"] label {padding: 0.3rem 0.35rem;}
    [data-testid="stRadio"] label:has(input:checked) {font-weight: 650;}
    [data-testid="stHorizontalBlock"] [data-testid="stButton"] {margin-top: 1.75rem;}
    [data-testid="stPlotlyChart"] {border: 1px solid #e3e8e1; border-radius: 0.55rem; padding: 0 0.3rem;}
    @media (max-width: 640px) {
        [data-testid="stHorizontalBlock"] [data-testid="stButton"] {margin-top: 0;}
        [data-testid="stPlotlyChart"] .xtick text, [data-testid="stPlotlyChart"] .ytick text {
            font-size: 10px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

title, refresh_control = st.columns([4, 1])
with title:
    st.title("Robusta Market")
with refresh_control:
    live_refresh = st.toggle("Live refresh", help="Read new capture events every five seconds.")


@st.fragment(run_every=5 if live_refresh else None)
def _dashboard() -> None:
    log_root = ROOT_DIR / "logs"
    matches = discover_matches(log_root)
    if not matches:
        st.info("No JSONL captures are available in logs or listener/logs.")
        st.button("Refresh")
        return

    capture_column, round_column, refresh_column = st.columns([3, 1.45, 1])
    with capture_column:
        capture = st.selectbox(
            "Match or capture", matches,
            format_func=lambda name: f"{name} (mock)" if "mock" in name.lower() else name,
        )
    frames = load_dashboard_frames(capture, log_root)
    rounds = frames["rounds_df"]
    round_numbers = sorted(rounds["round"].astype(int).unique(), reverse=True) if not rounds.empty else []
    with round_column:
        chosen = st.selectbox("Round", ["Latest", *round_numbers], key=f"round_{capture}")
    with refresh_column:
        st.button("Refresh", help="Read the latest logged events.", use_container_width=True)

    if chosen == "Latest":
        snapshot = rounds["board_seen"].eq(True) if "board_seen" in rounds else pd.Series(False, index=rounds.index)
        selected_round = int(rounds.loc[snapshot, "round"].max()) if snapshot.any() else (int(round_numbers[0]) if round_numbers else None)
    else:
        selected_round = int(chosen)
    selected_summary = _records(_at_round(rounds, selected_round))
    summary = selected_summary[0] if selected_summary else {}
    quota = count(summary.get("q_max"))
    context = []
    if selected_round is not None:
        total_rounds = count(summary.get("total_rounds"))
        context.append(f"Round {selected_round} of {total_rounds}" if total_rounds else f"Round {selected_round}")
    observed = pd.to_datetime(summary.get("snapshot_at"), errors="coerce", utc=True)
    if observed is not None and pd.notna(observed):
        context.append(f"Board at {observed.tz_convert('Asia/Bangkok'):%H:%M:%S} ICT")
    if quota is not None:
        context.append(f"Round cap {quota} sacks")
    if summary.get("settled") is True:
        context.append("Settled")
    if context:
        st.caption(" · ".join(context))

    view = st.radio("View", VIEWS, horizontal=True, label_visibility="collapsed", key="view")
    lot_rows = _records(_at_round(frames["lots_df"], selected_round))
    buyer_rows = _records(_at_round(frames["buyers_df"], selected_round))
    if view == "Quick Match":
        render_quick_match(lot_rows, buyer_rows, quota, capture)
    elif view == "Coffee Lots":
        _render_lots(lot_rows, capture)
    elif view == "Buyers":
        _render_buyers(buyer_rows, capture)
    elif view == "Market" and selected_round is not None:
        _render_market(rounds, summary, selected_round)
    elif view == "Bids":
        _render_bids(_at_round(frames["bids_df"], selected_round))
    elif view == "Audit":
        _render_audit(_at_round(frames["raw_df"], selected_round))
    else:
        st.info("No recorded rounds in this capture.")


_dashboard()
