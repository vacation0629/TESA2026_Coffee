from __future__ import annotations
from typing import Any, Callable

# Optional 1-line Excel drop-in for Nov 17 when valuation_mode == "CUSTOM_LAMBDA"
def default_custom_valuation(lot: dict[str, Any], v_base: float) -> float:
    # If explicit baseline value is provided in lot, respect it:
    if "baseline_v" in lot and lot["baseline_v"] is not None:
        return float(lot["baseline_v"])
    if "value" in lot and lot["value"] is not None:
        return float(lot["value"])
    if "v_i" in lot and lot["v_i"] is not None:
        return float(lot["v_i"])

    # Physical parameter valuation:
    # 1. Process premium: wet (+10 THB/kg) vs dry (baseline 0)
    proc = str(lot.get("process", "dry")).lower()
    proc_adj = 10.0 if proc in ["wet", "washed", "honey"] else 0.0

    # 2. Moisture content (target 10.0% - 12.0%)
    moisture = float(lot.get("moisture", lot.get("humidity", 11.0)))
    moisture_adj = 0.0
    if moisture > 12.0:
        moisture_adj = -5.0 * (moisture - 12.0)
    elif moisture < 10.0:
        moisture_adj = -5.0 * (10.0 - moisture)

    # 3. Ripeness (0 - 100% scale, baseline 85%)
    ripeness = float(lot.get("ripeness", 85.0))
    if ripeness <= 1.0:
        ripeness *= 100.0
    ripeness_adj = 0.25 * (ripeness - 85.0)

    # 4. Bean Shape / Broken ratio (WHOLE vs BROKEN)
    shape = str(lot.get("bean_shape", "WHOLE")).upper()
    broken_ratio = float(lot.get("broken_ratio", lot.get("defect_ratio", 0.05)))
    if broken_ratio > 1.0:
        broken_ratio /= 100.0
    shape_penalty = -15.0 if shape == "BROKEN" else (-30.0 * broken_ratio)

    # Legacy fallback grade bonus if present and no process specified
    grade_bonus = {"A": 10.0, "B": 0.0, "C": -10.0, "1": 10.0, "2": 0.0, "3": -10.0}
    g = str(lot.get("lot_grade", "B"))
    g_bonus = grade_bonus.get(g, 0.0) if "process" not in lot else 0.0

    calc_v = v_base + proc_adj + moisture_adj + ripeness_adj + shape_penalty + g_bonus
    return round(max(60.0, calc_v), 2)


PIPELINE_CONFIG: dict[str, Any] = {
    # --- 1. API & Runtime Endpoints (Update on Nov 17) ---
    "api": {
        "base_url": "http://127.0.0.1:8000",
        "allowed_ip": "",             # e.g., "10.x.x.x" (empty string allows any host)
        "allowed_port": None,         # e.g., 8000 (None allows any port)
        "allowed_types": ("application/json",),
        "team_api_key": "REPLACE_WITH_TEAM_KEY",
        "endpoints": {
            "init": "/api/init",
            "board": "/api/market/board",
            "bid": "/api/market/bid",
            "result": "/api/market/result",
            "track12_ingest": "/api/connectivity/sensors",
            "llm": "/api/llm/chat",
        },
        "http_timeout_sec": 10.0,
        "llm_timeout_sec": 15.0,
        "dry_run": False,             # Set True during Phase 1 passive shadow polling
    },

    # --- 2. Competition Economics & Guardrails ---
    "market_rules": {
        "v_base": 120.0,
        "demand_ratio": 0.90,
        "quota_multiplier": 1.50,
        "buyback_rate": 0.80,
        "hard_floor_multiplier": 0.81,  # Strict > 0.80 buyback floor
        "default_teams": 45,
        "default_total_rounds": 15,
    },

    # --- 3. Schema-Agnostic Field Mapping (Stage 1) ---
    "schema_map": {
        "lot": {
            "lot_id": ["lot_id", "id", "coffee_id", "batch_id"],
            "process": ["process", "processing_method", "method", "process_type"],
            "moisture": ["moisture", "humidity", "moisture_pct", "hum", "mc"],
            "ripeness": ["ripeness", "ripeness_pct", "ripe_ratio", "brix_ripeness"],
            "bean_shape": ["bean_shape", "shape", "broken_status", "integrity", "defect_type"],
            "broken_ratio": ["broken_ratio", "broken_pct", "broken_beans", "defect_ratio"],
            "bean_size": ["bean_size", "size", "screen_size", "bean_mm"],
            "defect_ratio": ["defect_ratio", "defect", "defect_pct", "damage_ratio"],
            "sacks": ["remaining_sacks", "sacks", "quantity", "stock"],
            "lot_grade": ["lot_grade", "grade", "tier", "quality_grade"],
            "v_i": ["v_i", "value", "evaluated_value", "baseline_v", "base_price"],
        },
        "buyer": {
            "buyer_id": ["buyer_id", "id", "bot_id", "name"],
            "required_process": ["required_process", "process", "process_req", "method_req"],
            "max_moisture": ["max_moisture", "moisture_max", "max_humidity", "humidity_max"],
            "min_ripeness": ["min_ripeness", "ripeness_min", "min_ripe", "ripe_min"],
            "bean_shape_req": ["bean_shape_req", "shape_req", "required_shape", "shape"],
            "max_broken": ["max_broken", "max_defect", "defect_max", "broken_max"],
            "min_size": ["min_size", "size_min"],
            "target_value": ["target_value", "value_ceiling", "max_price", "budget"],
            "demand_sacks": ["demand_sacks", "demand", "wanted_sacks", "quota"],
            "min_grade": ["min_grade", "required_grade", "grade_min"],
        },
    },

    # --- 4. Pluggable Feature-to-Valuation Config (Stage 2) ---
    "valuation": {
        # Options: "LINEAR_WEIGHTED", "ADDITIVE_POINTS", "CUSTOM_LAMBDA"
        "mode": "LINEAR_WEIGHTED",
        "transforms": {
            "lot_grade": {
                "type": "lookup_map",
                "map": {
                    "FINE_ROBUSTA": 0.15, "PREMIUM_ROBUSTA": 0.08,
                    "A": 0.10, "B": 0.0, "C": -0.10,
                    "1": 0.10, "2": 0.0, "3": -0.10,
                },
                "default": 0.0,
            },
            "bean_size": {"type": "reference_delta", "ref": 6.35, "scale": 1.0},
            "defect_ratio": {"type": "raw"},
        },
        "weights": {
            "lot_grade": 1.0,       # Positive quality driver (+w)
            "bean_size": 0.04,      # Positive quality driver (+w)
            "defect_ratio": -0.80,  # Negative defect driver (-w)
        },
        "gate_rules": {
            "enabled": False,       # Disabled by default so synthetic datasets are never falsely rejected
            "rules": [],
        },
        "custom_fn": default_custom_valuation,
    },

    # --- 5. Buyer Spec Operators & Grade Ordering (Stage 4) ---
    "spec_matching": {
        "grade_rank": {
            "C": 1, "3": 1, "COMMERCIAL": 1,
            "B": 2, "2": 2, "TAS_SPECIAL": 2,
            "A": 3, "1": 3, "PREMIUM_ROBUSTA": 3,
            "S": 4, "0": 4, "FINE_ROBUSTA": 4,
        },
    },

    # --- 6. Heuristic & Statistical Pricing Parameters (Stages 3 & 5) ---
    "pricing": {
        "default_base_markup": 0.06,
        "buyer_base_markups": {},   # Calibrated per buyer_id from Phase 1 logs
        "alpha_slope": 0.50,        # Sensitivity to clearing price momentum Slope_t
        "beta_demand": 0.25,        # Sensitivity to demand intensity (DIR_t - 1.0)
        "gamma_urgency": 0.30,      # Liquidation discount sensitivity to IUR_t
        "stage_overrides": {
            "PRICE_DISCOVERY": {"markup_offset": 0.08, "volume_cap_ratio": 0.35},
            "EARLY_DUMPING_WAR": {"markup_offset": 0.02, "min_floor_mult": 0.98},
            "HIGH_SEASON_PEAK": {"markup_offset": 0.06, "volume_cap_ratio": 1.00},
            "LATE_SATURATION": {"markup_offset": -0.02, "undercut_clear_pct": 0.01},
            "END_GAME_SQUEEZE": {"markup_offset": -0.08, "min_floor_mult": 0.81},
        },
    },

    # --- 7. Pluggable Ensemble & Optional XGBoost Config (Stage 5) ---
    "ensemble": {
        "active_predictors": ["heuristic", "xgb", "llm"],
        "weights_cold_start": {"heuristic": 0.70, "xgb": 0.00, "llm": 0.30},
        "weights_warm_start": {"heuristic": 0.45, "xgb": 0.35, "llm": 0.20},
        "xgb": {
            "enabled": True,
            "mode": "MODE_A_RESIDUAL",  # "MODE_A_RESIDUAL" | "MODE_B_WIN_PROB" | "MODE_C_WEIGHT_TUNER"
            "min_samples": 18,          # Requires >= 18 buyer-round rows before activating
            "max_depth": 3,
            "n_estimators": 30,
            "learning_rate": 0.10,
        },
        "llm": {
            "enabled": True,
            "max_prompt_tokens": 480,
            "max_adjustment_pct": 0.12,  # Clamps LLM tactical nudge within +/-12% of P_heur
        },
    },
}
