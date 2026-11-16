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
            lot_id, k = _extract_key(raw, lot_map.get("lot_id", ["lot_id"]), f"lot_{idx+1}")
            if k: used_keys.add(k)

            # Process: dry vs wet
            proc_raw, k = _extract_key(raw, lot_map.get("process", ["process"]), "dry")
            if k: used_keys.add(k)
            proc_str = str(proc_raw).lower()
            if "wet" in proc_str or "wash" in proc_str:
                norm_process = "wet"
            elif "dry" in proc_str or "nat" in proc_str:
                norm_process = "dry"
            else:
                norm_process = proc_str or "dry"

            # Moisture / Humidity
            moisture_val, k = _extract_key(raw, lot_map.get("moisture", ["moisture", "humidity"]), 10.8)
            if k: used_keys.add(k)
            moisture = float(moisture_val)

            # Ripeness (scale 0 - 100%)
            ripeness_val, k = _extract_key(raw, lot_map.get("ripeness", ["ripeness"]), 85.0)
            if k: used_keys.add(k)
            ripeness = float(ripeness_val)
            if ripeness <= 1.0:
                ripeness *= 100.0

            # Bean shape: WHOLE vs BROKEN
            shape_val, k = _extract_key(raw, lot_map.get("bean_shape", ["bean_shape"]), None)
            if k: used_keys.add(k)
            broken_val, k = _extract_key(raw, lot_map.get("broken_ratio", ["broken_ratio"]), 0.0)
            if k: used_keys.add(k)
            broken_ratio = float(broken_val)
            if broken_ratio > 1.0:
                broken_ratio /= 100.0

            if shape_val is not None:
                norm_shape = "BROKEN" if "BROK" in str(shape_val).upper() else "WHOLE"
            else:
                norm_shape = "BROKEN" if broken_ratio >= 0.10 else "WHOLE"

            # Evaluated Value / Baseline V
            v_val, k = _extract_key(raw, lot_map.get("v_i", ["v_i", "value"]), None)
            if k: used_keys.add(k)

            # Legacy features
            bean_size, k = _extract_key(raw, lot_map.get("bean_size", ["bean_size"]), 6.35)
            if k: used_keys.add(k)
            defect_ratio, k = _extract_key(raw, lot_map.get("defect_ratio", ["defect_ratio"]), 0.05)
            if k: used_keys.add(k)
            sacks, k = _extract_key(raw, lot_map.get("sacks", ["sacks"]), 0)
            if k: used_keys.add(k)
            lot_grade, k = _extract_key(raw, lot_map.get("lot_grade", ["lot_grade"]), "B")
            if k: used_keys.add(k)

            defect_val = float(defect_ratio)
            if defect_val > 1.0:
                defect_val = defect_val / 100.0

            extra = {ek: ev for ek, ev in raw.items() if ek not in used_keys}
            canonical.append({
                "lot_id": str(lot_id),
                "process": norm_process,
                "moisture": round(moisture, 2),
                "ripeness": round(ripeness, 1),
                "bean_shape": norm_shape,
                "broken_ratio": round(broken_ratio, 4),
                "baseline_v": float(v_val) if v_val is not None else None,
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
            buyer_id, _ = _extract_key(raw, buyer_map.get("buyer_id", ["buyer_id"]), f"buyer_{idx+1}")
            req_process, _ = _extract_key(raw, buyer_map.get("required_process", ["required_process"]), "ANY")
            max_moisture, _ = _extract_key(raw, buyer_map.get("max_moisture", ["max_moisture"]), None)
            min_ripeness, _ = _extract_key(raw, buyer_map.get("min_ripeness", ["min_ripeness"]), None)
            shape_req, _ = _extract_key(raw, buyer_map.get("bean_shape_req", ["bean_shape_req"]), "ANY")
            max_broken, _ = _extract_key(raw, buyer_map.get("max_broken", ["max_broken"]), None)
            target_val, _ = _extract_key(raw, buyer_map.get("target_value", ["target_value"]), None)

            # Legacy fields
            min_grade, _ = _extract_key(raw, buyer_map.get("min_grade", ["min_grade"]), None)
            max_defect, _ = _extract_key(raw, buyer_map.get("max_defect", ["max_defect"]), None)
            min_size, _ = _extract_key(raw, buyer_map.get("min_size", ["min_size"]), None)
            demand_sacks, _ = _extract_key(raw, buyer_map.get("demand_sacks", ["demand_sacks"]), 0)

            min_rip_val = float(min_ripeness) if min_ripeness is not None else None
            if min_rip_val is not None and min_rip_val <= 1.0:
                min_rip_val *= 100.0

            max_def_val = float(max_defect) if max_defect is not None else None
            if max_def_val is not None and max_def_val > 1.0:
                max_def_val = max_def_val / 100.0

            max_brk_val = float(max_broken) if max_broken is not None else None
            if max_brk_val is not None and max_brk_val > 1.0:
                max_brk_val = max_brk_val / 100.0

            canonical.append({
                "buyer_id": str(buyer_id),
                "required_process": str(req_process).lower() if str(req_process).upper() not in ["ANY", "ALL", "NONE", ""] else "ANY",
                "max_moisture": float(max_moisture) if max_moisture is not None else None,
                "min_ripeness": min_rip_val,
                "shape_requirement": str(shape_req).upper() if str(shape_req).upper() not in ["ANY", "ALL", "NONE", ""] else "ANY",
                "max_broken": max_brk_val,
                "target_value": float(target_val) if target_val is not None else None,
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

        # 1. Process Requirement (dry vs wet)
        req_proc = buyer.get("required_process", "ANY")
        if req_proc and req_proc.upper() not in ["ANY", "ALL", "NONE", ""]:
            if str(lot.get("process", "dry")).lower() != str(req_proc).lower():
                return False

        # 2. Moisture Requirement (e.g., max_moisture <= 12.0%)
        max_m = buyer.get("max_moisture")
        if max_m is not None and float(lot.get("moisture", 11.0)) > float(max_m):
            return False

        # 3. Ripeness Requirement (e.g., min_ripeness >= 80%)
        min_rip = buyer.get("min_ripeness")
        if min_rip is not None and float(lot.get("ripeness", 100.0)) < float(min_rip):
            return False

        # 4. Bean Shape Requirement (WHOLE vs BROKEN)
        shape_req = buyer.get("shape_requirement", "ANY")
        if shape_req and str(shape_req).upper() in ["WHOLE", "WHOLE_ONLY"]:
            if str(lot.get("bean_shape", "WHOLE")).upper() != "WHOLE":
                return False

        max_brk = buyer.get("max_broken")
        if max_brk is not None and float(lot.get("broken_ratio", 0.0)) > float(max_brk):
            return False

        # 5. Legacy Fallback Checks (grade, defect_ratio, bean_size)
        if not self._grade_ok(lot.get("lot_grade", "B"), buyer.get("min_grade")):
            return False
        if buyer.get("max_defect") is not None and float(lot.get("defect_ratio", 0.0)) > float(buyer["max_defect"]):
            return False
        if buyer.get("min_size") is not None and float(lot.get("bean_size", 6.35)) < float(buyer["min_size"]):
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
