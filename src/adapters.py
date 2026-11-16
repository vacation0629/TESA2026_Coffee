from __future__ import annotations
from typing import Any


def _extract_key(raw: dict[str, Any], candidates: list[str], default: Any) -> tuple[Any, str | None]:
    for key in candidates:
        if key in raw and raw[key] is not None:
            return raw[key], key
    return default, None


class DynamicSchemaAdapter:
    """Stage 1: Maps arbitrary organizer JSON payloads into canonical dicts without KeyErrors."""

    def __init__(self, schema_map: dict[str, Any]) -> None:
        self.schema_map = schema_map

    def normalize_lots(self, raw_lots: list[dict[str, Any]]) -> list[dict[str, Any]]:
        lot_map = self.schema_map["lot"]
        canonical: list[dict[str, Any]] = []
        for idx, raw in enumerate(raw_lots):
            used_keys: set[str] = set()
            lot_id, k = _extract_key(raw, lot_map["lot_id"], f"lot_{idx+1}")
            if k: used_keys.add(k)
            lot_grade, k = _extract_key(raw, lot_map["lot_grade"], "B")
            if k: used_keys.add(k)
            bean_size, k = _extract_key(raw, lot_map["bean_size"], 6.35)
            if k: used_keys.add(k)
            defect_ratio, k = _extract_key(raw, lot_map["defect_ratio"], 0.05)
            if k: used_keys.add(k)
            sacks, k = _extract_key(raw, lot_map["sacks"], 0)
            if k: used_keys.add(k)

            # Auto-normalize defect percentage (e.g., 5.0 -> 0.05) if > 1.0
            defect_val = float(defect_ratio)
            if defect_val > 1.0:
                defect_val = defect_val / 100.0

            extra = {ek: ev for ek, ev in raw.items() if ek not in used_keys}
            canonical.append({
                "lot_id": str(lot_id),
                "lot_grade": str(lot_grade),
                "bean_size": float(bean_size),
                "defect_ratio": defect_val,
                "remaining_sacks": int(sacks),
                "extra_features": extra,
            })
        return canonical

    def normalize_buyers(self, raw_buyers: list[dict[str, Any]]) -> list[dict[str, Any]]:
        buyer_map = self.schema_map["buyer"]
        canonical: list[dict[str, Any]] = []
        for idx, raw in enumerate(raw_buyers):
            buyer_id, _ = _extract_key(raw, buyer_map["buyer_id"], f"buyer_{idx+1}")
            min_grade, _ = _extract_key(raw, buyer_map["min_grade"], None)
            max_defect, _ = _extract_key(raw, buyer_map["max_defect"], None)
            min_size, _ = _extract_key(raw, buyer_map["min_size"], None)
            demand_sacks, _ = _extract_key(raw, buyer_map["demand_sacks"], 0)

            max_def_val = float(max_defect) if max_defect is not None else None
            if max_def_val is not None and max_def_val > 1.0:
                max_def_val = max_def_val / 100.0

            canonical.append({
                "buyer_id": str(buyer_id),
                "min_grade": str(min_grade) if min_grade is not None else None,
                "max_defect": max_def_val,
                "min_size": float(min_size) if min_size is not None else None,
                "demand_sacks": int(demand_sacks),
            })
        return canonical


class FlexibleValuationEngine:
    """Stage 2: Hot-swappable valuation engine supporting 3 formula templates around V_base."""

    def __init__(self, val_cfg: dict[str, Any], v_base: float = 120.0) -> None:
        self.val_cfg = val_cfg
        self.v_base = float(v_base)

    def _transform_feature(self, feat_name: str, raw_val: Any) -> float:
        t_cfg = self.val_cfg.get("transforms", {}).get(feat_name, {"type": "raw"})
        t_type = t_cfg.get("type", "raw")
        if t_type == "lookup_map":
            return float(t_cfg.get("map", {}).get(str(raw_val), t_cfg.get("default", 0.0)))
        if t_type == "reference_delta":
            ref = float(t_cfg.get("ref", 0.0))
            scale = float(t_cfg.get("scale", 1.0)) or 1.0
            return (float(raw_val) - ref) / scale
        return float(raw_val)

    def evaluate_lot(self, lot: dict[str, Any]) -> float:
        mode = self.val_cfg.get("mode", "LINEAR_WEIGHTED")
        if mode == "CUSTOM_LAMBDA":
            custom_fn = self.val_cfg["custom_fn"]
            return round(float(custom_fn(lot, self.v_base)), 4)

        weights: dict[str, float] = self.val_cfg.get("weights", {})
        weighted_sum = 0.0
        for feat_name, w in weights.items():
            if w == 0.0:
                continue
            if feat_name in lot:
                val = lot[feat_name]
            elif feat_name in lot.get("extra_features", {}):
                val = lot["extra_features"][feat_name]
            else:
                continue
            weighted_sum += float(w) * self._transform_feature(feat_name, val)

        if mode == "ADDITIVE_POINTS":
            return round(self.v_base + weighted_sum, 4)
        return round(self.v_base * (1.0 + weighted_sum), 4)

    def evaluate_all(self, lots: list[dict[str, Any]]) -> dict[str, float]:
        return {lot["lot_id"]: self.evaluate_lot(lot) for lot in lots}


class SpecAndQuotaMatcher:
    """Stage 4: Filters valid (lot, buyer) pairs and sorts by ascending V_i (Minimum-Spec Arbitrage)."""

    def __init__(self, grade_rank: dict[str, int]) -> None:
        self.grade_rank = grade_rank

    def _grade_ok(self, lot_grade: str, min_grade: str | None) -> bool:
        if min_grade is None:
            return True
        lot_r = self.grade_rank.get(str(lot_grade).upper())
        min_r = self.grade_rank.get(str(min_grade).upper())
        if lot_r is not None and min_r is not None:
            return lot_r >= min_r
        return str(lot_grade) >= str(min_grade)

    def is_bid_valid(self, lot: dict[str, Any], buyer: dict[str, Any]) -> bool:
        if lot["remaining_sacks"] <= 0 or buyer["demand_sacks"] <= 0:
            return False
        if not self._grade_ok(lot["lot_grade"], buyer["min_grade"]):
            return False
        if buyer["max_defect"] is not None and lot["defect_ratio"] > buyer["max_defect"]:
            return False
        if buyer["min_size"] is not None and lot["bean_size"] < buyer["min_size"]:
            return False
        return True

    def match_pairs(
        self,
        lots: list[dict[str, Any]],
        buyers: list[dict[str, Any]],
        valuations: dict[str, float],
    ) -> list[dict[str, Any]]:
        valid_pairs: list[dict[str, Any]] = []
        # Sort lots ascending by V_i so cheapest qualifying lot is paired first
        sorted_lots = sorted(lots, key=lambda x: valuations.get(x["lot_id"], 120.0))
        for buyer in buyers:
            for lot in sorted_lots:
                if self.is_bid_valid(lot, buyer):
                    valid_pairs.append({
                        "lot_id": lot["lot_id"],
                        "buyer_id": buyer["buyer_id"],
                        "v_i": valuations[lot["lot_id"]],
                        "lot": lot,
                        "buyer": buyer,
                        "bid_valid": True,
                    })
        return valid_pairs
