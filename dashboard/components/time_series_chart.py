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
