#!/usr/bin/env python3
"""
Semi-Random Walk Market Simulator (6 Rounds, 3 Coffee Types, 0.9 Demand Constraint)

Pricing Formula:
    P_new = 0.3 * P_previous + 0.7 * P_shock
    where P_shock = Base_Price * (1.0 + Uniform(-0.20, +0.20))
    At t=0: P_previous = Base_Price

Supply & Demand Constraint:
    - Initial Supply: 30 sacks across 3 lots (10 sacks each, 60 kg/sack = 1,800 kg total)
    - 0.9 Demand Rule: Total market demand across 6 rounds = 0.9 * 30 = 27 sacks
    - Unsold Supply (exactly 10% = 3 sacks, 1 sack per lot) liquidated via Central Buyback at 80% (0.80 * V_i)
"""

from __future__ import annotations
import json
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


def simulate_semirandom_market(seed: int = 42) -> dict[str, Any]:
    random.seed(seed)

    # 1. Base Lots Setup (10 sacks each = 30 sacks total)
    lots_config = {
        "LOT_COMMERCIAL_DRY": {
            "lot_id": "LOT_COMMERCIAL_DRY",
            "process": "dry",
            "moisture": 12.6,
            "ripeness": 76.0,
            "bean_shape": "BROKEN",
            "broken_ratio": 0.16,
            "baseline_v": 80.0,
            "initial_sacks": 10,
            "bean_size": 5.8,
            "defect_ratio": 0.16,
            "lot_grade": "C",
        },
        "LOT_STANDARD_DRY": {
            "lot_id": "LOT_STANDARD_DRY",
            "process": "dry",
            "moisture": 11.2,
            "ripeness": 87.0,
            "bean_shape": "WHOLE",
            "broken_ratio": 0.04,
            "baseline_v": 100.0,
            "initial_sacks": 10,
            "bean_size": 6.35,
            "defect_ratio": 0.04,
            "lot_grade": "B",
        },
        "LOT_SPECIALTY_WET": {
            "lot_id": "LOT_SPECIALTY_WET",
            "process": "wet",
            "moisture": 10.4,
            "ripeness": 97.0,
            "bean_shape": "WHOLE",
            "broken_ratio": 0.01,
            "baseline_v": 120.0,
            "initial_sacks": 10,
            "bean_size": 7.1,
            "defect_ratio": 0.01,
            "lot_grade": "A",
        },
    }

    total_supply_sacks = sum(l["initial_sacks"] for l in lots_config.values())  # 30 sacks
    total_demand_sacks = int(round(total_supply_sacks * 0.90))  # 27 sacks (0.9 demand rule)
    total_rounds = 6
    kg_per_sack = 60.0

    # Demand schedule across 6 rounds summing to exactly 27 sacks:
    # B1 (Specialty): 1 sack per round = 6
    # B2 (Cafe Chain): 1 sack in R2, R4, R6 = 3 (buys Specialty or Standard)
    # B3 (Exporter Hub): 1 sack per round = 6 (buys Standard)
    # B4 (Commercial Can): 1 sack per round = 6 (buys Commercial)
    # B5 (Instant Factory): 1 sack in R1, R3, R5, R6, R2, R4 summing to 6 sacks total
    # Total demand per round: R1: 4, R2: 5, R3: 4, R4: 5, R5: 4, R6: 5 -> 27 sacks total
    buyer_schedule = [
        {"B1": 1, "B2": 0, "B3": 1, "B4": 1, "B5": 1},  # R1: 4 sacks
        {"B1": 1, "B2": 1, "B3": 1, "B4": 1, "B5": 1},  # R2: 5 sacks
        {"B1": 1, "B2": 0, "B3": 1, "B4": 1, "B5": 1},  # R3: 4 sacks
        {"B1": 1, "B2": 1, "B3": 1, "B4": 1, "B5": 1},  # R4: 5 sacks
        {"B1": 1, "B2": 0, "B3": 1, "B4": 1, "B5": 1},  # R5: 4 sacks
        {"B1": 1, "B2": 1, "B3": 1, "B4": 1, "B5": 1},  # R6: 5 sacks
    ]

    buyers_specs = {
        "B1": {"buyer_id": "B1_SPECIALTY_ROASTER", "required_process": "wet", "max_moisture": 11.0, "min_ripeness": 90.0, "shape_requirement": "WHOLE_ONLY", "target_value": 120.0, "min_grade": "A"},
        "B2": {"buyer_id": "B2_CAFE_CHAIN", "required_process": "ANY", "max_moisture": 12.0, "min_ripeness": 80.0, "shape_requirement": "WHOLE_ONLY", "target_value": 110.0, "min_grade": "B"},
        "B3": {"buyer_id": "B3_EXPORTER_HUB", "required_process": "dry", "max_moisture": 12.0, "min_ripeness": 80.0, "shape_requirement": "ANY", "target_value": 100.0, "min_grade": "B"},
        "B4": {"buyer_id": "B4_COMMERCIAL_CAN", "required_process": "dry", "max_moisture": 13.0, "min_ripeness": 70.0, "shape_requirement": "ANY", "target_value": 80.0, "min_grade": "C"},
        "B5": {"buyer_id": "B5_INSTANT_FACTORY", "required_process": "ANY", "max_moisture": 13.5, "min_ripeness": 70.0, "shape_requirement": "ANY", "target_value": 80.0, "min_grade": "C"},
    }

    # State tracking
    remaining_sacks = {k: v["initial_sacks"] for k, v in lots_config.items()}
    prev_prices = {k: v["baseline_v"] for k, v in lots_config.items()}

    records: list[dict[str, Any]] = []
    sniffer_records: list[dict[str, Any]] = []
    round_log: list[dict[str, Any]] = []

    base_time = datetime.now(timezone.utc) - timedelta(minutes=35)
    stages = [
        "PRICE_DISCOVERY",
        "PRICE_DISCOVERY",
        "MID_GAME_ACCUMULATION",
        "MID_GAME_ACCUMULATION",
        "END_GAME_SQUEEZE",
        "END_GAME_SQUEEZE",
    ]

    total_auction_revenue = 0.0
    total_auction_sacks_sold = 0
    total_intrinsic_value = sum(l["initial_sacks"] * kg_per_sack * l["baseline_v"] for l in lots_config.values())

    for r in range(1, total_rounds + 1):
        r_time = base_time + timedelta(minutes=5 * (r - 1))
        r_rem = total_rounds - r
        stage = stages[r - 1]
        sched = buyer_schedule[r - 1]
        r_demand = sum(sched.values())

        # 1. Calculate Semi-Random Prices per Lot
        # Formula: P_new = 0.3 * P_prev + 0.7 * (Base * (1 + Uniform(-0.2, 0.2)))
        current_market_prices = {}
        shock_prices = {}
        for lot_id, ldata in lots_config.items():
            base_v = ldata["baseline_v"]
            prev_p = prev_prices[lot_id]
            rand_factor = random.uniform(-0.20, 0.20)
            p_shock = base_v * (1.0 + rand_factor)
            p_new = round(0.30 * prev_p + 0.70 * p_shock, 2)
            current_market_prices[lot_id] = p_new
            shock_prices[lot_id] = round(p_shock, 2)
            prev_prices[lot_id] = p_new

        # 2. Build Board Data
        board_lots = []
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

        board_buyers = []
        for b_key, b_sacks in sched.items():
            b_info = buyers_specs[b_key]
            board_buyers.append({
                "buyer_id": b_info["buyer_id"],
                "required_process": b_info["required_process"],
                "max_moisture": b_info["max_moisture"],
                "min_ripeness": b_info["min_ripeness"],
                "bean_shape_req": b_info["shape_requirement"],
                "target_value": b_info["target_value"],
                "min_grade": b_info["min_grade"],
                "demand_sacks": b_sacks,
            })

        # Save BOARD_POLL
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

        # 3. Agent Decides Bids
        # Anti-dumping quota cap: 1.5 * (initial / rounds) = 1.5 * (30/6) = 7 sacks max
        max_quota_round = 7
        bid_time = r_time + timedelta(seconds=2)
        bids = []
        offered_this_round = 0

        # Physical matching with Minimum-Spec Arbitrage (Ascending V_i)
        # Low-spec buyers get lowest-value qualifying lot, preserving premium lots for high-spec buyers
        sorted_lot_ids = sorted(lots_config.keys(), key=lambda lid: lots_config[lid]["baseline_v"])
        for b in board_buyers:
            b_demand = b["demand_sacks"]
            if b_demand <= 0:
                continue

            for lot_id in sorted_lot_ids:
                ldata = lots_config[lot_id]
                if remaining_sacks[lot_id] <= 0 or offered_this_round >= max_quota_round:
                    continue

                proc_ok = (b["required_process"] in ["ANY", ldata["process"]])
                moist_ok = (b["max_moisture"] is None or ldata["moisture"] <= b["max_moisture"])
                ripe_ok = (b["min_ripeness"] is None or ldata["ripeness"] >= b["min_ripeness"])
                shape_ok = (b["bean_shape_req"] != "WHOLE_ONLY" or ldata["bean_shape"] == "WHOLE")

                if proc_ok and moist_ok and ripe_ok and shape_ok:
                    v_i = ldata["baseline_v"]
                    p_market = current_market_prices[lot_id]
                    p_bid = max(round(p_market * 1.01, 2), round(0.81 * v_i, 2))
                    sacks_to_bid = min(b_demand, remaining_sacks[lot_id], max_quota_round - offered_this_round)
                    if sacks_to_bid > 0:
                        bids.append({
                            "lot_id": lot_id,
                            "buyer_id": b["buyer_id"],
                            "sacks": sacks_to_bid,
                            "price_per_kg": p_bid,
                        })
                        offered_this_round += sacks_to_bid
                        remaining_sacks[lot_id] -= sacks_to_bid
                        b_demand -= sacks_to_bid
                        if b_demand <= 0:
                            break

        # Save DECISION_AND_BID
        cpr_t = round(sum(current_market_prices.values()) / sum(l["baseline_v"] for l in lots_config.values()), 3)
        total_rem = sum(remaining_sacks.values())
        iur_t = round(total_rem / max(1, r_rem * 5), 3)

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
                    "q_max": max_quota_round,
                    "cpr_t": cpr_t,
                    "slope_t": 0.02,
                    "cv_t": 0.06,
                    "dir_t": round(r_demand / max(1, offered_this_round), 2),
                    "iur_t": iur_t,
                    "season_state": "NORMAL",
                    "market_stage": stage,
                },
                "valuations": {k: v["baseline_v"] for k, v in lots_config.items()},
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

        # 4. Settlement
        settle_time = r_time + timedelta(seconds=15)
        clearing_prices = {}
        allocations = []
        round_revenue = 0.0
        round_sacks_sold = 0

        for b in bids:
            lid = b["lot_id"]
            p_clear = current_market_prices[lid]
            clearing_prices[lid] = p_clear
            sacks_sold = b["sacks"]
            round_sacks_sold += sacks_sold
            
            lot_rev = sacks_sold * kg_per_sack * p_clear
            round_revenue += lot_rev
            total_auction_revenue += lot_rev
            total_auction_sacks_sold += sacks_sold

            allocations.append({
                "lot_id": lid,
                "buyer_id": b["buyer_id"],
                "clearing_price": p_clear,
                "sacks_allocated": sacks_sold,
                "won": True,
            })

            round_log.append({
                "round": r,
                "stage": stage,
                "lot_id": lid,
                "buyer_id": b["buyer_id"],
                "base_v": lots_config[lid]["baseline_v"],
                "p_prev": prev_prices[lid],
                "p_shock": shock_prices[lid],
                "p_clear": p_clear,
                "sacks_sold": sacks_sold,
                "kg_sold": sacks_sold * kg_per_sack,
                "lot_revenue": lot_rev,
                "rem_after": remaining_sacks[lid],
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
                    "round_cpr": cpr_t,
                    "round_volume": round_sacks_sold,
                    "round_revenue": round_revenue,
                },
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
                "round_revenue": round_revenue,
            },
        })

    # 5. End-Game Buyback Settlement (Round 6 Closing)
    total_unsold_sacks = sum(remaining_sacks.values())
    total_buyback_revenue = 0.0
    buyback_details = []

    for lot_id, rem_cnt in remaining_sacks.items():
        if rem_cnt > 0:
            v_i = lots_config[lot_id]["baseline_v"]
            buyback_rate = 0.80 * v_i
            buyback_rev = rem_cnt * kg_per_sack * buyback_rate
            total_buyback_revenue += buyback_rev
            buyback_details.append({
                "lot_id": lot_id,
                "unsold_sacks": rem_cnt,
                "kg": rem_cnt * kg_per_sack,
                "base_v": v_i,
                "buyback_rate_per_kg": buyback_rate,
                "buyback_revenue": buyback_rev,
            })

    total_gross_revenue = total_auction_revenue + total_buyback_revenue
    net_profit = total_gross_revenue - total_intrinsic_value
    net_margin_pct = (net_profit / total_intrinsic_value) * 100.0 if total_intrinsic_value > 0 else 0.0

    summary = {
        "total_initial_sacks": total_supply_sacks,
        "total_initial_kg": total_supply_sacks * kg_per_sack,
        "total_demand_sacks": total_demand_sacks,
        "auction_sacks_sold": total_auction_sacks_sold,
        "unsold_sacks": total_unsold_sacks,
        "unsold_pct": (total_unsold_sacks / total_supply_sacks) * 100.0,
        "total_intrinsic_value_thb": total_intrinsic_value,
        "auction_revenue_thb": total_auction_revenue,
        "buyback_revenue_thb": total_buyback_revenue,
        "gross_revenue_thb": total_gross_revenue,
        "net_profit_thb": net_profit,
        "net_margin_pct": net_margin_pct,
        "round_log": round_log,
        "buyback_details": buyback_details,
    }

    # 6. Save JSONL Files for Dashboard & Listener
    target_dirs = [
        Path("G:/Antigravity Projects/Coffee2026/logs/mock_semirandom_6rounds"),
        Path("G:/Antigravity Projects/TESA2026_Coffee/logs/mock_semirandom_6rounds"),
        Path("G:/Antigravity Projects/Coffee2026/listener/logs"),
        Path("G:/Antigravity Projects/TESA2026_Coffee/listener/logs"),
    ]
    for d in target_dirs:
        d.mkdir(parents=True, exist_ok=True)

    for p in [
        Path("G:/Antigravity Projects/Coffee2026/logs/mock_semirandom_6rounds/raw_events.jsonl"),
        Path("G:/Antigravity Projects/TESA2026_Coffee/logs/mock_semirandom_6rounds/raw_events.jsonl"),
    ]:
        with open(p, "w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")

    for p in [
        Path("G:/Antigravity Projects/Coffee2026/listener/logs/mock_semirandom_6rounds.jsonl"),
        Path("G:/Antigravity Projects/TESA2026_Coffee/listener/logs/mock_semirandom_6rounds.jsonl"),
    ]:
        with open(p, "w", encoding="utf-8") as f:
            for rec in sniffer_records:
                f.write(json.dumps(rec) + "\n")

    return summary


def print_financial_statement(summary: dict[str, Any]) -> None:
    print("\n" + "=" * 78)
    print("      TESA 2026 TRACK 3 — SEMI-RANDOM WALK SIMULATION SUMMARY")
    print("=" * 78)
    print(f"Total Initial Supply   : {summary['total_initial_sacks']} sacks ({summary['total_initial_kg']:,.0f} kg across 3 lots)")
    print(f"0.9 Market Demand Cap  : {summary['total_demand_sacks']} sacks (exactly 90.0% of total supply)")
    print(f"Auction Sacks Cleared  : {summary['auction_sacks_sold']} sacks ({summary['auction_sacks_sold']*60:,.0f} kg)")
    print(f"Unsold Sacks Remaining : {summary['unsold_sacks']} sacks ({summary['unsold_pct']:.1f}% -> Central 80% Buyback)")
    print("-" * 78)
    print(" ROUND-BY-ROUND EXECUTION LOG:")
    print("-" * 78)
    print(f"{'R':<2} | {'Lot ID':<20} | {'Base V':<6} | {'P_Shock':<7} | {'P_Clear':<7} | {'Sacks':<5} | {'Revenue (THB)':<13}")
    print("-" * 78)
    for row in summary["round_log"]:
        print(f"R{row['round']} | {row['lot_id']:<20} | {row['base_v']:>6.1f} | {row['p_shock']:>7.2f} | {row['p_clear']:>7.2f} | {row['sacks_sold']:>5} | {row['lot_revenue']:>13,.2f}")
    
    print("-" * 78)
    print(" END-GAME 80% CENTRAL BUYBACK (ROUND 6 CLOSING):")
    print("-" * 78)
    for bb in summary["buyback_details"]:
        print(f"  • {bb['lot_id']:<20}: {bb['unsold_sacks']} sacks ({bb['kg']:.0f} kg) @ {bb['buyback_rate_per_kg']:.2f} THB/kg = {bb['buyback_revenue']:,.2f} THB")

    print("=" * 78)
    print(" FINANCIAL STATEMENT & PROFIT AUDIT:")
    print("=" * 78)
    print(f"  1. Gross Auction Revenue (Sold to Buyers) : {summary['auction_revenue_thb']:>14,.2f} THB")
    print(f"  2. Buyback Settlement (80% Penalty)       : {summary['buyback_revenue_thb']:>14,.2f} THB")
    print(f"  -------------------------------------------------------------")
    print(f"  Total Realized Gross Revenue              : {summary['gross_revenue_thb']:>14,.2f} THB")
    print(f"  Intrinsic Lot Cost Basis (Evaluated V_i)  : {summary['total_intrinsic_value_thb']:>14,.2f} THB")
    print(f"  -------------------------------------------------------------")
    profit_sign = "+" if summary['net_profit_thb'] >= 0 else ""
    print(f"  NET EARNINGS / PROFIT                     : {profit_sign}{summary['net_profit_thb']:>14,.2f} THB")
    print(f"  PROFIT MARGIN OVER V_i                    : {profit_sign}{summary['net_margin_pct']:>13.2f} %")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    summary = simulate_semirandom_market()
    print_financial_statement(summary)
