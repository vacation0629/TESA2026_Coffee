from __future__ import annotations

from collections import Counter
from html import escape
from textwrap import wrap
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard.components.kpi_card import render_kpi_row
from dashboard.field_catalog import count
from dashboard.matching import Allocation, Match, allocate_sacks, filter_matches, requirement_summary

_COLORS = ("#277363", "#ad713f", "#526e9a", "#866080", "#586c46", "#965451")
_INK = "#243932"


def _short_id(value: str, width: int | None = None) -> str:
    label = value.removeprefix("LOT_").replace("_", " ").title()
    return "<br>".join(map(escape, wrap(label, width))) if width else escape(label)


def _value_text(value: float | None) -> str:
    return "Value unavailable" if value is None else f"{value:,.2f} THB/kg"


def _style_chart(fig: go.Figure, height: int, **kwargs: Any) -> None:
    fig.update_layout(
        template="plotly_white",
        height=height,
        font={"family": "Inter, Source Sans 3, sans-serif", "color": _INK, "size": 12},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel={"bgcolor": "white", "font_color": _INK},
        **kwargs,
    )


def _render_matrix(matches: list[Match], allocations: list[Allocation], buyer_ids: list[str]) -> None:
    lookup = {(match.buyer_id, match.lot_id): match for match in matches}
    lots = {match.lot_id: match for match in matches}
    lot_ids = list(lots)
    assigned = {(row.match.buyer_id, row.match.lot_id): row.sacks for row in allocations}
    states, labels, tooltips = [], [], []
    for buyer_id in buyer_ids:
        buyer_states, buyer_labels, buyer_tooltips = [], [], []
        for lot_id in lot_ids:
            key = (buyer_id, lot_id)
            match = lookup[key]
            amount = assigned.get(key, 0)
            if amount:
                state, label = 3, f"{amount} assigned"
            elif match.eligible:
                state, label = 2, "Match"
            elif match.stock == 0:
                state, label = 0, "Out of stock"
            elif match.mismatches:
                state, label = 0, "Outside spec"
            else:
                state, label = 1, "Check data"
            detail = [
                f"{escape(buyer_id)} · {escape(lot_id)}",
                _value_text(match.value),
                f"{match.passed}/{match.checked} filters met" if match.checked else label,
                *(escape(reason) for reason in (*match.mismatches, *match.missing)),
            ]
            buyer_states.append(state)
            buyer_labels.append(label)
            buyer_tooltips.append("<br>".join(detail))
        states.append(buyer_states)
        labels.append(buyer_labels)
        tooltips.append(buyer_tooltips)

    fig = go.Figure(go.Heatmap(
        x=lot_ids,
        y=buyer_ids,
        z=states,
        text=labels,
        hovertext=tooltips,
        texttemplate="%{text}",
        hovertemplate="%{hovertext}<extra></extra>",
        zmin=0,
        zmax=3,
        xgap=4,
        ygap=5,
        showscale=False,
        colorscale=[
            (0.0, "#efe9e4"), (1 / 6, "#efe9e4"),
            (1 / 6, "#f8e6bb"), (0.5, "#f8e6bb"),
            (0.5, "#e0efe8"), (5 / 6, "#e0efe8"),
            (5 / 6, "#a9d6bf"), (1.0, "#a9d6bf"),
        ],
    ))
    fig.update_xaxes(
        side="top", tickmode="array", tickvals=lot_ids, tickangle=0, fixedrange=True, automargin=True,
        ticktext=[
            f"{_short_id(lot_id)}<br>{_value_text(lots[lot_id].value)}"
            f"<br>{lots[lot_id].stock if lots[lot_id].stock is not None else '—'} sacks"
            for lot_id in lot_ids
        ],
        showgrid=False, zeroline=False,
    )
    fig.update_yaxes(
        tickmode="array", tickvals=buyer_ids, ticktext=[_short_id(b, 15) for b in buyer_ids],
        autorange="reversed", fixedrange=True, automargin=True, showgrid=False, zeroline=False,
    )
    _style_chart(fig, max(185, 75 + len(buyer_ids) * 39), margin={"l": 103, "r": 8, "t": 61, "b": 9})
    st.plotly_chart(fig, use_container_width=True, theme=None, config={"displayModeBar": False}, key="match_matrix")


def _render_allocation(allocations: list[Allocation], buyers: list[dict[str, Any]]) -> None:
    buyer_ids = [buyer["buyer_id"] for buyer in buyers]
    by_lot: dict[str, dict[str, Allocation]] = {}
    filled: Counter[str] = Counter()
    for row in allocations:
        by_lot.setdefault(row.match.lot_id, {})[row.match.buyer_id] = row
        filled[row.match.buyer_id] += row.sacks

    fig = go.Figure()
    for idx, (lot_id, by_buyer) in enumerate(by_lot.items()):
        sacks = [by_buyer[buyer_id].sacks if buyer_id in by_buyer else 0 for buyer_id in buyer_ids]
        value = next(iter(by_buyer.values())).match.value
        fig.add_bar(
            y=buyer_ids, x=sacks, name=_short_id(lot_id), orientation="h",
            marker_color=_COLORS[idx % len(_COLORS)],
            text=[quantity or "" for quantity in sacks], textposition="inside",
            textangle=0, insidetextanchor="middle", textfont={"color": "white", "size": 12},
            hovertemplate=f"{escape(lot_id)} · {_value_text(value)}<br>%{{x}} sacks<extra></extra>",
        )
    unfilled = [(count(buyer.get("demand_sacks")) or 0) - filled[buyer["buyer_id"]] for buyer in buyers]
    if any(unfilled):
        fig.add_bar(
            y=buyer_ids, x=unfilled, name="Unfilled", orientation="h", marker_color="#e7e4dd",
            hovertemplate="%{x} sacks unfilled<extra></extra>",
        )
    if not fig.data:
        st.info("No buyer demand recorded for an allocation.")
        return
    largest_demand = max((count(buyer.get("demand_sacks")) or 0 for buyer in buyers), default=1)
    fig.update_yaxes(
        tickmode="array", tickvals=buyer_ids, ticktext=[_short_id(b, 15) for b in buyer_ids],
        autorange="reversed", fixedrange=True, automargin=True, showgrid=False,
    )
    fig.update_xaxes(
        title="Sacks", title_standoff=6, tickformat="d", dtick=max(1, (largest_demand + 5) // 6),
        fixedrange=True, gridcolor="#e9ebe7", zeroline=False,
    )
    _style_chart(
        fig, max(185, 75 + len(buyer_ids) * 39), barmode="stack", bargap=0.44,
        uniformtext={"minsize": 10, "mode": "hide"},
        margin={"l": 103, "r": 11, "t": 9, "b": 48},
        legend={"orientation": "h", "y": -0.37, "yanchor": "top", "x": 0, "traceorder": "normal", "font": {"size": 11}},
    )
    st.plotly_chart(fig, use_container_width=True, theme=None, config={"displayModeBar": False}, key="match_allocation")


def _match_table(rows: list[dict[str, Any]]) -> None:
    st.dataframe(
        pd.DataFrame(rows),
        column_config={"Value (THB/kg)": st.column_config.NumberColumn(format="%.2f")},
        hide_index=True, use_container_width=True,
    )


def render_quick_match(
    lots: list[dict[str, Any]], buyers: list[dict[str, Any]], quota: int | None, scope: str
) -> None:
    if not lots or not buyers:
        st.info("Quick Match needs a round with inventory and buyer records.")
        return
    buyer_lookup = {buyer["buyer_id"]: buyer for buyer in buyers}
    first = next((buyer["buyer_id"] for buyer in buyers if buyer.get("demand_sacks")), next(iter(buyer_lookup)))
    saved_selection = f"quick_selection_{scope}"
    default = [buyer_id for buyer_id in st.session_state.get(saved_selection, [first]) if buyer_id in buyer_lookup]
    selection, limit_control = st.columns([3, 1])
    with selection:
        buyer_ids = st.multiselect("Buyer IDs", list(buyer_lookup), default=default, key=f"quick_buyers_{scope}")
    st.session_state[saved_selection] = buyer_ids
    if not buyer_ids:
        st.info("Select one or more buyer IDs to see matches.")
        return

    selected = [buyer_lookup[buyer_id] for buyer_id in buyer_ids]
    demand = sum(count(buyer.get("demand_sacks")) or 0 for buyer in selected)
    inventory = sum(count(lot.get("remaining_sacks")) or 0 for lot in lots)
    limit = min(inventory, demand, inventory if quota is None else quota)
    with limit_control:
        if limit > 0:
            limit = st.number_input(
                "Sack limit", min_value=1, max_value=limit, value=limit,
                help=f"Recorded round cap is {quota} sacks." if quota is not None else "Limit for this recommendation.",
                key=f"quick_limit_{scope}_{limit}_{tuple(sorted(buyer_ids))}",
            )
        else:
            st.caption("Allocation limit of 0 sacks")
    if len(selected) == 1:
        st.caption(requirement_summary(selected[0]))
    else:
        with st.expander("Buyer requirements"):
            for buyer in selected:
                st.write(buyer["buyer_id"], requirement_summary(buyer))

    matches = filter_matches(lots, selected)
    candidates = [match for match in matches if match.eligible]
    allocation = allocate_sacks(matches, selected, limit)
    quantity = sum(row.sacks for row in allocation)
    avg_value = (
        sum(row.sacks * row.match.value for row in allocation) / quantity
        if quantity and all(row.match.value is not None for row in allocation) else None
    )
    render_kpi_row([
        {"label": "Eligible lots", "value": len({match.lot_id for match in candidates})},
        {"label": "Suggested sacks / demand", "value": f"{quantity} / {demand}" if demand else f"{quantity} / —"},
        {"label": "Avg. recorded value", "value": _value_text(avg_value) if avg_value is not None else "—",
         "help": "Average THB/kg weighted by the suggested sack counts."},
    ])

    matrix_column, allocation_column = st.columns([1.55, 1])
    with matrix_column:
        st.subheader("Buyer × lot matches")
        _render_matrix(matches, allocation, buyer_ids)
    with allocation_column:
        st.subheader("Suggested allocation")
        _render_allocation(allocation, selected)

    if any(buyer.get("demand_sacks") is None for buyer in selected):
        st.caption("A buyer with unrecorded demand can have eligible lots. Allocation requires a recorded sack count.")
    if allocation:
        st.subheader("Suggested sacks by lot")
        _match_table([
            {"Buyer": row.match.buyer_id, "Lot": row.match.lot_id, "Assign": row.sacks,
             "Value (THB/kg)": row.match.value, "Value source": row.match.value_source or "Unavailable"}
            for row in allocation
        ])
    if candidates:
        st.subheader("Eligible alternatives")
        _match_table([
            {"Buyer": match.buyer_id, "Lot": match.lot_id, "Available": match.stock,
             "Filters met": f"{match.passed}/{match.checked}" if match.checked else "Any",
             "Value (THB/kg)": match.value, "Value source": match.value_source or "Unavailable"}
            for match in candidates
        ])
    else:
        st.info("No lots meet all recorded filters. Hover over the matrix for each reason.")
