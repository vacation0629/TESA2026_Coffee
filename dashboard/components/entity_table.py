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
