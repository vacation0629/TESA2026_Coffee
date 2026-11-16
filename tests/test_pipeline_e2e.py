from __future__ import annotations
import copy
import shutil
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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
