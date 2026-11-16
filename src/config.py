from __future__ import annotations
from typing import Any, Callable

# Optional 1-line Excel drop-in for Nov 17 when valuation_mode == "CUSTOM_LAMBDA"
def default_custom_valuation(lot: dict[str, Any], v_base: float) -> float:
    grade_bonus = {"A": 12.0, "B": 0.0, "C": -10.0, "1": 12.0, "2": 0.0, "3": -10.0}
    g = str(lot.get("lot_grade", "2"))
    size = float(lot.get("bean_size", 6.35))
    defect = float(lot.get("defect_ratio", 0.05))
    return v_base + grade_bonus.get(g, 0.0) + 5.0 * (size - 6.35) - 80.0 * defect


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
            "lot_grade": ["lot_grade", "grade", "tier", "quality_grade"],
            "bean_size": ["bean_size", "size", "screen_size", "bean_mm"],
            "defect_ratio": ["defect_ratio", "defect", "defect_pct", "damage_ratio"],
            "sacks": ["remaining_sacks", "sacks", "quantity", "stock"],
        },
        "buyer": {
            "buyer_id": ["buyer_id", "id", "bot_id", "name"],
            "min_grade": ["min_grade", "required_grade", "grade_min"],
            "max_defect": ["max_defect", "defect_max", "max_defect_ratio"],
            "min_size": ["min_size", "size_min"],
            "demand_sacks": ["demand_sacks", "demand", "wanted_sacks", "quota"],
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
