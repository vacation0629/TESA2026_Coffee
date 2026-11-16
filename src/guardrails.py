from __future__ import annotations
from typing import Any


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
