# \[v2.5.0 — Part 5 of 5\] Recyclable Local Telemetry & Market Analytics Dashboard Blueprint

**Project:** TESA Top Gun Rally 2026 — End-to-End Coffee Quality & Autonomous Market Agent  
**Version:** `v2.5.0` (Self-Contained Modular Suite — Part 5 of 5\)  
**Modular Suite Structure (`v2`):**

* **Part 1 (`v2_part1_upstream_coffee_science.md`):** Upstream Agronomy, Varietal Genetics, Harvesting, Metagenomic Fermentation, Solar/OTA Drying & Post-Hulling Storage Safety.  
* **Part 2 (`v2_part2_grading_cv_chemistry_roasting.md`):** Downstream CQI/TAS 5700 Grading Gatekeepers, Hardware/CV Morphometrics, Active Thermography, NIR/FTIR Spectroscopy, Roasting Chemistry, Carbon Footprint, Circular Bioeconomy & 18-Feature Python Schema.  
* **Part 3 (`v2_part3_competition_agent_and_pricing_engine.md`):** Track 3 Competition Rules, Pluggable Feature-to-Valuation Framework, 25 Market/API Variables, 5 Statistical Market-Stage Indicators (`CPR`, `Slope`, `CV`, `DIR`, `IUR`), Hybrid Quantitative-First \+ Qwen 9B Pricing Engine, Optional XGBoost & Risk Matrix.  
* **Part 4 (`v2_part4_local_ai_implementation_blueprint.md`):** Production-Ready 13-File Python Codebase (`config.py`, `logger.py`, `adapters.py`, `stats_engine.py`, `xgb_plugin.py`, `predictors.py`, `guardrails.py`, `agent_loop.py`), `auto_sniffer.py`, CI/CD Workflow & End-to-End Tests.  
* **Part 5 (`v2_part5_telemetry_dashboard_blueprint.md`):** Local Recyclable Analytics Dashboard (`dashboard/app.py`, `data_loader.py`, and 5 Polymorphic UI Components) for Multi-Customer & Multi-Grade Market Monitoring.  
  **Date:** 2026-11-16  
  **Target Audience:** Local AI Coding Assistant (Claude Code / Cursor / GitHub Copilot) & Team Developers

---

## Current dashboard and Quick Match

Run the dashboard from the repository root.

```powershell
python -m pip install -r dashboard/requirements-dashboard.txt
python -m streamlit run dashboard/app.py
```

Quick Match opens on the latest recorded board. Select one or more buyer IDs and a sack limit. The buyer-by-lot matrix puts the lowest recorded THB/kg values first and shows which lots meet the filters, which were assigned, and why other lots were excluded. Coffee Lots groups recorded fields under Bean, Processing, Storage, Quality Assessment, Inventory, and Valuation.

Matching uses all recorded requirements, including buyer moisture bounds and lot process, grade, size, shape, ripeness, and defect limits when supplied. The allocation maximizes filled sacks within the selected limit, recorded round cap, stock, and buyer demand. Among equally complete allocations, it prefers recorded values, then minimizes their sack-weighted cost basis. Each sack can be assigned once.

**Future pricing expansion.** Add the official valuation formula and any buyer price criteria when their fields and coefficients are confirmed. Recorded lot values currently provide the THB/kg ranking. A per-sack total requires a recorded sack weight.

---

## 0\. Local AI Execution Directive & System Overview

**Instructions for Local AI Coding Assistant:**  
Use the dashboard implementation described above for current work. Sections 2–6 preserve the original v2.5.0 blueprint.

* **Strict Polymorphism (Recyclable Components):** Never hardcode fixed customer names (e.g., `"B1".."B6"`) or fixed coffee grade labels (e.g., `"A"`, `"B"`, `"C"`, `"FINE_ROBUSTA"`). Every chart, KPI card row, filter bar, and table must accept dynamic grouping columns (`group_col: str`) and metric definitions (`metric_col: str`) discovered at runtime from the loaded telemetry logs.  
* **Zero Coupling to Live Trading Loop:** The dashboard reads exclusively from disk (`logs/<match_id>/raw_events.jsonl`, `logs/<match_id>/state_snapshot.json`, and `logs/phase1_*.jsonl`) and never makes live `POST` calls to the market server.  
* **Isolated Dependencies:** Keep `streamlit`, `plotly`, and `pandas` inside `dashboard/requirements-dashboard.txt` so the headless GitHub Actions trading runner (`requirements.txt`) stays minimal.

---

## 1\. Scope Definition, Prerequisites & Phased Roadmap

### 1.1 Scope & Prerequisites

* **Core Objective:** Provide a local, real-time analytics dashboard displaying basic KPI statistics, interactive time-series and cohort breakdown charts, and raw event logs across **multiple customer archetypes** (`buyer_id`) and **multiple coffee grades/attributes** (`lot_grade`, `process`, `humidity` `9–11%` band, `bean_size`, `defect_ratio`) using **5 recyclable UI components**.  
* **Explicit Non-Goals:** Do not deploy the dashboard inside GitHub Actions CI/CD; do not duplicate schema mapping logic (reuse `PIPELINE_CONFIG["schema_map"]` from `src/config.py`).  
* **Prerequisites:** Python 3.10+, existing `src/` modules from `v2` Part 4 (`src/config.py`, `src/adapters.py`), and `pip install -r dashboard/requirements-dashboard.txt`.

### 1.2 Phased Implementation Milestones (`D1–D4`)

| Phase ID | Phase Name | Key Actions | Deliverables | Blocking Dependency |
| :---- | :---- | :---- | :---- | :---- |
| `D1` | Log Ingestion & Normalized DataFrames | Parse `raw_events.jsonl`, `state_snapshot.json`, and `phase1_*.jsonl` into `rounds_df`, `buyers_df`, `lots_df`, `bids_df` with partial-line JSON guards | `dashboard/data_loader.py` | `src/config.py` (`v2` Part 4\) |
| `D2` | Recyclable UI Component Library | Build 5 entity-agnostic UI primitives (`MetricKPICard`, `EntityDimensionSelector`, `RecyclableTimeSeriesChart`, `RecyclableBreakdownChart`, `RecyclableEntityTable`) | `dashboard/components/*.py` | Phase `D1` |
| `D3` | Multi-View Dashboard Orchestrator | Compose 4 tabs (*Executive Command*, *Customer Intelligence*, *Coffee Grade & Quality*, *Model & Telemetry*) by recycling the 5 primitives | `dashboard/app.py` | Phase `D2` |
| `D4` | Offline Verification & Camp Replay | Test zero-crash rendering on empty logs (`Round 0`), Phase 1 `mitmdump` captures, and multi-grade/multi-buyer mock matches | `tests/test_dashboard_loader.py` | Phase `D3` |

---

## 2\. Repository Extension Layout & Dependencies

```
tesa2026-track3-agent/
├── src/                                  # Existing v2 Part 4 core trading engine
├── logs/                                 # Telemetry source (raw_events.jsonl, state_snapshot.json, phase1_*.jsonl)
├── dashboard/
│   ├── requirements-dashboard.txt        # Local UI dependencies (streamlit, plotly, pandas)
│   ├── data_loader.py                    # Schema-agnostic JSONL/JSON parser -> normalized DataFrames
│   ├── app.py                            # Main Streamlit multi-tab orchestrator recycling components
│   └── components/
│       ├── __init__.py
│       ├── kpi_card.py                   # Recyclable Component 1: MetricKPICard row renderer
│       ├── filter_bar.py                 # Recyclable Component 2: EntityDimensionSelector dynamic filters
│       ├── time_series_chart.py          # Recyclable Component 3: RecyclableTimeSeriesChart (Plotly)
│       ├── breakdown_chart.py            # Recyclable Component 4: RecyclableBreakdownChart & Heatmap
│       └── entity_table.py               # Recyclable Component 5: RecyclableEntityTable with badges
└── tests/
    └── test_dashboard_loader.py          # Offline DataFrame & component schema verification tests
```

### 2.1 `dashboard/requirements-dashboard.txt`

```
streamlit>=1.32.0
plotly>=5.20.0
pandas>=2.2.0
```

---

## 3\. Schema-Agnostic Telemetry Loader (`dashboard/data_loader.py`)

`LogDataLoader` ingests both autonomous agent logs (`logs/<match_id>/raw_events.jsonl`) and Phase 1 `mitmdump` browser captures (`logs/phase1_*.jsonl`), normalizing arbitrary customer and coffee grade fields through `DynamicSchemaAdapter` from `src/adapters.py`.

```py
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
    if not root.exists():
        return ["default"]
    items = [p.name for p in sorted(root.iterdir()) if p.is_dir()]
    phase1_files = [p.name for p in sorted(root.glob("phase1_*.jsonl"))]
    return items + phase1_files if (items or phase1_files) else ["default"]


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
                "bids_submitted": len(payload.get("bids", [])),
                "sacks_offered": sum(int(b.get("sacks", 0)) for b in payload.get("bids", [])),
            })

            settle = settlement_by_round.get(r_num, {})
            clear_map = settle.get("clearing_prices", {})
            won_map = settle.get("won_by_buyer", {})
            for b in payload.get("bids", []):
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
```

---

## 4\. Five Recyclable UI Components (`dashboard/components/*.py`)

Every component below is stateless and polymorphic: pass any `DataFrame`, any grouping column (`"buyer_id"`, `"lot_grade"`, `"process"`, `"humidity_band"`, `"market_stage"`), and any numeric metric column (`"price_per_kg"`, `"margin_over_vi_pct"`, `"demand_sacks"`, `"sacks"`).

### 4.1 Component 1: `MetricKPICard` (`dashboard/components/kpi_card.py`)

```py
from __future__ import annotations
from typing import Any
import streamlit as st


def render_kpi_row(kpis: list[dict[str, Any]], columns_per_row: int = 4) -> None:
    """Recyclable KPI stat card grid used across global, customer, and coffee-grade views."""
    if not kpis:
        return
    for start in range(0, len(kpis), columns_per_row):
        batch = kpis[start : start + columns_per_row]
        cols = st.columns(len(batch))
        for col, item in zip(cols, batch):
            with col:
                st.metric(
                    label=str(item.get("label", "")),
                    value=str(item.get("value", "—")),
                    delta=item.get("delta"),
                    delta_color=item.get("delta_color", "normal"),
                    help=item.get("help"),
                )
```

### 4.2 Component 2: `EntityDimensionSelector` (`dashboard/components/filter_bar.py`)

```py
from __future__ import annotations
import pandas as pd
import streamlit as st


def render_dimension_filters(
    df: pd.DataFrame,
    dimensions: list[tuple[str, str]],
    key_prefix: str = "global",
) -> pd.DataFrame:
    """Dynamically discovers unique customer/grade/process values and filters df without hardcoding."""
    if df.empty:
        return df

    filtered = df.copy()
    active_dims = [(col, label) for col, label in dimensions if col in filtered.columns]
    if not active_dims:
        return filtered

    cols = st.columns(len(active_dims))
    for ui_col, (col_name, label) in zip(cols, active_dims):
        unique_vals = sorted(filtered[col_name].dropna().astype(str).unique().tolist())
        with ui_col:
            selected = st.multiselect(
                label=label,
                options=unique_vals,
                default=unique_vals,
                key=f"{key_prefix}_{col_name}",
            )
            if selected:
                filtered = filtered[filtered[col_name].astype(str).isin(selected)]
    return filtered
```

### 4.3 Component 3: `RecyclableTimeSeriesChart` (`dashboard/components/time_series_chart.py`)

```py
from __future__ import annotations
from typing import Any
import pandas as pd
import plotly.express as px
import streamlit as st


def render_trend_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_by: str | None = None,
    title: str = "",
    y_label: str = "",
    reference_lines: list[dict[str, Any]] | None = None,
    markers: bool = True,
) -> None:
    """Recyclable multi-series line chart for customer clearing trends, grade margins, and market stats."""
    if df.empty or x_col not in df.columns or y_col not in df.columns:
        st.info(f"Waiting for telemetry data to render: {title}")
        return

    plot_df = df.dropna(subset=[x_col, y_col]).sort_values(by=x_col)
    if plot_df.empty:
        st.info(f"No non-null observations yet for: {title}")
        return

    fig = px.line(
        plot_df,
        x=x_col,
        y=y_col,
        color=color_by if (color_by and color_by in plot_df.columns) else None,
        markers=markers,
        title=title,
        labels={x_col: "Round", y_col: y_label or y_col},
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    if reference_lines:
        for ref in reference_lines:
            fig.add_hline(
                y=float(ref["y"]),
                line_dash=ref.get("dash", "dash"),
                line_color=ref.get("color", "#EF553B"),
                annotation_text=ref.get("label", ""),
            )
    fig.update_layout(height=360, margin=dict(l=20, r=20, t=45, b=20), legend_title_text=color_by or "")
    st.plotly_chart(fig, use_container_width=True)
```

### 4.4 Component 4: `RecyclableBreakdownChart` (`dashboard/components/breakdown_chart.py`)

```py
from __future__ import annotations
import pandas as pd
import plotly.express as px
import streamlit as st


def render_cohort_breakdown(
    df: pd.DataFrame,
    group_col: str,
    metric_col: str,
    agg_fn: str = "mean",
    color_col: str | None = None,
    chart_type: str = "bar",
    title: str = "",
) -> None:
    """Recyclable grouped-bar or box distribution component across customer or coffee-grade cohorts."""
    if df.empty or group_col not in df.columns or metric_col not in df.columns:
        st.info(f"No cohort records available for: {title}")
        return

    clean_df = df.dropna(subset=[group_col, metric_col])
    if clean_df.empty:
        st.info(f"Insufficient values for: {title}")
        return

    if chart_type == "box":
        fig = px.box(
            clean_df,
            x=group_col,
            y=metric_col,
            color=color_col if (color_col and color_col in clean_df.columns) else group_col,
            title=title,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
    else:
        group_keys = [group_col] + ([color_col] if (color_col and color_col in clean_df.columns and color_col != group_col) else [])
        agg_df = clean_df.groupby(group_keys, as_index=False)[metric_col].agg(agg_fn)
        fig = px.bar(
            agg_df,
            x=group_col,
            y=metric_col,
            color=color_col if (color_col and color_col in agg_df.columns) else group_col,
            barmode="group",
            title=title,
            text_auto=".2f",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )

    fig.update_layout(height=350, margin=dict(l=20, r=20, t=45, b=20))
    st.plotly_chart(fig, use_container_width=True)


def render_compatibility_heatmap(
    df: pd.DataFrame,
    row_col: str = "buyer_id",
    col_col: str = "lot_grade",
    value_col: str = "margin_over_vi_pct",
    title: str = "Customer x Coffee Grade Performance Matrix",
) -> None:
    """2D recyclable pivot heatmap showing margin or win rate across any two entity dimensions."""
    if df.empty or not {row_col, col_col, value_col}.issubset(df.columns):
        st.info(f"Waiting for cross-dimension pairs: {title}")
        return

    pivot = df.pivot_table(index=row_col, columns=col_col, values=value_col, aggfunc="mean")
    if pivot.empty:
        return
    fig = px.imshow(
        pivot,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="RdYlGn",
        title=title,
        labels=dict(x=col_col, y=row_col, color=value_col),
    )
    fig.update_layout(height=340, margin=dict(l=20, r=20, t=45, b=20))
    st.plotly_chart(fig, use_container_width=True)
```

### 4.5 Component 5: `RecyclableEntityTable` (`dashboard/components/entity_table.py`)

```py
from __future__ import annotations
import pandas as pd
import streamlit as st


def render_entity_table(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    title: str = "",
    max_rows: int = 200,
) -> None:
    """Recyclable data table with column projection and row cap for fast live refresh."""
    if title:
        st.subheader(title)
    if df.empty:
        st.caption("No records logged yet.")
        return

    view_df = df[[c for c in columns if c in df.columns]] if columns else df
    st.dataframe(view_df.tail(max_rows), use_container_width=True, hide_index=True)
```

---

## 5\. Multi-View Dashboard Orchestrator (`dashboard/app.py`)

```py
from __future__ import annotations
import time
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
    "2. Customer Intelligence (Multi-Buyer)",
    "3. Coffee Grade & Quality (Multi-Grade)",
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

    render_entity_table(
        bids_df,
        columns=["round", "buyer_id", "lot_id", "lot_grade", "process", "sacks", "v_i", "price_per_kg", "margin_over_vi_pct", "clearing_price", "won"],
        title="Round-by-Round Bid Execution & Settlement Ledger",
    )

# ==============================================================================
# TAB 2: CUSTOMER INTELLIGENCE (RECYCLED ACROSS ALL BUYER BOT ARCHETYPES)
# ==============================================================================
with tab_customers:
    filtered_buyers = render_dimension_filters(
        buyers_df,
        dimensions=[("buyer_id", "Customer / Buyer Bot"), ("min_grade", "Min Grade Spec"), ("required_process", "Process Spec")],
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

    render_entity_table(
        filtered_buyers,
        columns=["round", "buyer_id", "min_grade", "max_defect", "required_process", "demand_sacks", "clearing_price", "our_won"],
        title="Customer Specification & Clearing History",
    )

# ==============================================================================
# TAB 3: COFFEE GRADE & QUALITY (RECYCLED ACROSS ALL GRADES, PROCESSES & HUMIDITY)
# ==============================================================================
with tab_grades:
    filtered_lots = render_dimension_filters(
        lots_df,
        dimensions=[("lot_grade", "Coffee Grade"), ("process", "Processing Method"), ("humidity_band", "Humidity Band (9-11%)")],
        key_prefix="grade_tab",
    )

    num_grades = int(filtered_lots["lot_grade"].nunique()) if not filtered_lots.empty else 0
    avg_size = float(filtered_lots["bean_size"].mean()) if not filtered_lots.empty else 0.0
    avg_defect = float(filtered_lots["defect_ratio"].mean() * 100.0) if not filtered_lots.empty else 0.0
    in_band_pct = float((filtered_lots["humidity_band"] == "IN_BAND_9_11").mean() * 100.0) if not filtered_lots.empty else 0.0

    render_kpi_row([
        {"label": "Distinct Coffee Grades", "value": f"{num_grades} grades"},
        {"label": "Mean Bean Size", "value": f"{avg_size:.2f} mm"},
        {"label": "Mean Defect Ratio", "value": f"{avg_defect:.2f}%"},
        {"label": "Humidity 9-11% Compliance", "value": f"{in_band_pct:.1f}%"},
    ])

    g1, g2 = st.columns(2)
    with g1:
        render_cohort_breakdown(
            bids_df,
            group_col="lot_grade",
            metric_col="margin_over_vi_pct",
            agg_fn="mean",
            color_col="process",
            chart_type="bar",
            title="Realized Margin (%) by Coffee Grade & Process (Washed vs Dry)",
        )
    with g2:
        render_compatibility_heatmap(
            bids_df,
            row_col="buyer_id",
            col_col="lot_grade",
            value_col="margin_over_vi_pct",
            title="Recycled Matrix: Buyer Archetype x Coffee Grade Avg Margin (%)",
        )

    render_entity_table(
        filtered_lots,
        columns=["round", "lot_id", "lot_grade", "process", "humidity", "humidity_band", "bean_size", "defect_ratio", "remaining_sacks"],
        title="Coffee Lot Quality & Inventory Ledger",
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
```

---

## 6\. Offline Verification Suite (`tests/test_dashboard_loader.py`)

```py
from __future__ import annotations
import copy
import shutil
import unittest
from pathlib import Path
from dashboard.data_loader import load_dashboard_frames
from src.agent_loop import MarketAgentOrchestrator
from src.config import PIPELINE_CONFIG


class TestDashboardDataLoader(unittest.TestCase):
    def setUp(self) -> None:
        self.match_id = "dashboard_test_match"
        log_dir = Path("logs") / self.match_id
        if log_dir.exists():
            shutil.rmtree(log_dir)
        cfg = copy.deepcopy(PIPELINE_CONFIG)
        cfg["api"]["dry_run"] = True

        agent = MarketAgentOrchestrator(config=cfg, match_id=self.match_id)
        decision = agent.run_round({
            "round": 1,
            "total_rounds": 15,
            "num_teams": 40,
            "lots": [
                {"id": "L1", "grade": "A", "bean_mm": 6.8, "defect_pct": 2.0, "humidity": 10.2, "process": "washed", "sacks": 12},
                {"id": "L2", "grade": "C", "bean_mm": 5.8, "defect_pct": 11.0, "humidity": 12.5, "process": "dry", "sacks": 12},
            ],
            "buyers": [
                {"bot_id": "B_SPECIALTY", "min_grade": "A", "required_process": "washed", "demand": 8},
                {"bot_id": "B_FACTORY", "min_grade": "C", "demand": 15},
            ],
        })
        agent.record_settlement(
            round_num=1,
            settlement_payload={
                "clearing_prices": {"B_SPECIALTY": 142.0, "B_FACTORY": 118.0},
                "buyer_min_spec_vals": {"B_SPECIALTY": 132.0, "B_FACTORY": 108.0},
                "won_by_buyer": {"B_SPECIALTY": True, "B_FACTORY": True},
            },
            stats=decision["stats"],
        )

    def test_polymorphic_frames_populated(self) -> None:
        frames = load_dashboard_frames(self.match_id, log_root="logs")
        self.assertEqual(len(frames["rounds_df"]), 1)
        self.assertEqual(set(frames["lots_df"]["lot_grade"]), {"A", "C"})
        self.assertEqual(set(frames["buyers_df"]["buyer_id"]), {"B_SPECIALTY", "B_FACTORY"})
        self.assertIn("margin_over_vi_pct", frames["bids_df"].columns)
        self.assertIn("humidity_band", frames["bids_df"].columns)


if __name__ == "__main__":
    unittest.main()
```

---

## 7\. Risk & Edge-Case Matrix

| Risk / Edge Case | Impact if Unhandled | Concrete Mitigation & Fallback Protocol |
| :---- | :---- | :---- |
| Concurrent read while `FlightRecorder` appends a line | `json.JSONDecodeError` crashes dashboard reload | `_read_jsonl_safe()` wraps every line parse in `try...except json.JSONDecodeError` and skips incomplete tail lines cleanly. |
| Empty log directory before Round 1 starts | `KeyError` or blank crash on startup | Every DataFrame loader returns structured empty DataFrames and every component renders an informative `st.info(...)` placeholder. |
| Practice rounds (`4` grades) vs. Final match (`6` grades) | Hardcoded tabs or selectors hide new grades/customers | `EntityDimensionSelector` dynamically queries `df[col].unique()` on every render so any number of grades or buyers appears automatically. |
| Dashboard libraries bloat CI/CD runner install time | Slows down 5-minute automated GitHub Actions bids | `streamlit`, `plotly`, and `pandas` live exclusively in `dashboard/requirements-dashboard.txt`, never in root `requirements.txt`. |

---

## 8\. Verification Criteria Before Camp Rounds

1. Run `python -m unittest discover -s tests -p "test_*.py"` and confirm both `test_pipeline_e2e.py` and `test_dashboard_loader.py` pass with zero errors.  
2. Run `streamlit run dashboard/app.py`, select `dashboard_test_match`, and verify that all 4 tabs render KPI cards, trend lines, cohort bar charts, and the Buyer × Grade heatmap without hardcoded buyer or grade strings.  
3. Confirm `requirements.txt` at repository root remains untouched (`requests>=2.31.0` only) so CI/CD build speed is unaffected.