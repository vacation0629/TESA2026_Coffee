from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from src.config import PIPELINE_CONFIG


@dataclass(frozen=True)
class Field:
    key: str
    label: str
    kind: str = "text"
    aliases: tuple[str, ...] = ()
    unit: str = ""


_LOT = PIPELINE_CONFIG["schema_map"]["lot"]
_BUYER = PIPELINE_CONFIG["schema_map"]["buyer"]

LOT_GROUPS = {
    "Bean / Identity": (
        Field("variety_clone", "Variety or clone"),
        Field("is_authentic_species", "Species verified", "bool"),
    ),
    "Bean / Physical": (
        Field("moisture_pct", "Moisture", "percent", tuple(_LOT["moisture"]), "%"),
        Field("bean_size", "Bean size", "number", tuple(k for k in _LOT["bean_size"] if k != "screen_size"), "mm"),
        Field("screen_size", "Screen size", "number"),
        Field("water_activity", "Water activity", "fraction"),
        Field("bulk_density_g_l", "Bulk density", "number", unit="g/L"),
        Field("size_retention_std", "Size retention", "percent", unit="%"),
        Field("green_color_lab", "Green color (L*, a*, b*)", "lab"),
        Field("shape_peaberry_pct", "Peaberry", "percent", unit="%"),
        Field("bean_shape", "Bean shape", "shape", tuple(_LOT["bean_shape"])),
    ),
    "Bean / Defects": (
        Field("defect_ratio", "Defects", "ratio", tuple(_LOT["defect_ratio"]), "%"),
        Field("broken_ratio", "Broken beans", "ratio", tuple(k for k in _LOT["broken_ratio"] if k != "defect_ratio"), "%"),
        Field("primary_defects", "Primary defects", "count"),
        Field("secondary_defects", "Secondary defects", "count"),
        Field("defect_mass_pct", "Defect mass", "percent", unit="%"),
    ),
    "Bean / Chemistry": (
        Field("sucrose_to_cga_ratio", "Sucrose to CGA ratio", "number"),
    ),
    "Processing": (
        Field("process", "Process", "process", tuple(_LOT["process"])),
        Field("fermentation_ph", "Fermentation pH", "number"),
    ),
    "Processing / Harvest": (
        Field("ripeness", "Cherry ripeness", "ripeness", ("ripeness", "ripeness_pct", "ripe_ratio"), "%"),
    ),
    "Storage": (
        Field("storage_age_months", "Storage age", "count", unit="months"),
        Field("is_hermetic", "Hermetic storage", "bool"),
    ),
    "Quality assessment": (
        Field("lot_grade", "Lot grade", "grade", tuple(_LOT["lot_grade"])),
        Field("clean_odor_flag", "Clean odor", "bool"),
        Field("quaker_count_100g", "Quakers after sample roast", "count", unit="per 100 g"),
        Field("cupping_score", "Cupping score", "number"),
    ),
    "Inventory": (
        Field("lot_id", "Lot ID", aliases=tuple(_LOT["lot_id"])),
        Field("remaining_sacks", "Available sacks", "count", tuple(_LOT["sacks"])),
    ),
    "Valuation": (
        Field("lot_evaluated_value", "Evaluated value", "number", ("lot_evaluated_value", *_LOT["v_i"]), "THB/kg"),
    ),
}

BUYER_GROUPS = {
    "Requirements": (
        Field("min_grade", "Minimum grade", "grade", tuple(_BUYER["min_grade"])),
        Field("min_size", "Minimum bean size", "number", tuple(_BUYER["min_size"]), "mm"),
        Field("max_defect", "Maximum defects", "ratio", ("max_defect", "defect_max", "max_defect_pct"), "%"),
        Field("min_humidity", "Minimum moisture", "percent", ("min_humidity", "min_moisture", "humidity_min", "moisture_min"), "%"),
        Field("max_humidity", "Maximum moisture", "percent", tuple(_BUYER["max_moisture"]), "%"),
        Field("required_process", "Required process", "process", tuple(_BUYER["required_process"])),
        Field("min_ripeness", "Minimum cherry ripeness", "ripeness", tuple(_BUYER["min_ripeness"]), "%"),
        Field("shape_requirement", "Required bean shape", "shape", ("shape_requirement", *_BUYER["bean_shape_req"])),
        Field("max_broken", "Maximum broken beans", "ratio", ("max_broken", "broken_max", "max_broken_pct"), "%"),
    ),
    "Demand": (
        Field("buyer_id", "Buyer ID", aliases=tuple(_BUYER["buyer_id"])),
        Field("demand_sacks", "Demand", "count", tuple(_BUYER["demand_sacks"]), "sacks"),
        Field("target_value", "Disclosed target value", "number", ("target_value",), "THB/kg"),
    ),
}

BUYER_REQUIREMENTS = {field.key: field for field in BUYER_GROUPS["Requirements"]}
LOT_FIELDS = {field.key: field for fields in LOT_GROUPS.values() for field in fields}
_UNRESTRICTED = {"ANY", "ALL", "NONE"}
_PROCESSES = {"WET": "WASHED", "WASH": "WASHED", "WASHED": "WASHED", "DRY": "DRY", "NATURAL": "DRY"}
_SHAPES = {"WHOLE": "WHOLE", "WHOLE_ONLY": "WHOLE", "BROKEN": "BROKEN", "BROKEN_ONLY": "BROKEN"}


def number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return numeric if isfinite(numeric) else None


def count(value: Any) -> int | None:
    numeric = number(value)
    return int(numeric) if numeric is not None and numeric >= 0 and numeric.is_integer() else None


def _decode(field: Field, value: Any, alias: str) -> Any:
    kind = field.kind
    if kind == "bool":
        return value if isinstance(value, bool) else None
    if kind == "lab":
        if isinstance(value, (list, tuple)) and len(value) == 3:
            lab = tuple(number(component) for component in value)
            return lab if None not in lab else None
        return None
    if kind == "count":
        return count(value)
    if kind in {"text", "grade", "process", "shape"}:
        if not isinstance(value, (str, int)) or isinstance(value, bool):
            return None
        text = str(value).strip()
        if kind == "text" or not text:
            return text or None
        text = text.upper().replace(" ", "_")
        if text in _UNRESTRICTED:
            return "ANY"
        if kind == "process":
            return _PROCESSES.get(text, text)
        if kind == "shape":
            return _SHAPES.get(text)
        return text

    literal_percent = isinstance(value, str) and value.strip().endswith("%")
    numeric = number(value.strip()[:-1] if literal_percent else value)
    if numeric is None or numeric < 0:
        return None
    if kind == "ratio":
        numeric = numeric / 100 if literal_percent or alias.endswith("_pct") or numeric > 1 else numeric
    if kind == "ripeness" and not literal_percent and (alias == "ripe_ratio" or (not alias.endswith("_pct") and numeric <= 1)):
        numeric *= 100
    if kind in {"ratio", "fraction"} and numeric > 1:
        return None
    if kind in {"percent", "ripeness"} and numeric > 100:
        return None
    return numeric


def read_record(raw: dict[str, Any], groups: dict[str, tuple[Field, ...]]) -> dict[str, Any]:
    """Keep the source key of each observation. Missing data never gets a default."""
    record: dict[str, Any] = {}
    sources: dict[str, str] = {}
    for fields in groups.values():
        for field in fields:
            record[field.key] = None
            for alias in dict.fromkeys((field.key, *field.aliases)):
                value = raw.get(alias)
                if value is not None and not (isinstance(value, str) and not value.strip()):
                    unrestricted = field.key in BUYER_REQUIREMENTS and isinstance(value, str) and value.strip().upper() in _UNRESTRICTED
                    record[field.key] = "ANY" if unrestricted else _decode(field, value, alias)
                    sources[field.key] = alias
                    break
    record["field_sources"] = sources
    return record


def display_value(field: Field, value: Any) -> str:
    if value is None:
        return "Unavailable"
    if value == "ANY":
        return "Any"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, tuple):
        return ", ".join(f"{item:g}" for item in value)
    if field.kind == "ratio":
        value *= 100
    text = f"{value:g}" if isinstance(value, (int, float)) else str(value)
    if field.unit == "%":
        return f"{text}%"
    return f"{text} {field.unit}".strip()
