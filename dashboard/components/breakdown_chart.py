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
