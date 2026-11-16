# \[v2.3.0 — Part 4 of 4\] Local-AI Implementation Blueprint & Modular Python Codebase (Milestone M5)

**Project:** TESA Top Gun Rally 2026 — End-to-End Coffee Quality & Autonomous Market Agent  
**Version:** `v2.3.0` (Self-Contained Modular Suite — Part 4 of 4\)  
**Modular Suite Structure (`v2`):**

* **Part 1 (**`v2_part1_upstream_coffee_science.md`**):** Upstream Agronomy, Varietal Genetics, Harvesting, Metagenomic Fermentation, Solar/OTA Drying & Post-Hulling Storage Safety.  
* **Part 2 (**`v2_part2_grading_cv_chemistry_roasting.md`**):** Downstream CQI/TAS 5700 Grading Gatekeepers, Hardware/CV Morphometrics, Active Thermography, NIR/FTIR Spectroscopy, Roasting Chemistry, Carbon Footprint, Circular Bioeconomy & 18-Feature Python Schema.  
* **Part 3 (**`v2_part3_competition_agent_and_pricing_engine.md`**):** Track 3 Competition Rules, Pluggable Feature-to-Valuation Framework, 25 Market/API Variables, 5 Statistical Market-Stage Indicators (`CPR`, `Slope`, `CV`, `DIR`, `IUR`), Hybrid Quantitative-First \+ Qwen 9B Pricing Engine, Optional XGBoost & Risk Matrix.  
* **Part 4 (**`v2_part4_local_ai_implementation_blueprint.md`**):** Production-Ready 13-File Python Codebase (`config.py`, `logger.py`, `adapters.py`, `stats_engine.py`, `xgb_plugin.py`, `predictors.py`, `guardrails.py`, `agent_loop.py`), `auto_sniffer.py`, CI/CD Workflow & End-to-End Tests.

**Date:** 2026-11-16  
**Target Audience:** Local AI Coding Assistant (Claude Code / Cursor / GitHub Copilot) & Team Developers

---

## 0\. Local AI Execution Directive & System Overview

**Instructions for Local AI Coding Assistant:**  
Implement the repository structure and Python modules defined in Sections 2–4 verbatim. Do **NOT** invent hardcoded real-world coffee quality thresholds (such as fixed moisture percentages, water activity cutoffs, or 350 g defect counts), do **NOT** require `xgboost` at import time (`try...except ImportError` is mandatory), and do **NOT** pass raw multi-round JSON logs to the central LLM (`4K` token context limit). Every module communicates via canonical Python `dict` structures and primitive types (`int`, `float`, `string`, `bool`, `list`), controlled centrally by `src/config.py`.

### System & Competition Architecture Summary

* **Market Environment:** Sealed-bid Robusta green-bean auction competing against `35–55` teams (`6–8` practice rounds on Nov 17, `15` final rounds on Nov 20, `~300s` per round).  
* **Core Economic Rules:** Baseline price `V_base = 120.0` THB/kg (`float`); score measures profit margin relative to your lot's intrinsic evaluated value (`V_i`); aggregate market demand is `~90%` (`0.9`) of total supply; max sacks offered per round are capped at `1.5x` average (`Q_max`); unsold sacks at game end settle via central buyback at `80%` (`0.80 * V_i`), locking our hard price floor at `0.81 * V_i`.  
* **6-Stage Schema-Agnostic Pipeline:** `DynamicSchemaAdapter` \$\\rightarrow\$ `FlexibleValuationEngine` \$\\rightarrow\$ `FeatureStoreAndStats` (`CPR_t`, `Slope_t`, `CV_t`, `DIR_t`, `IUR_t`) \$\\rightarrow\$ `SpecAndQuotaMatcher` \$\\rightarrow\$ `PluggablePredictorEnsemble` (`Heuristic` \+ `Optional XGBoost` \+ `Qwen 9B LLM`) \$\\rightarrow\$ `SafetyGuardrailEnforcer`.  
* **Zero-Loss Black-Box Telemetry:** Every HTTP `GET`/`POST` payload matching target IP, port, and `Content-Type` is flushed immediately (`os.fsync`) to `logs/<match_id>/raw_events.jsonl` and checkpointed atomically to `state_snapshot.json` for CI/CD persistence.

---

## 1\. Repository Directory Layout

```
tesa2026-track3-agent/
├── .github/
│   └── workflows/
│       └── trade.yml                 # GitHub Actions CI/CD runner + telemetry-logs branch push
├── src/
│   ├── __init__.py
│   ├── config.py                     # Central PIPELINE_CONFIG (all weights, maps, formulas, thresholds)
│   ├── logger.py                     # FlightRecorder (JSONL + fsync) & filtered requests.Session hook
│   ├── adapters.py                   # DynamicSchemaAdapter, FlexibleValuationEngine, SpecAndQuotaMatcher
│   ├── stats_engine.py               # FeatureStoreAndStats (5 indicators + 5-stage market classifier)
│   ├── xgb_plugin.py                 # OptionalXGBPlugin (3 modes) + pure-Python EWMAFallbackPlugin
│   ├── predictors.py                 # HeuristicPricePredictor, CompressedLLMAdvisor, Ensemble blender
│   ├── guardrails.py                 # SafetyGuardrailEnforcer (0.81*V_i floor, spec & Q_max clamping)
│   └── agent_loop.py                 # Main Observe -> Think -> Act -> Persist loop + Track 1/2 stub
├── tools/
│   └── auto_sniffer.py               # Phase 1 mitmdump passive traffic recorder (IP/Port/MIME filter)
├── tests/
│   └── test_pipeline_e2e.py          # Offline end-to-end tests (cold start, warm start, LLM timeout)
├── logs/                             # Auto-generated runtime telemetry (gitignored on main, pushed to telemetry-logs)
└── requirements.txt                  # Minimal CI/CD dependencies (requests; xgboost optional)
```

---

## 2\. Core Configuration & Telemetry Modules

### 2.1 `requirements.txt`

```
requests>=2.31.0
# Optional ML plugin (agent falls back cleanly to EWMAFallbackPlugin if absent in CI/CD):
# xgboost>=2.0.0
# numpy>=1.26.0
```

### 2.2 `src/config.py`

```py
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
```

### 2.3 `src/logger.py`

```py
from __future__ import annotations
import json
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore


class FlightRecorder:
    """Append-only raw JSONL black-box logger + atomic state checkpointer."""

    def __init__(self, log_dir: str = "logs", match_id: str = "default") -> None:
        self.base_dir = Path(log_dir) / match_id
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.events_path = self.base_dir / "raw_events.jsonl"
        self.state_path = self.base_dir / "state_snapshot.json"

    def log_event(
        self,
        event_type: str,
        round_num: int,
        endpoint: str,
        payload: Any,
        status_code: int = 200,
    ) -> None:
        record = {
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "round": round_num,
            "event_type": event_type,
            "endpoint": endpoint,
            "status_code": status_code,
            "payload": payload,
        }
        with open(self.events_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def save_state(self, state: dict[str, Any]) -> None:
        tmp_path = self.state_path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2, default=str)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, self.state_path)

    def load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"history_log": [], "buyer_ceilings": {}, "round_snapshots": {}}
        with open(self.state_path, "r", encoding="utf-8") as f:
            return json.load(f)


def create_monitored_session(
    recorder: FlightRecorder,
    allowed_ip: str = "",
    allowed_port: int | None = None,
    allowed_types: tuple[str, ...] = ("application/json",),
) -> Any:
    """Creates a requests.Session that filters and logs matching HTTP traffic automatically."""
    if requests is None:
        raise RuntimeError("requests package is required for live HTTP mode.")
    session = requests.Session()

    def _on_response(resp: Any, *args: Any, **kwargs: Any) -> None:
        parsed = urlparse(resp.url)
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        ctype = resp.headers.get("Content-Type", "").lower()

        if allowed_port is not None and port != allowed_port:
            return
        if allowed_ip:
            try:
                resolved_ip = socket.gethostbyname(parsed.hostname or "")
            except OSError:
                resolved_ip = parsed.hostname or ""
            if allowed_ip not in {resolved_ip, parsed.hostname}:
                return
        if allowed_types and not any(t in ctype for t in allowed_types):
            return

        try:
            body = resp.json()
        except ValueError:
            body = resp.text

        recorder.log_event(
            event_type=f"HTTP_{resp.request.method}",
            round_num=-1,
            endpoint=resp.url,
            payload={
                "port": port,
                "content_type": ctype,
                "request": resp.request.body.decode("utf-8", errors="replace")
                if isinstance(resp.request.body, bytes)
                else resp.request.body,
                "response": body,
            },
            status_code=resp.status_code,
        )

    session.hooks["response"].append(_on_response)
    return session
```

---

## 3\. Pipeline Engine Modules (`adapters.py`, `stats_engine.py`, `xgb_plugin.py`, `predictors.py`, `guardrails.py`)

### 3.1 `src/adapters.py` (Stages 1, 2 & 4\)

```py
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
```

### 3.2 `src/stats_engine.py` (Stage 3: 5 Statistical Market-Stage Indicators)

```py
from __future__ import annotations
import math
from typing import Any


class FeatureStoreAndStats:
    """Stage 3: Computes CPR_t, Slope_t, CV_t, DIR_t, IUR_t and classifies the 5 market stages."""

    def __init__(self, rules_cfg: dict[str, Any]) -> None:
        self.rules = rules_cfg

    def compute_market_stats(
        self,
        current_round: int,
        total_rounds: int,
        initial_sacks: int,
        remaining_sacks: int,
        num_teams: int,
        buyers: list[dict[str, Any]],
        history_log: list[dict[str, Any]],
        season_state: str = "NORMAL",
    ) -> dict[str, Any]:
        # 1. Clearing Price-to-Valuation Ratio (CPR_t) & Cross-Buyer CV_t
        ratios: list[float] = []
        if history_log:
            last_round = history_log[-1]
            clearing_map: dict[str, float] = last_round.get("clearing_prices", {})
            min_spec_vals: dict[str, float] = last_round.get("buyer_min_spec_vals", {})
            for b_id, p_clear in clearing_map.items():
                v_spec = min_spec_vals.get(b_id, self.rules["v_base"])
                if v_spec > 0 and p_clear > 0:
                    ratios.append(float(p_clear) / float(v_spec))

        if ratios:
            cpr_t = sum(ratios) / len(ratios)
            variance = sum((r - cpr_t) ** 2 for r in ratios) / len(ratios)
            cv_t = math.sqrt(variance) / cpr_t if cpr_t > 0 else 0.0
        else:
            cpr_t = 1.02
            cv_t = 0.10  # Triggers PRICE_DISCOVERY on Round 1

        # 2. Clearing Price Momentum Slope (Slope_t)
        prev_cpr = float(history_log[-1].get("cpr_t", cpr_t)) if history_log else cpr_t
        slope_t = cpr_t - prev_cpr

        # 3. Demand Intensity Ratio (DIR_t)
        total_board_demand = sum(int(b.get("demand_sacks", 0)) for b in buyers)
        d_bar_expected = (
            self.rules["demand_ratio"] * float(num_teams) * float(initial_sacks)
        ) / max(1, total_rounds)
        dir_t = total_board_demand / d_bar_expected if d_bar_expected > 0 else 1.0

        # 4. Inventory Urgency Ratio (IUR_t) & Quota Cap (Q_max)
        q_max = max(1, int(round(self.rules["quota_multiplier"] * (initial_sacks / max(1, total_rounds)))))
        r_rem = max(1, total_rounds - current_round + 1)
        iur_t = float(remaining_sacks) / float(r_rem * q_max)

        # 5. Classify Market Stage
        stage = self.classify_stage(
            current_round=current_round,
            r_rem=r_rem,
            cpr_t=cpr_t,
            slope_t=slope_t,
            cv_t=cv_t,
            dir_t=dir_t,
            iur_t=iur_t,
            season_state=season_state,
            has_history=bool(history_log),
        )

        return {
            "round": current_round,
            "total_rounds": total_rounds,
            "r_rem": r_rem,
            "q_max": q_max,
            "cpr_t": round(cpr_t, 4),
            "slope_t": round(slope_t, 4),
            "cv_t": round(cv_t, 4),
            "dir_t": round(dir_t, 4),
            "iur_t": round(iur_t, 4),
            "season_state": season_state,
            "market_stage": stage,
        }

    @staticmethod
    def classify_stage(
        current_round: int,
        r_rem: int,
        cpr_t: float,
        slope_t: float,
        cv_t: float,
        dir_t: float,
        iur_t: float,
        season_state: str,
        has_history: bool,
    ) -> str:
        if iur_t > 0.70 or r_rem <= 2:
            return "END_GAME_SQUEEZE"
        if not has_history or (current_round <= 2 and cv_t > 0.08):
            return "PRICE_DISCOVERY"
        if cpr_t < 0.98 and slope_t < 0:
            return "EARLY_DUMPING_WAR"
        if dir_t > 1.15 or "HIGH" in season_state.upper():
            return "HIGH_SEASON_PEAK"
        if dir_t < 0.85 or "LATE" in season_state.upper():
            return "LATE_SATURATION"
        return "HIGH_SEASON_PEAK" if slope_t > 0 else "LATE_SATURATION"
```

### 3.3 `src/xgb_plugin.py` (Optional Pluggable XGBoost \+ EWMA Fallback)

```py
from __future__ import annotations
from typing import Any

try:
    import numpy as np
    import xgboost as xgb
    HAS_XGB = True
except ImportError:  # pragma: no cover
    np = None  # type: ignore
    xgb = None  # type: ignore
    HAS_XGB = False


class EWMAFallbackPlugin:
    """Zero-dependency pure-Python residual tracker when xgboost is unavailable or under-sampled."""

    def __init__(self, alpha: float = 0.35) -> None:
        self.alpha = alpha
        self.buyer_residuals: dict[str, float] = {}

    def fit(self, rows: list[dict[str, Any]]) -> None:
        self.buyer_residuals.clear()
        for row in rows:
            b_id = str(row.get("buyer_id", ""))
            res = float(row.get("residual", 0.0))
            prev = self.buyer_residuals.get(b_id, 0.0)
            self.buyer_residuals[b_id] = self.alpha * res + (1.0 - self.alpha) * prev

    def predict_adjustment(self, features: dict[str, Any]) -> float:
        b_id = str(features.get("buyer_id", ""))
        return self.buyer_residuals.get(b_id, 0.0)


class OptionalXGBPlugin:
    """Pluggable shallow XGBoost predictor supporting MODE_A_RESIDUAL, MODE_B_WIN_PROB, MODE_C_WEIGHT_TUNER."""

    FEATURE_KEYS = ["cpr_t", "slope_t", "cv_t", "dir_t", "iur_t", "demand_sacks", "defect_ratio", "bean_size"]

    def __init__(self, xgb_cfg: dict[str, Any]) -> None:
        self.cfg = xgb_cfg
        self.mode: str = xgb_cfg.get("mode", "MODE_A_RESIDUAL")
        self.min_samples: int = int(xgb_cfg.get("min_samples", 18))
        self.fallback = EWMAFallbackPlugin()
        self.model: Any = None
        self.buyer_index: dict[str, int] = {}
        self.trained_samples: int = 0

    def is_ready(self) -> bool:
        return (
            bool(self.cfg.get("enabled", True))
            and HAS_XGB
            and self.model is not None
            and self.trained_samples >= self.min_samples
        )

    def _vectorize(self, row: dict[str, Any]) -> list[float]:
        b_id = str(row.get("buyer_id", "unknown"))
        if b_id not in self.buyer_index:
            self.buyer_index[b_id] = len(self.buyer_index)
        vec = [float(row.get(k, 0.0)) for k in self.FEATURE_KEYS]
        vec.append(float(self.buyer_index[b_id]))
        return vec

    def fit(self, history_rows: list[dict[str, Any]]) -> None:
        self.fallback.fit(history_rows)
        self.trained_samples = len(history_rows)
        if not (self.cfg.get("enabled", True) and HAS_XGB and self.trained_samples >= self.min_samples):
            self.model = None
            return

        X = np.array([self._vectorize(r) for r in history_rows], dtype=float)
        if self.mode == "MODE_B_WIN_PROB":
            y = np.array([1 if r.get("won", False) else 0 for r in history_rows], dtype=int)
            clf = xgb.XGBClassifier(
                max_depth=int(self.cfg.get("max_depth", 3)),
                n_estimators=int(self.cfg.get("n_estimators", 30)),
                learning_rate=float(self.cfg.get("learning_rate", 0.1)),
                eval_metric="logloss",
            )
            clf.fit(X, y)
            self.model = clf
        else:
            y = np.array([float(r.get("residual", 0.0)) for r in history_rows], dtype=float)
            reg = xgb.XGBRegressor(
                max_depth=int(self.cfg.get("max_depth", 3)),
                n_estimators=int(self.cfg.get("n_estimators", 30)),
                learning_rate=float(self.cfg.get("learning_rate", 0.1)),
            )
            reg.fit(X, y)
            self.model = reg

    def predict_price(self, v_i: float, p_heur: float, features: dict[str, Any]) -> tuple[float, bool]:
        """Returns (predicted_price, used_xgb_flag)."""
        if not self.is_ready():
            delta = self.fallback.predict_adjustment(features)
            return v_i * ((p_heur / max(1.0, v_i)) + delta), False

        x_vec = np.array([self._vectorize(features)], dtype=float)
        if self.mode == "MODE_B_WIN_PROB":
            # Grid-search candidate multipliers around p_heur to maximize Expected Value
            best_price = p_heur
            best_ev = -1e9
            for mult in (0.96, 0.98, 1.00, 1.02, 1.04, 1.06):
                cand_price = p_heur * mult
                cand_feat = dict(features, cpr_t=cand_price / max(1.0, v_i))
                prob = float(self.model.predict_proba(np.array([self._vectorize(cand_feat)], dtype=float))[0][1])
                ev = (cand_price - v_i) * prob + (-0.20 * v_i) * (1.0 - prob)
                if ev > best_ev:
                    best_ev = ev
                    best_price = cand_price
            return best_price, True

        delta_m = float(self.model.predict(x_vec)[0])
        return p_heur + (v_i * delta_m), True
```

### 3.4 `src/predictors.py` & `src/guardrails.py` (Stages 5 & 6\)

```py
from __future__ import annotations
import json
from typing import Any
from src.xgb_plugin import OptionalXGBPlugin


class HeuristicPricePredictor:
    """Deterministic baseline pricing formula driven by statistical market regime indicators."""

    def __init__(self, pricing_cfg: dict[str, Any]) -> None:
        self.cfg = pricing_cfg

    def predict(self, v_i: float, buyer_id: str, stats: dict[str, Any]) -> float:
        stage = stats["market_stage"]
        overrides = self.cfg.get("stage_overrides", {}).get(stage, {})
        m_base = float(self.cfg.get("buyer_base_markups", {}).get(buyer_id, self.cfg["default_base_markup"]))
        m_offset = float(overrides.get("markup_offset", 0.0))

        adj = (
            m_base
            + m_offset
            + float(self.cfg["alpha_slope"]) * float(stats["slope_t"])
            + float(self.cfg["beta_demand"]) * (float(stats["dir_t"]) - 1.0)
            - float(self.cfg["gamma_urgency"]) * float(stats["iur_t"])
        )
        return v_i * (1.0 + adj)


class CompressedLLMAdvisor:
    """Consults central Qwen 9B LLM using < 500 token summary with strict timeout fallback."""

    def __init__(self, api_cfg: dict[str, Any], llm_cfg: dict[str, Any], session: Any = None) -> None:
        self.api_cfg = api_cfg
        self.llm_cfg = llm_cfg
        self.session = session

    def build_compact_prompt(self, stats: dict[str, Any], candidates: list[dict[str, Any]]) -> str:
        top3 = [
            {
                "lot": c["lot_id"],
                "buyer": c["buyer_id"],
                "v_i": round(c["v_i"], 2),
                "p_heur": round(c["p_heur"], 2),
            }
            for c in candidates[:3]
        ]
        summary = {
            "round": f"{stats['round']}/{stats['total_rounds']}",
            "stage": stats["market_stage"],
            "cpr": stats["cpr_t"],
            "dir": stats["dir_t"],
            "iur": stats["iur_t"],
            "season": stats["season_state"],
            "top_pairs": top3,
        }
        return (
            "Robusta coffee market advisor. Return ONLY JSON mapping 'lot_id:buyer_id' to adjusted price float "
            "within +/-10% of p_heur. State: " + json.dumps(summary, separators=(",", ":"))
        )

    def advise(self, stats: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, float]:
        if not self.llm_cfg.get("enabled", True) or self.session is None or not candidates:
            return {}
        prompt = self.build_compact_prompt(stats, candidates)
        url = self.api_cfg["base_url"].rstrip("/") + self.api_cfg["endpoints"]["llm"]
        headers = {"Authorization": f"Bearer {self.api_cfg['team_api_key']}"}
        try:
            resp = self.session.post(
                url,
                json={"prompt": prompt, "max_tokens": 180, "temperature": 0.2},
                headers=headers,
                timeout=float(self.api_cfg.get("llm_timeout_sec", 15.0)),
            )
            resp.raise_for_status()
            data = resp.json()
            raw_text = data.get("text") or data.get("response") or json.dumps(data)
            parsed = json.loads(raw_text) if isinstance(raw_text, str) else raw_text
            return {str(k): float(v) for k, v in parsed.items()}
        except Exception:
            return {}  # Automatic zero-crash fallback to deterministic ensemble


class PluggablePredictorEnsemble:
    """Stage 5: Blends Heuristic, Optional XGBoost, and Qwen 9B LLM with dynamic weight redistribution."""

    def __init__(
        self,
        ensemble_cfg: dict[str, Any],
        heuristic: HeuristicPricePredictor,
        xgb_plugin: OptionalXGBPlugin,
        llm_advisor: CompressedLLMAdvisor,
    ) -> None:
        self.cfg = ensemble_cfg
        self.heuristic = heuristic
        self.xgb_plugin = xgb_plugin
        self.llm_advisor = llm_advisor

    def score_candidates(self, stats: dict[str, Any], pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for p in pairs:
            p["p_heur"] = self.heuristic.predict(p["v_i"], p["buyer_id"], stats)

        llm_nudges = self.llm_advisor.advise(stats, pairs)
        base_weights = (
            self.cfg["weights_warm_start"] if self.xgb_plugin.is_ready() else self.cfg["weights_cold_start"]
        )
        max_nudge = float(self.cfg.get("llm", {}).get("max_adjustment_pct", 0.12))

        scored: list[dict[str, Any]] = []
        for p in pairs:
            feat_row = {
                **stats,
                "buyer_id": p["buyer_id"],
                "demand_sacks": p["buyer"]["demand_sacks"],
                "defect_ratio": p["lot"]["defect_ratio"],
                "bean_size": p["lot"]["bean_size"],
            }
            p_xgb, used_xgb = self.xgb_plugin.predict_price(p["v_i"], p["p_heur"], feat_row)

            pair_key = f"{p['lot_id']}:{p['buyer_id']}"
            has_llm = pair_key in llm_nudges
            if has_llm:
                raw_llm = llm_nudges[pair_key]
                p_llm = max(p["p_heur"] * (1.0 - max_nudge), min(p["p_heur"] * (1.0 + max_nudge), raw_llm))
            else:
                p_llm = p["p_heur"]

            w_h = float(base_weights["heuristic"])
            w_x = float(base_weights["xgb"]) if used_xgb else 0.0
            w_l = float(base_weights["llm"]) if has_llm else 0.0
            w_sum = w_h + w_x + w_l
            if w_sum <= 0:
                p_ens = p["p_heur"]
            else:
                p_ens = (w_h * p["p_heur"] + w_x * p_xgb + w_l * p_llm) / w_sum

            scored.append({**p, "p_xgb": p_xgb, "p_llm": p_llm, "p_ensemble": p_ens})
        return scored


class SafetyGuardrailEnforcer:
    """Stage 6: Enforces hard floor (>= 0.81 * V_i), spec validity, and per-round Q_max quota."""

    def __init__(self, rules_cfg: dict[str, Any], pricing_cfg: dict[str, Any]) -> None:
        self.rules = rules_cfg
        self.pricing_cfg = pricing_cfg

    def build_final_bids(self, stats: dict[str, Any], scored_pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        stage = stats["market_stage"]
        stage_cfg = self.pricing_cfg.get("stage_overrides", {}).get(stage, {})
        vol_ratio = float(stage_cfg.get("volume_cap_ratio", 1.0))
        stage_floor_mult = float(stage_cfg.get("min_floor_mult", self.rules["hard_floor_multiplier"]))

        q_max = int(stats["q_max"])
        target_round_sacks = max(1, int(round(q_max * vol_ratio)))
        sacks_allocated = 0
        lot_used: dict[str, int] = {}
        final_bids: list[dict[str, Any]] = []

        # Prioritize highest expected margin ratio (p_ensemble / v_i)
        ranked = sorted(scored_pairs, key=lambda x: x["p_ensemble"] / max(1.0, x["v_i"]), reverse=True)
        for cand in ranked:
            if sacks_allocated >= target_round_sacks:
                break
            if not cand.get("bid_valid", False):
                continue

            lot_id = cand["lot_id"]
            avail_lot = cand["lot"]["remaining_sacks"] - lot_used.get(lot_id, 0)
            avail_buyer = cand["buyer"]["demand_sacks"]
            rem_quota = target_round_sacks - sacks_allocated
            sacks_to_bid = min(avail_lot, avail_buyer, rem_quota)
            if sacks_to_bid <= 0:
                continue

            hard_floor = max(
                float(self.rules["hard_floor_multiplier"]) * cand["v_i"],
                stage_floor_mult * cand["v_i"],
            )
            clamped_price = round(max(hard_floor, float(cand["p_ensemble"])), 2)

            final_bids.append({
                "lot_id": lot_id,
                "buyer_id": cand["buyer_id"],
                "sacks": int(sacks_to_bid),
                "price_per_kg": clamped_price,
            })
            lot_used[lot_id] = lot_used.get(lot_id, 0) + sacks_to_bid
            sacks_allocated += sacks_to_bid

        return final_bids
```

---

## 4\. Orchestrator, Sniffer, CI/CD & End-to-End Verification (`agent_loop.py`, `auto_sniffer.py`, `trade.yml`, `test_pipeline_e2e.py`)

### 4.1 `src/agent_loop.py`

```py
from __future__ import annotations
from typing import Any
from src.adapters import DynamicSchemaAdapter, FlexibleValuationEngine, SpecAndQuotaMatcher
from src.config import PIPELINE_CONFIG
from src.guardrails import SafetyGuardrailEnforcer
from src.logger import FlightRecorder, create_monitored_session
from src.predictors import CompressedLLMAdvisor, HeuristicPricePredictor, PluggablePredictorEnsemble
from src.stats_engine import FeatureStoreAndStats
from src.xgb_plugin import OptionalXGBPlugin


class MarketAgentOrchestrator:
    """Executes one complete Observe -> Think -> Act -> Persist cycle."""

    def __init__(self, config: dict[str, Any] = PIPELINE_CONFIG, match_id: str = "live", session: Any = None) -> None:
        self.cfg = config
        self.recorder = FlightRecorder(log_dir="logs", match_id=match_id)
        self.state = self.recorder.load_state()
        self.session = session or (
            create_monitored_session(
                self.recorder,
                allowed_ip=config["api"]["allowed_ip"],
                allowed_port=config["api"]["allowed_port"],
                allowed_types=config["api"]["allowed_types"],
            )
            if not config["api"].get("dry_run", False)
            else None
        )

        self.adapter = DynamicSchemaAdapter(config["schema_map"])
        self.valuator = FlexibleValuationEngine(config["valuation"], config["market_rules"]["v_base"])
        self.stats_engine = FeatureStoreAndStats(config["market_rules"])
        self.matcher = SpecAndQuotaMatcher(config["spec_matching"]["grade_rank"])
        self.heuristic = HeuristicPricePredictor(config["pricing"])
        self.xgb_plugin = OptionalXGBPlugin(config["ensemble"]["xgb"])
        self.llm_advisor = CompressedLLMAdvisor(config["api"], config["ensemble"]["llm"], self.session)
        self.ensemble = PluggablePredictorEnsemble(
            config["ensemble"], self.heuristic, self.xgb_plugin, self.llm_advisor
        )
        self.guardrails = SafetyGuardrailEnforcer(config["market_rules"], config["pricing"])

    def ingest_track12_connectivity(self, track1_payload: dict[str, Any], track2_payload: dict[str, Any]) -> dict[str, Any]:
        """Logs and forwards Track 1/2 sensor & vision payloads for connectivity points."""
        combined = {"track1": track1_payload, "track2": track2_payload}
        self.recorder.log_event("TRACK12_CONNECTIVITY", 0, "local_ingest", combined)
        return combined

    def run_round(self, raw_board_payload: dict[str, Any]) -> dict[str, Any]:
        current_round = int(raw_board_payload.get("round", 1))
        total_rounds = int(raw_board_payload.get("total_rounds", self.cfg["market_rules"]["default_total_rounds"]))
        num_teams = int(raw_board_payload.get("num_teams", self.cfg["market_rules"]["default_teams"]))
        season_state = str(raw_board_payload.get("season_state", "NORMAL"))

        self.recorder.log_event("BOARD_POLL", current_round, "board", raw_board_payload)

        # Warm-start XGBoost / EWMA from accumulated history_log
        training_rows: list[dict[str, Any]] = []
        for h in self.state.get("history_log", []):
            training_rows.extend(h.get("training_rows", []))
        self.xgb_plugin.fit(training_rows)

        lots = self.adapter.normalize_lots(raw_board_payload.get("lots", []))
        buyers = self.adapter.normalize_buyers(raw_board_payload.get("buyers", []))
        valuations = self.valuator.evaluate_all(lots)

        rem_sacks = sum(l["remaining_sacks"] for l in lots)
        init_sacks = int(self.state.get("initial_sacks") or rem_sacks or 30)
        self.state["initial_sacks"] = init_sacks

        stats = self.stats_engine.compute_market_stats(
            current_round=current_round,
            total_rounds=total_rounds,
            initial_sacks=init_sacks,
            remaining_sacks=rem_sacks,
            num_teams=num_teams,
            buyers=buyers,
            history_log=self.state.get("history_log", []),
            season_state=season_state,
        )

        valid_pairs = self.matcher.match_pairs(lots, buyers, valuations)
        scored_pairs = self.ensemble.score_candidates(stats, valid_pairs)
        final_bids = self.guardrails.build_final_bids(stats, scored_pairs)

        decision_record = {
            "round": current_round,
            "stats": stats,
            "valuations": valuations,
            "bids": final_bids,
        }
        self.recorder.log_event("DECISION_AND_BID", current_round, "bid", decision_record)
        self.recorder.save_state(self.state)
        return decision_record

    def record_settlement(self, round_num: int, settlement_payload: dict[str, Any], stats: dict[str, Any]) -> None:
        self.recorder.log_event("ROUND_SETTLEMENT", round_num, "result", settlement_payload)
        clearing_prices: dict[str, float] = settlement_payload.get("clearing_prices", {})
        min_spec_vals: dict[str, float] = settlement_payload.get("buyer_min_spec_vals", {})
        cpr_t = float(stats.get("cpr_t", 1.0))

        new_rows: list[dict[str, Any]] = []
        for b_id, p_clear in clearing_prices.items():
            v_spec = float(min_spec_vals.get(b_id, self.cfg["market_rules"]["v_base"]))
            residual = (float(p_clear) / v_spec) - cpr_t if v_spec > 0 else 0.0
            new_rows.append({
                "buyer_id": b_id,
                "cpr_t": cpr_t,
                "slope_t": stats.get("slope_t", 0.0),
                "dir_t": stats.get("dir_t", 1.0),
                "iur_t": stats.get("iur_t", 0.5),
                "residual": residual,
                "won": bool(settlement_payload.get("won_by_buyer", {}).get(b_id, False)),
            })

        self.state.setdefault("history_log", []).append({
            "round": round_num,
            "cpr_t": cpr_t,
            "clearing_prices": clearing_prices,
            "buyer_min_spec_vals": min_spec_vals,
            "training_rows": new_rows,
        })
        self.recorder.save_state(self.state)
```

### 4.2 `tools/auto_sniffer.py` (Phase 1 Browser Traffic Recorder)

```py
from __future__ import annotations
import json
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from mitmproxy import http

TARGET_IP = os.getenv("CAP_IP", "").strip()
TARGET_PORT = os.getenv("CAP_PORT", "").strip()
ALLOWED_TYPES = tuple(
    t.strip().lower()
    for t in os.getenv("CAP_TYPES", "application/json,text/plain").split(",")
    if t.strip()
)
ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH"}

LOG_FILE = Path("logs") / f"phase1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def _matches_filter(flow: http.HTTPFlow) -> bool:
    if flow.request.method not in ALLOWED_METHODS:
        return False
    if TARGET_PORT and str(flow.request.port) != TARGET_PORT:
        return False
    if TARGET_IP:
        peer_ip = flow.server_conn.peername[0] if (flow.server_conn and flow.server_conn.peername) else ""
        try:
            resolved_ip = socket.gethostbyname(flow.request.pretty_host)
        except OSError:
            resolved_ip = flow.request.pretty_host
        if TARGET_IP not in {peer_ip, resolved_ip, flow.request.pretty_host}:
            return False
    if flow.response and ALLOWED_TYPES:
        ctype = flow.response.headers.get("content-type", "").lower()
        if not any(allowed in ctype for allowed in ALLOWED_TYPES):
            return False
    return True


def response(flow: http.HTTPFlow) -> None:
    if not _matches_filter(flow):
        return
    req_body = flow.request.get_text(strict=False)
    resp_body = flow.response.get_text(strict=False) if flow.response else ""
    try:
        req_parsed = json.loads(req_body) if req_body else None
    except json.JSONDecodeError:
        req_parsed = req_body
    try:
        resp_parsed = json.loads(resp_body) if resp_body else None
    except json.JSONDecodeError:
        resp_parsed = resp_body

    record = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "server_ip": flow.server_conn.peername[0] if (flow.server_conn and flow.server_conn.peername) else None,
        "port": flow.request.port,
        "method": flow.request.method,
        "url": flow.request.pretty_url,
        "content_type": flow.response.headers.get("content-type", "") if flow.response else "",
        "status_code": flow.response.status_code if flow.response else None,
        "request_payload": req_parsed,
        "response_payload": resp_parsed,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
```

### 4.3 `.github/workflows/trade.yml`

```
name: TESA Track 3 Autonomous Market Agent
on:
  workflow_dispatch:
  schedule:
    - cron: "*/5 * * * *"

jobs:
  run-agent:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Restore Telemetry State Branch
        run: |
          git fetch origin telemetry-logs || true
          git checkout origin/telemetry-logs -- logs/ || mkdir -p logs
      - name: Install Dependencies
        run: pip install -r requirements.txt
      - name: Execute Verification Suite
        run: python -m unittest discover -s tests -p "test_*.py"
      - name: Persist Telemetry & State Across Rounds
        if: always()
        run: |
          git config user.name "tesa-agent-bot"
          git config user.email "bot@users.noreply.github.com"
          git checkout -B telemetry-logs
          git add -f logs/
          git commit -m "telemetry: round snapshot $(date -u +%Y-%m-%dT%H:%M:%SZ)" || true
          git push -u origin telemetry-logs --force || true
      - name: Upload Raw Logs Artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: round-telemetry-${{ github.run_number }}
          path: logs/
```

### 4.4 `tests/test_pipeline_e2e.py`

```py
from __future__ import annotations
import copy
import shutil
import unittest
from pathlib import Path
from src.agent_loop import MarketAgentOrchestrator
from src.config import PIPELINE_CONFIG


class TestPipelineEndToEnd(unittest.TestCase):
    def setUp(self) -> None:
        self.match_id = "unit_test_match"
        log_path = Path("logs") / self.match_id
        if log_path.exists():
            shutil.rmtree(log_path)
        self.cfg = copy.deepcopy(PIPELINE_CONFIG)
        self.cfg["api"]["dry_run"] = True

    def test_cold_start_and_guardrail_floor(self) -> None:
        agent = MarketAgentOrchestrator(config=self.cfg, match_id=self.match_id)
        mock_board = {
            "round": 1,
            "total_rounds": 15,
            "num_teams": 40,
            "season_state": "NORMAL",
            "lots": [
                {"id": "L1", "grade": "A", "bean_mm": 6.8, "defect_pct": 2.0, "sacks": 16},
                {"id": "L2", "grade": "C", "bean_mm": 5.8, "defect_pct": 12.0, "sacks": 16},
            ],
            "buyers": [
                {"bot_id": "B_PREMIUM", "min_grade": "A", "max_defect": 5.0, "demand": 10},
                {"bot_id": "B_VOLUME", "min_grade": "C", "max_defect": 15.0, "demand": 20},
            ],
        }
        decision = agent.run_round(mock_board)
        self.assertEqual(decision["stats"]["market_stage"], "PRICE_DISCOVERY")
        self.assertTrue(len(decision["bids"]) >= 1)
        for bid in decision["bids"]:
            v_i = decision["valuations"][bid["lot_id"]]
            self.assertGreaterEqual(bid["price_per_kg"], round(0.81 * v_i, 2))
            self.assertLessEqual(bid["sacks"], decision["stats"]["q_max"])

    def test_custom_lambda_valuation_swap(self) -> None:
        self.cfg["valuation"]["mode"] = "CUSTOM_LAMBDA"
        self.cfg["valuation"]["custom_fn"] = lambda lot, v_base: v_base + 25.0
        agent = MarketAgentOrchestrator(config=self.cfg, match_id=self.match_id)
        decision = agent.run_round({
            "round": 14,
            "total_rounds": 15,
            "lots": [{"lot_id": "L1", "lot_grade": "B", "bean_size": 6.35, "defect_ratio": 0.05, "remaining_sacks": 8}],
            "buyers": [{"buyer_id": "B1", "demand_sacks": 10}],
        })
        self.assertEqual(decision["valuations"]["L1"], 145.0)
        self.assertEqual(decision["stats"]["market_stage"], "END_GAME_SQUEEZE")
        self.assertGreaterEqual(decision["bids"][0]["price_per_kg"], round(0.81 * 145.0, 2))


if __name__ == "__main__":
    unittest.main()
```

---

## 5\. Step-by-Step Build & Camp Calibration Playbook for Local AI

1. **Pre-Camp Implementation (Now):** Have your local AI create every file in Section 1 from the code blocks in Sections 2–4, then run `python -m unittest discover -s tests -p "test_*.py"` and confirm all tests pass with `0` external dependencies beyond `requests`.  
2. **Nov 17 Morning (Formula & API Drop-In):** Edit **only `src/config.py`**:  
   * Paste the official Nov 17 valuation weights into `PIPELINE_CONFIG["valuation"]["weights"]` (or paste the 1-line Excel formula into `default_custom_valuation` and set `"mode": "CUSTOM_LAMBDA"`).  
   * Add any newly revealed JSON field names into `PIPELINE_CONFIG["schema_map"]` and set `"allowed_ip"` / `"allowed_port"`.  
3. **Nov 17 Afternoon (Phase 1 Manual Trading):** Launch `CAP_IP="<server_ip>" CAP_PORT="<port>" mitmdump -p 8888 -s tools/auto_sniffer.py` to record all 6–8 manual rounds into `logs/phase1_*.jsonl` for `OptionalXGBPlugin` warm-start training.  
4. **Nov 18 & Nov 20 (Phases 2 & 3 Autonomous Competition):** Push to GitHub to activate `.github/workflows/trade.yml`; monitor `telemetry-logs` branch snapshots between rounds and tune `alpha_slope`, `beta_demand`, and `gamma_urgency` in `src/config.py`.