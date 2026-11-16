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
        if r_rem <= 2 or (current_round > 2 and iur_t > 0.70):
            return "END_GAME_SQUEEZE"
        if current_round <= 2 or not has_history:
            return "PRICE_DISCOVERY"
        if cpr_t < 0.98 and slope_t < 0:
            return "EARLY_DUMPING_WAR"
        if dir_t > 1.15 or "HIGH" in season_state.upper():
            return "HIGH_SEASON_PEAK"
        if dir_t < 0.85 or "LATE" in season_state.upper():
            return "LATE_SATURATION"
        return "HIGH_SEASON_PEAK" if slope_t > 0 else "LATE_SATURATION"
