from __future__ import annotations
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from dashboard.components.breakdown_chart import render_cohort_breakdown, render_compatibility_heatmap
from dashboard.components.entity_table import render_entity_table
from dashboard.components.filter_bar import render_dimension_filters
from dashboard.components.kpi_card import render_kpi_row
from dashboard.components.time_series_chart import render_trend_chart
from dashboard.data_loader import discover_matches, load_dashboard_frames

st.set_page_config(page_title="TESA 2026 Track 3 — Market Command Dashboard", layout="wide")
st.title("TESA 2026 Track 3 — Autonomous Robusta Market Dashboard")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Telemetry Source")
    matches = discover_matches("logs")
    selected_match = st.selectbox("Match / Capture Log", options=matches, index=0)
    auto_refresh = st.checkbox("Auto-Refresh (5s polling)", value=False)
    if st.button("Refresh Now"):
        st.rerun()

frames = load_dashboard_frames(selected_match, log_root="logs")
rounds_df = frames["rounds_df"]
lots_df = frames["lots_df"]
buyers_df = frames["buyers_df"]
bids_df = frames["bids_df"]
raw_df = frames["raw_df"]

tab_exec, tab_customers, tab_grades, tab_telemetry = st.tabs([
    "1. Executive Command Center",
    "2. Customer Intelligence (Multi-Buyer Requirements)",
    "3. Coffee Quality & Parameters (Moisture, Process, Ripeness, Shape, Value)",
    "4. Telemetry & Raw Audit Log",
])

# ==============================================================================
# TAB 1: EXECUTIVE COMMAND CENTER
# ==============================================================================
with tab_exec:
    latest_round = int(rounds_df["round"].max()) if not rounds_df.empty else 0
    latest_stage = str(rounds_df.iloc[-1]["market_stage"]) if not rounds_df.empty else "WAITING"
    latest_cpr = float(rounds_df.iloc[-1]["cpr_t"]) if not rounds_df.empty else 1.00
    latest_iur = float(rounds_df.iloc[-1]["iur_t"]) if not rounds_df.empty else 0.00
    avg_margin = float(bids_df["margin_over_vi_pct"].mean()) if not bids_df.empty else 0.0
    win_rate = float(bids_df["won"].mean() * 100.0) if not bids_df.empty else 0.0
    rem_sacks = (
        int(lots_df[lots_df["round"] == lots_df["round"].max()]["remaining_sacks"].sum())
        if not lots_df.empty else 0
    )

    render_kpi_row([
        {"label": "Current Round / Stage", "value": f"R{latest_round} · {latest_stage}"},
        {"label": "Clearing Price Ratio (CPR)", "value": f"{latest_cpr:.3f}x", "delta": f"{(latest_cpr - 1.0)*100:+.1f}% vs V_spec"},
        {"label": "Avg Offered Margin vs V_i", "value": f"{avg_margin:+.2f}%", "delta": f"Win Rate: {win_rate:.1f}%"},
        {"label": "Remaining Sacks / IUR", "value": f"{rem_sacks} sacks", "delta": f"Urgency IUR: {latest_iur:.2f}", "delta_color": "inverse"},
    ])

    c1, c2 = st.columns(2)
    with c1:
        if not rounds_df.empty:
            melted_stats = rounds_df.melt(
                id_vars=["round", "market_stage"],
                value_vars=["cpr_t", "dir_t", "iur_t"],
                var_name="indicator",
                value_name="value",
            )
            render_trend_chart(
                melted_stats,
                x_col="round",
                y_col="value",
                color_by="indicator",
                title="Live Statistical Market Regime Indicators (CPR, DIR, IUR)",
                y_label="Ratio",
                reference_lines=[{"y": 1.0, "label": "Equilibrium (1.0)", "color": "#888888"}],
            )
        else:
            st.info("No round telemetry recorded yet.")
    with c2:
        render_trend_chart(
            bids_df,
            x_col="round",
            y_col="margin_over_vi_pct",
            color_by="buyer_id",
            title="Submitted Bid Margin (%) Over Evaluated Value V_i",
            y_label="Margin (%)",
            reference_lines=[
                {"y": 0.0, "label": "V_i Break-Even (0%)", "color": "#2CA02C"},
                {"y": -19.0, "label": "Hard Floor 0.81*V_i (-19%)", "color": "#D62728"},
            ],
        )

    exec_cols = [c for c in ["round", "buyer_id", "lot_id", "process", "moisture", "ripeness", "bean_shape", "sacks", "v_i", "price_per_kg", "margin_over_vi_pct", "clearing_price", "won"] if c in bids_df.columns]
    render_entity_table(
        bids_df,
        columns=exec_cols,
        title="Round-by-Round Bid Execution & Settlement Ledger",
    )

# ==============================================================================
# TAB 2: CUSTOMER INTELLIGENCE (MULTI-BUYER REQUIREMENTS)
# ==============================================================================
with tab_customers:
    filtered_buyers = render_dimension_filters(
        buyers_df,
        dimensions=[
            ("buyer_id", "Customer / Buyer Bot"),
            ("required_process", "Required Process (Dry / Wet)"),
            ("req_moisture_band", "Moisture Requirement"),
            ("min_ripeness_tier", "Min Ripeness Requirement"),
            ("shape_requirement", "Bean Shape Requirement"),
        ],
        key_prefix="cust_tab",
    )
    filtered_customer_bids = render_dimension_filters(
        bids_df,
        dimensions=[("buyer_id", "Filter Bids by Customer")],
        key_prefix="cust_bids",
    )

    num_buyers = int(filtered_buyers["buyer_id"].nunique()) if not filtered_buyers.empty else 0
    total_demand = int(filtered_buyers["demand_sacks"].sum()) if not filtered_buyers.empty else 0
    avg_clear = float(filtered_buyers["clearing_price"].dropna().mean()) if (not filtered_buyers.empty and filtered_buyers["clearing_price"].notna().any()) else 0.0
    cust_win_rate = float(filtered_customer_bids["won"].mean() * 100.0) if not filtered_customer_bids.empty else 0.0

    render_kpi_row([
        {"label": "Active Customer Archetypes", "value": f"{num_buyers} buyers"},
        {"label": "Cumulative Board Demand", "value": f"{total_demand} sacks"},
        {"label": "Avg Buyer Clearing Price", "value": f"{avg_clear:.2f} THB/kg" if avg_clear > 0 else "Pending"},
        {"label": "Filtered Customer Win Rate", "value": f"{cust_win_rate:.1f}%"},
    ])

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        render_trend_chart(
            filtered_buyers,
            x_col="round",
            y_col="clearing_price",
            color_by="buyer_id",
            title="Clearing Price Trajectory by Customer Archetype",
            y_label="THB/kg",
        )
    with col_b2:
        render_cohort_breakdown(
            filtered_buyers,
            group_col="buyer_id",
            metric_col="demand_sacks",
            agg_fn="sum",
            chart_type="bar",
            title="Total Demand Volume (Sacks) by Customer",
        )

    buyer_table_cols = [c for c in ["round", "buyer_id", "required_process", "req_moisture_band", "min_ripeness_tier", "shape_requirement", "demand_sacks", "clearing_price", "our_won"] if c in filtered_buyers.columns]
    render_entity_table(
        filtered_buyers,
        columns=buyer_table_cols,
        title="Customer Specification & Clearing History",
    )

# ==============================================================================
# TAB 3: COFFEE QUALITY & PHYSICAL PARAMETERS (MOISTURE, PROCESS, RIPENESS, SHAPE, VALUE)
# ==============================================================================
with tab_grades:
    filtered_lots = render_dimension_filters(
        lots_df,
        dimensions=[
            ("process", "Process (Dry vs Wet)"),
            ("moisture_band", "Moisture (Humidity %)"),
            ("ripeness_tier", "Ripeness (Scale 0-100%)"),
            ("bean_shape", "Bean Shape (Whole vs Broken)"),
            ("value_tier", "Evaluated Value V_i (THB/kg)"),
        ],
        key_prefix="quality_tab",
    )

    num_lots = int(filtered_lots["lot_id"].nunique()) if not filtered_lots.empty else 0
    avg_moisture = float(filtered_lots["moisture"].mean()) if (not filtered_lots.empty and "moisture" in filtered_lots.columns) else 0.0
    avg_ripeness = float(filtered_lots["ripeness"].mean()) if (not filtered_lots.empty and "ripeness" in filtered_lots.columns) else 0.0
    whole_pct = float((filtered_lots["bean_shape"] == "WHOLE").mean() * 100.0) if (not filtered_lots.empty and "bean_shape" in filtered_lots.columns) else 0.0
    avg_v = float(filtered_lots["v_i"].mean()) if (not filtered_lots.empty and "v_i" in filtered_lots.columns) else 0.0

    render_kpi_row([
        {"label": "Active Coffee Lots", "value": f"{num_lots} lots"},
        {"label": "Mean Moisture Content", "value": f"{avg_moisture:.1f}%", "delta": "Target: 10.0–12.0%"},
        {"label": "Mean Ripeness", "value": f"{avg_ripeness:.1f}%", "delta": "Scale: 0–100%"},
        {"label": "Whole Bean Integrity", "value": f"{whole_pct:.1f}%", "delta": f"Broken: {100.0 - whole_pct:.1f}%"},
        {"label": "Mean Evaluated Value (V_i)", "value": f"{avg_v:.2f} THB/kg"},
    ])

    g1, g2 = st.columns(2)
    with g1:
        render_cohort_breakdown(
            bids_df,
            group_col="process" if "process" in bids_df.columns else "lot_id",
            metric_col="margin_over_vi_pct",
            agg_fn="mean",
            color_col="bean_shape" if "bean_shape" in bids_df.columns else None,
            chart_type="bar",
            title="Realized Margin (%) by Process (Dry vs Wet) & Bean Shape",
        )
    with g2:
        render_compatibility_heatmap(
            bids_df,
            row_col="buyer_id",
            col_col="process" if "process" in bids_df.columns else "lot_id",
            value_col="margin_over_vi_pct",
            title="Buyer Archetype x Processing Method Margin (%)",
        )

    lot_table_cols = [c for c in ["round", "lot_id", "process", "moisture", "moisture_band", "ripeness", "ripeness_tier", "bean_shape", "v_i", "value_tier", "remaining_sacks"] if c in filtered_lots.columns]
    render_entity_table(
        filtered_lots,
        columns=lot_table_cols,
        title="Coffee Lot Physical Quality & Inventory Ledger",
    )

# ==============================================================================
# TAB 4: TELEMETRY & RAW AUDIT LOG
# ==============================================================================
with tab_telemetry:
    filtered_raw = render_dimension_filters(
        raw_df,
        dimensions=[("event_type", "Telemetry Event Type")],
        key_prefix="raw_tab",
    )
    render_entity_table(
        filtered_raw,
        columns=["ts_utc", "round", "event_type", "endpoint", "status_code", "payload"],
        title="Black-Box FlightRecorder & Sniffer Audit Trail",
        max_rows=100,
    )

if auto_refresh:
    time.sleep(5)
    st.rerun()
