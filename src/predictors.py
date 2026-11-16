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
