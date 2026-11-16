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

    # 3 Coffee Types with baselines 80, 100, 120 THB/kg
    lots_config = {
        "LOT_C_COMMERCIAL": {
            "lot_id": "LOT_C_COMMERCIAL",
            "lot_grade": "C",
            "baseline_v": 80.0,
            "bean_size": 5.8,
            "defect_ratio": 0.12,
            "humidity": 10.8,
            "process": "dry",
            "initial_sacks": 12,
        },
        "LOT_B_PREMIUM": {
            "lot_id": "LOT_B_PREMIUM",
            "lot_grade": "B",
            "baseline_v": 100.0,
            "bean_size": 6.35,
            "defect_ratio": 0.05,
            "humidity": 10.2,
            "process": "washed",
            "initial_sacks": 12,
        },
        "LOT_A_SPECIALTY": {
            "lot_id": "LOT_A_SPECIALTY",
            "lot_grade": "A",
            "baseline_v": 120.0,
            "bean_size": 7.1,
            "defect_ratio": 0.02,
            "humidity": 9.9,
            "process": "honey",
            "initial_sacks": 12,
        },
    }

    buyers_config = [
        {"buyer_id": "B1_SPECIALTY_ROASTER", "min_grade": "A", "max_defect": 0.03, "demand_sacks": 6, "min_spec_v": 120.0},
        {"buyer_id": "B2_CAFE_CHAIN", "min_grade": "B", "max_defect": 0.06, "demand_sacks": 8, "min_spec_v": 100.0},
        {"buyer_id": "B3_EXPORTER_HUB", "min_grade": "B", "max_defect": 0.08, "demand_sacks": 10, "min_spec_v": 100.0},
        {"buyer_id": "B4_COMMERCIAL_CAN", "min_grade": "C", "max_defect": 0.15, "demand_sacks": 14, "min_spec_v": 80.0},
        {"buyer_id": "B5_INSTANT_FACTORY", "min_grade": "C", "max_defect": 0.15, "demand_sacks": 16, "min_spec_v": 80.0},
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
                "lot_grade": ldata["lot_grade"],
                "bean_size": ldata["bean_size"],
                "defect_ratio": ldata["defect_ratio"],
                "humidity": ldata["humidity"],
                "process": ldata["process"],
                "remaining_sacks": remaining_sacks[lot_id],
            })
            # Valuation with slight market variation
            valuations[lot_id] = round(ldata["baseline_v"] * (1.0 + 0.01 * (r - 1)), 2)

        board_buyers = []
        for b in buyers_config:
            board_buyers.append({
                "buyer_id": b["buyer_id"],
                "min_grade": b["min_grade"],
                "max_defect": b["max_defect"],
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

        # Sniffer equivalent representation
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
        # Agent bids on matching lots
        for lot_id, ldata in lots_config.items():
            v_i = valuations[lot_id]
            # Sacks to offer: quota clamped
            offer_sacks = min(2, remaining_sacks[lot_id])
            if offer_sacks > 0:
                # Price based on stage and cpr
                bid_price = round(v_i * cpr * 1.02, 2)
                # Hard floor check
                bid_price = max(bid_price, round(0.81 * v_i, 2))
                
                # Assign to matching buyer
                for b in buyers_config:
                    if ldata["lot_grade"] <= b["min_grade"] and ldata["defect_ratio"] <= b["max_defect"]:
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
            # Simulating realistic winning clearing price
            clear_p = round(b["price_per_kg"] * 0.99, 2)
            clearing_prices[lid] = clear_p
            # Deduct sacks if won
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
                "buyer_min_spec_v": {
                    "B1_SPECIALTY_ROASTER": 120.0,
                    "B2_CAFE_CHAIN": 100.0,
                    "B3_EXPORTER_HUB": 100.0,
                    "B4_COMMERCIAL_CAN": 80.0,
                    "B5_INSTANT_FACTORY": 80.0,
                },
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
