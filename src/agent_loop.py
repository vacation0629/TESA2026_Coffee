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
