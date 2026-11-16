import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

def generate_mock_datastream():
    target_dirs = [
        Path("G:/Antigravity Projects/Coffee2026/logs/mock_stream_6rounds"),
        Path("G:/Antigravity Projects/TESA2026_Coffee/logs/mock_stream_6rounds"),
        Path("G:/Antigravity Projects/Coffee2026/listener/logs"),
        Path("G:/Antigravity Projects/TESA2026_Coffee/listener/logs"),
    ]
    for d in target_dirs:
        d.mkdir(parents=True, exist_ok=True)

    # 3 Coffee Types defined by physical parameters (Moisture, Process, Ripeness, Shape, Value)
    # Baseline values: 80, 100, 120 THB/kg
    lots_config = {
        "LOT_COMMERCIAL_DRY": {
            "lot_id": "LOT_COMMERCIAL_DRY",
            "process": "dry",
            "moisture": 12.6,
            "ripeness": 76.0,
            "bean_shape": "BROKEN",
            "broken_ratio": 0.16,
            "baseline_v": 80.0,
            "bean_size": 5.8,
            "defect_ratio": 0.16,
            "lot_grade": "C",
            "initial_sacks": 12,
        },
        "LOT_STANDARD_DRY": {
            "lot_id": "LOT_STANDARD_DRY",
            "process": "dry",
            "moisture": 11.2,
            "ripeness": 87.0,
            "bean_shape": "WHOLE",
            "broken_ratio": 0.04,
            "baseline_v": 100.0,
            "bean_size": 6.35,
            "defect_ratio": 0.04,
            "lot_grade": "B",
            "initial_sacks": 12,
        },
        "LOT_SPECIALTY_WET": {
            "lot_id": "LOT_SPECIALTY_WET",
            "process": "wet",
            "moisture": 10.4,
            "ripeness": 97.0,
            "bean_shape": "WHOLE",
            "broken_ratio": 0.01,
            "baseline_v": 120.0,
            "bean_size": 7.1,
            "defect_ratio": 0.01,
            "lot_grade": "A",
            "initial_sacks": 12,
        },
    }

    # Buyer Bots with physical parameter requirements
    buyers_config = [
        {
            "buyer_id": "B1_SPECIALTY_ROASTER",
            "required_process": "wet",
            "max_moisture": 11.0,
            "min_ripeness": 90.0,
            "bean_shape_req": "WHOLE_ONLY",
            "max_broken": 0.03,
            "target_value": 120.0,
            "min_grade": "A",
            "demand_sacks": 6,
        },
        {
            "buyer_id": "B2_CAFE_CHAIN",
            "required_process": "ANY",
            "max_moisture": 12.0,
            "min_ripeness": 80.0,
            "bean_shape_req": "WHOLE_ONLY",
            "max_broken": 0.06,
            "target_value": 100.0,
            "min_grade": "B",
            "demand_sacks": 8,
        },
        {
            "buyer_id": "B3_EXPORTER_HUB",
            "required_process": "dry",
            "max_moisture": 12.0,
            "min_ripeness": 80.0,
            "bean_shape_req": "ANY",
            "max_broken": 0.08,
            "target_value": 100.0,
            "min_grade": "B",
            "demand_sacks": 10,
        },
        {
            "buyer_id": "B4_COMMERCIAL_CAN",
            "required_process": "dry",
            "max_moisture": 13.0,
            "min_ripeness": 70.0,
            "bean_shape_req": "ANY",
            "max_broken": 0.20,
            "target_value": 80.0,
            "min_grade": "C",
            "demand_sacks": 14,
        },
        {
            "buyer_id": "B5_INSTANT_FACTORY",
            "required_process": "ANY",
            "max_moisture": 13.5,
            "min_ripeness": 70.0,
            "bean_shape_req": "ANY",
            "max_broken": 0.25,
            "target_value": 80.0,
            "min_grade": "C",
            "demand_sacks": 16,
        },
    ]

    total_rounds = 6
    remaining_sacks = {k: v["initial_sacks"] for k, v in lots_config.items()}
    records = []
    sniffer_records = []
    base_time = datetime.now(timezone.utc) - timedelta(minutes=30)

    stages = [
        "PRICE_DISCOVERY",
        "PRICE_DISCOVERY",
        "MID_GAME_ACCUMULATION",
        "MID_GAME_ACCUMULATION",
        "END_GAME_SQUEEZE",
        "END_GAME_SQUEEZE",
    ]

    # Dynamic pricing factors over 6 rounds
    cpr_trend = [0.94, 0.98, 1.03, 1.08, 1.15, 1.22]
    dir_trend = [0.82, 0.95, 1.12, 1.25, 1.40, 1.65]

    for r in range(1, total_rounds + 1):
        r_time = base_time + timedelta(minutes=5 * (r - 1))
        stage = stages[r - 1]
        cpr = cpr_trend[r - 1]
        dir_t = dir_trend[r - 1]
        r_rem = total_rounds - r

        # 1. BOARD_POLL Event
        board_lots = []
        valuations = {}
        for lot_id, ldata in lots_config.items():
            board_lots.append({
                "lot_id": lot_id,
                "process": ldata["process"],
                "moisture": ldata["moisture"],
                "ripeness": ldata["ripeness"],
                "bean_shape": ldata["bean_shape"],
                "broken_ratio": ldata["broken_ratio"],
                "bean_size": ldata["bean_size"],
                "defect_ratio": ldata["defect_ratio"],
                "lot_grade": ldata["lot_grade"],
                "baseline_v": ldata["baseline_v"],
                "remaining_sacks": remaining_sacks[lot_id],
            })
            valuations[lot_id] = round(ldata["baseline_v"] * (1.0 + 0.01 * (r - 1)), 2)

        board_buyers = []
        for b in buyers_config:
            board_buyers.append({
                "buyer_id": b["buyer_id"],
                "required_process": b["required_process"],
                "max_moisture": b["max_moisture"],
                "min_ripeness": b["min_ripeness"],
                "bean_shape_req": b["bean_shape_req"],
                "max_broken": b["max_broken"],
                "target_value": b["target_value"],
                "min_grade": b["min_grade"],
                "demand_sacks": max(1, b["demand_sacks"] - (r - 1)),
            })

        board_poll_ev = {
            "ts_utc": r_time.isoformat(),
            "round": r,
            "event_type": "BOARD_POLL",
            "endpoint": "board",
            "status_code": 200,
            "payload": {
                "round": r,
                "total_rounds": total_rounds,
                "lots": board_lots,
                "buyers": board_buyers,
            },
        }
        records.append(board_poll_ev)

        sniffer_records.append({
            "ts_utc": r_time.isoformat(),
            "protocol": "HTTP",
            "method": "GET",
            "path": f"/api/v1/board?round={r}",
            "status_code": 200,
            "request_payload": None,
            "response_payload": board_poll_ev["payload"],
        })

        # 2. DECISION_AND_BID Event
        bid_time = r_time + timedelta(seconds=2)
        bids = []
        for lot_id, ldata in lots_config.items():
            v_i = valuations[lot_id]
            offer_sacks = min(2, remaining_sacks[lot_id])
            if offer_sacks > 0:
                bid_price = round(v_i * cpr * 1.02, 2)
                bid_price = max(bid_price, round(0.81 * v_i, 2))
                
                # Minimum-Spec physical matching
                for b in buyers_config:
                    proc_ok = (b["required_process"] in ["ANY", ldata["process"]])
                    moist_ok = (b["max_moisture"] is None or ldata["moisture"] <= b["max_moisture"])
                    ripe_ok = (b["min_ripeness"] is None or ldata["ripeness"] >= b["min_ripeness"])
                    shape_ok = (b["bean_shape_req"] != "WHOLE_ONLY" or ldata["bean_shape"] == "WHOLE")
                    
                    if proc_ok and moist_ok and ripe_ok and shape_ok:
                        bids.append({
                            "lot_id": lot_id,
                            "buyer_id": b["buyer_id"],
                            "sacks": offer_sacks,
                            "price_per_kg": bid_price,
                        })
                        break

        total_rem = sum(remaining_sacks.values())
        iur_t = round(total_rem / max(1, r_rem * 6), 3)

        decision_ev = {
            "ts_utc": bid_time.isoformat(),
            "round": r,
            "event_type": "DECISION_AND_BID",
            "endpoint": "bid",
            "status_code": 200,
            "payload": {
                "round": r,
                "stats": {
                    "round": r,
                    "total_rounds": total_rounds,
                    "r_rem": r_rem,
                    "q_max": 3,
                    "cpr_t": cpr,
                    "slope_t": 0.04,
                    "cv_t": 0.08,
                    "dir_t": dir_t,
                    "iur_t": iur_t,
                    "season_state": "NORMAL",
                    "market_stage": stage,
                },
                "valuations": valuations,
                "bids": bids,
            },
        }
        records.append(decision_ev)

        sniffer_records.append({
            "ts_utc": bid_time.isoformat(),
            "protocol": "HTTP",
            "method": "POST",
            "path": f"/api/v1/bid",
            "status_code": 200,
            "request_payload": bids,
            "response_payload": {"status": "SUCCESS", "bids_received": len(bids)},
        })

        # 3. ROUND_SETTLEMENT Event
        settle_time = r_time + timedelta(seconds=15)
        clearing_prices = {}
        allocations = []
        for b in bids:
            lid = b["lot_id"]
            clear_p = round(b["price_per_kg"] * 0.99, 2)
            clearing_prices[lid] = clear_p
            sacks_sold = min(b["sacks"], remaining_sacks[lid])
            remaining_sacks[lid] -= sacks_sold
            allocations.append({
                "lot_id": lid,
                "buyer_id": b["buyer_id"],
                "clearing_price": clear_p,
                "sacks_allocated": sacks_sold,
                "won": True,
            })

        settle_ev = {
            "ts_utc": settle_time.isoformat(),
            "round": r,
            "event_type": "ROUND_SETTLEMENT",
            "endpoint": "settlement",
            "status_code": 200,
            "payload": {
                "round": r,
                "clearing_prices": clearing_prices,
                "allocations": allocations,
                "market_stats": {
                    "round_cpr": cpr,
                    "round_volume": sum(a["sacks_allocated"] for a in allocations),
                },
                "buyer_target_value": {b["buyer_id"]: b["target_value"] for b in buyers_config},
                "won_by_buyer": {b["buyer_id"]: True for b in bids},
            },
        }
        records.append(settle_ev)

        sniffer_records.append({
            "ts_utc": settle_time.isoformat(),
            "protocol": "WEBSOCKET",
            "direction": "RECV",
            "payload": {
                "type": "SETTLEMENT",
                "round": r,
                "clearing_prices": clearing_prices,
            },
        })

    # Write files
    for p in [
        Path("G:/Antigravity Projects/Coffee2026/logs/mock_stream_6rounds/raw_events.jsonl"),
        Path("G:/Antigravity Projects/TESA2026_Coffee/logs/mock_stream_6rounds/raw_events.jsonl"),
    ]:
        with open(p, "w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")
        print(f"Wrote {len(records)} events to {p}")

    # Write sniffer capture format
    for p in [
        Path("G:/Antigravity Projects/Coffee2026/listener/logs/mock_stream_6rounds.jsonl"),
        Path("G:/Antigravity Projects/TESA2026_Coffee/listener/logs/mock_stream_6rounds.jsonl"),
    ]:
        with open(p, "w", encoding="utf-8") as f:
            for rec in sniffer_records:
                f.write(json.dumps(rec) + "\n")
        print(f"Wrote {len(sniffer_records)} sniffer records to {p}")

if __name__ == "__main__":
    generate_mock_datastream()
