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
