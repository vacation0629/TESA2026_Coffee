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
