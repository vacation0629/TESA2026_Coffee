from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from operator import eq, ge, le
from typing import Any

import networkx as nx

from dashboard.field_catalog import BUYER_REQUIREMENTS, LOT_FIELDS, count, display_value
from src.config import PIPELINE_CONFIG


def _grade_at_least(actual: str, minimum: str) -> bool | None:
    if actual == minimum:
        return True
    ranks = PIPELINE_CONFIG["spec_matching"]["grade_rank"]
    actual_rank, minimum_rank = ranks.get(actual), ranks.get(minimum)
    if actual_rank is None or minimum_rank is None:
        return None
    return actual_rank >= minimum_rank


# requirement -> lot field, comparison, display operator
_RULES = {
    "min_grade": ("lot_grade", _grade_at_least, "≥"),
    "min_size": ("bean_size", ge, "≥"),
    "max_defect": ("defect_ratio", le, "≤"),
    "min_humidity": ("moisture_pct", ge, "≥"),
    "max_humidity": ("moisture_pct", le, "≤"),
    "required_process": ("process", eq, "="),
    "min_ripeness": ("ripeness", ge, "≥"),
    "shape_requirement": ("bean_shape", eq, "="),
    "max_broken": ("broken_ratio", le, "≤"),
}


def _requirements(buyer: dict[str, Any]) -> list[str]:
    sources = buyer.get("field_sources", {})
    return [key for key in _RULES if key in sources or buyer.get(key) is not None]


def _requirement_label(key: str, value: Any) -> str:
    lot_key, _, symbol = _RULES[key]
    if value is None:
        return f"Invalid {BUYER_REQUIREMENTS[key].label.lower()}"
    return f"{LOT_FIELDS[lot_key].label} {symbol} {display_value(BUYER_REQUIREMENTS[key], value)}"


def requirement_summary(buyer: dict[str, Any]) -> str:
    recorded = _requirements(buyer)
    active = [_requirement_label(key, buyer.get(key)) for key in recorded if buyer.get(key) != "ANY"]
    if active:
        return " · ".join(active)
    return "Any lot with stock" if recorded else "No requirements recorded"


@dataclass(frozen=True)
class Match:
    buyer_id: str
    lot_id: str
    stock: int | None
    value: float | None
    value_source: str | None
    passed: int
    checked: int
    mismatches: tuple[str, ...]
    missing: tuple[str, ...]

    @property
    def eligible(self) -> bool:
        return bool(self.stock) and not self.mismatches and not self.missing


@dataclass(frozen=True)
class Allocation:
    match: Match
    sacks: int


def value_order(value: float | None) -> tuple[bool, float]:
    return value is None, 0.0 if value is None else value


def filter_matches(lots: list[dict[str, Any]], buyers: list[dict[str, Any]]) -> list[Match]:
    """Evaluate each lot against every recorded requirement for each buyer."""
    matches = []
    for buyer in buyers:
        recorded = _requirements(buyer)
        active = [key for key in recorded if buyer.get(key) != "ANY"]
        for lot in lots:
            passed = 0
            mismatches = []
            missing = [] if recorded else ["No buyer requirements recorded"]
            for key in active:
                lot_key, compare, _ = _RULES[key]
                actual, required = lot.get(lot_key), buyer.get(key)
                label = _requirement_label(key, required)
                if required is None:
                    missing.append(label)
                elif actual is None or actual == "ANY":
                    missing.append(f"{LOT_FIELDS[lot_key].label} unavailable")
                else:
                    result = compare(actual, required)
                    if result is None:
                        missing.append(f"Grade order unavailable for {actual} and {required}")
                    elif result:
                        passed += 1
                    else:
                        shown = display_value(LOT_FIELDS[lot_key], actual)
                        mismatches.append(f"{label} required, recorded {shown}")
            stock = count(lot.get("remaining_sacks"))
            if stock is None:
                missing.append("Available sack count unavailable")
            matches.append(Match(
                buyer["buyer_id"], lot["lot_id"], stock, lot.get("lot_evaluated_value"),
                lot.get("valuation_source"), passed, len(active), tuple(mismatches), tuple(missing),
            ))
    return sorted(matches, key=lambda m: (value_order(m.value), m.lot_id, m.buyer_id))


def allocate_sacks(
    matches: list[Match], buyers: list[dict[str, Any]], sack_limit: int
) -> list[Allocation]:
    """Fill the most sacks, then prefer priced stock and minimize its logged unit value."""
    demand = {buyer["buyer_id"]: count(buyer.get("demand_sacks")) or 0 for buyer in buyers}
    eligible = [match for match in matches if match.eligible and demand.get(match.buyer_id, 0) > 0]
    if not eligible or sack_limit <= 0:
        return []

    recorded = {
        match.lot_id: Decimal(str(match.value))
        for match in eligible if match.value is not None
    }
    precision = max((max(0, -value.as_tuple().exponent) for value in recorded.values()), default=0)
    values = {lot_id: int(value.scaleb(precision)) for lot_id, value in recorded.items()}
    # One unknown value ranks after any possible change in the recorded values.
    unknown_weight = max(values.values(), default=0) * sack_limit + 1
    graph = nx.DiGraph()
    graph.add_edge("source", "stock", capacity=sack_limit)
    for buyer_id, sacks in demand.items():
        graph.add_edge(("buyer", buyer_id), "sink", capacity=sacks)
    for match in eligible:
        lot = ("lot", match.lot_id)
        graph.add_edge("stock", lot, capacity=match.stock, weight=values.get(match.lot_id, unknown_weight))
        graph.add_edge(lot, ("buyer", match.buyer_id), capacity=match.stock)

    flow = nx.max_flow_min_cost(graph, "source", "sink")
    allocations = []
    for match in eligible:
        sacks = flow[("lot", match.lot_id)][("buyer", match.buyer_id)]
        if sacks:
            allocations.append(Allocation(match, sacks))
    return allocations
