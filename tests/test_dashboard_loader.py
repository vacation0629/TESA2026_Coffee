from __future__ import annotations
import copy
import shutil
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dashboard.data_loader import load_dashboard_frames
from src.agent_loop import MarketAgentOrchestrator
from src.config import PIPELINE_CONFIG


class TestDashboardDataLoader(unittest.TestCase):
    def setUp(self) -> None:
        self.match_id = "dashboard_test_match"
        log_dir = Path("logs") / self.match_id
        if log_dir.exists():
            shutil.rmtree(log_dir)
        cfg = copy.deepcopy(PIPELINE_CONFIG)
        cfg["api"]["dry_run"] = True

        agent = MarketAgentOrchestrator(config=cfg, match_id=self.match_id)
        decision = agent.run_round({
            "round": 1,
            "total_rounds": 15,
            "num_teams": 40,
            "lots": [
                {"id": "L1", "grade": "A", "bean_mm": 6.8, "defect_pct": 2.0, "humidity": 10.2, "process": "washed", "sacks": 12},
                {"id": "L2", "grade": "C", "bean_mm": 5.8, "defect_pct": 11.0, "humidity": 12.5, "process": "dry", "sacks": 12},
            ],
            "buyers": [
                {"bot_id": "B_SPECIALTY", "min_grade": "A", "required_process": "washed", "demand": 8},
                {"bot_id": "B_FACTORY", "min_grade": "C", "demand": 15},
            ],
        })
        agent.record_settlement(
            round_num=1,
            settlement_payload={
                "clearing_prices": {"B_SPECIALTY": 142.0, "B_FACTORY": 118.0},
                "buyer_min_spec_vals": {"B_SPECIALTY": 132.0, "B_FACTORY": 108.0},
                "won_by_buyer": {"B_SPECIALTY": True, "B_FACTORY": True},
            },
            stats=decision["stats"],
        )

    def tearDown(self) -> None:
        log_dir = Path("logs") / self.match_id
        if log_dir.exists():
            shutil.rmtree(log_dir)

    def test_polymorphic_frames_populated(self) -> None:
        frames = load_dashboard_frames(self.match_id, log_root="logs")
        self.assertEqual(len(frames["rounds_df"]), 1)
        self.assertEqual(set(frames["lots_df"]["lot_grade"]), {"A", "C"})
        self.assertEqual(set(frames["buyers_df"]["buyer_id"]), {"B_SPECIALTY", "B_FACTORY"})
        self.assertIn("margin_over_vi_pct", frames["bids_df"].columns)
        self.assertIn("humidity_band", frames["bids_df"].columns)


if __name__ == "__main__":
    unittest.main()
