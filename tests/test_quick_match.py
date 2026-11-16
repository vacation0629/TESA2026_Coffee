from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from dashboard.data_loader import load_dashboard_frames
from dashboard.field_catalog import BUYER_GROUPS, LOT_GROUPS, read_record
from dashboard.matching import allocate_sacks, filter_matches


def lot(lot_id: str, value: float | None, **fields):
    return read_record({"lot_id": lot_id, "remaining_sacks": 1, "v_i": value, **fields}, LOT_GROUPS)


def buyer(buyer_id: str, **fields):
    return read_record({"buyer_id": buyer_id, "demand_sacks": 1, **fields}, BUYER_GROUPS)


class TestQuickMatch(unittest.TestCase):
    def test_requires_observed_values_and_checks_each_filter(self):
        lots = [
            lot("unknown", 50, process="washed"),
            lot("too_dry", 60, humidity=8, process="washed"),
            lot("wrong_process", 70, moisture_pct=10.2, process="dry"),
            lot("eligible", 80, moisture=10.2, process="wet", defect_pct=0.5),
        ]
        selected = [buyer("B", min_humidity=9, max_moisture=11, required_process="washed", max_defect_pct=1)]
        matches = filter_matches(lots, selected)
        self.assertEqual([match.lot_id for match in matches if match.eligible], ["eligible"])
        self.assertEqual(matches[-1].passed, 4)
        self.assertIn("Moisture unavailable", matches[0].missing)
        self.assertIn("Defects unavailable", matches[0].missing)
        self.assertTrue(matches[1].mismatches)

    def test_whole_only_and_max_defects_use_distinct_measurements(self):
        selected = [buyer("B", max_defect=5, bean_shape_req="WHOLE_ONLY")]
        matches = filter_matches([
            lot("A", 80, shape="WHOLE", defect_ratio=0.04),
            lot("B", 90, shape="BROKEN", defect_ratio=0.01),
        ], selected)
        self.assertTrue(matches[0].eligible)
        self.assertFalse(matches[1].eligible)
        self.assertIsNone(selected[0]["max_broken"])

    def test_group_allocation_can_reassign_cheapest_lot_to_strict_buyer(self):
        lots = [lot("cheap", 80, grade="A"), lot("other", 105, grade="B")]
        buyers = [buyer("Flexible", min_grade="B"), buyer("Strict", min_grade="A")]
        matches = filter_matches(lots, buyers)
        allocation = allocate_sacks(matches, buyers, 2)
        self.assertEqual(
            [(row.match.lot_id, row.match.buyer_id, row.sacks) for row in allocation],
            [("cheap", "Strict", 1), ("other", "Flexible", 1)],
        )
        self.assertEqual(sum(row.sacks for row in allocate_sacks(matches, buyers, 1)), 1)

    def test_unknown_cost_appears_last_and_only_fills_remaining_demand(self):
        lots = [lot("Unknown", None), lot("Cheapest", 80), lot("Next", 100)]
        buyers = [buyer("A", required_process="ANY", demand_sacks=3)]
        matches = filter_matches(lots, buyers)
        self.assertEqual([match.lot_id for match in matches], ["Cheapest", "Next", "Unknown"])
        self.assertEqual([row.match.lot_id for row in allocate_sacks(matches, buyers, 2)], ["Cheapest", "Next"])
        self.assertEqual(sum(row.sacks for row in allocate_sacks(matches, buyers, 3)), 3)

    def test_latest_complete_board_is_the_inventory_snapshot(self):
        def poll(sacks, **fields):
            return {"round": 2, "event_type": "BOARD_POLL", "payload": {
                "lots": [{"id": "L", "sacks": sacks, **fields}],
                "buyers": [{"buyer_id": "B", "max_moisture": 11, "demand": 5}],
            }}

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "capture.jsonl"
            events = [poll(8, moisture=9.8), poll(2, humidity=10.5), {
                "round": 2, "event_type": "BOARD_POLL", "payload": {"lots": [{"id": "L", "sacks": 1}]},
            }]
            path.write_text("\n".join(map(json.dumps, events)) + '\n{"event_type":', encoding="utf-8")
            frames = load_dashboard_frames(path.name, folder)
        self.assertEqual(len(frames["lots_df"]), 1)
        latest = frames["lots_df"].iloc[0]
        self.assertEqual(latest["remaining_sacks"], 2)
        self.assertEqual(latest["moisture_pct"], 10.5)
        self.assertIsNone(latest["lot_evaluated_value"])
        self.assertEqual(latest["field_sources"]["moisture_pct"], "humidity")


if __name__ == "__main__":
    unittest.main()
