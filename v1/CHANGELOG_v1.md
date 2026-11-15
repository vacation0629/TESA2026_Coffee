# **Changelog — TESA Top Gun Rally 2026 (Track 3: The Next-Gen Market) — Iteration v1**

This changelog documents the complete `v1.0.0` consolidated pre-camp baseline (`v1_baseline_architecture_and_pricing_engine.md`), merging the competition rules, system variables, agent architecture, statistical market-stage detectors, and pricing engine into a single standalone specification.  
---

# **\[v1.0.0\] \- 2026-11-15**

**Standalone Specification:** `v1_baseline_architecture_and_pricing_engine.md`

## **Added**

* **Competition & Market Rules Baseline (Section 1):** Documented the 3-phase competition schedule and score weights (Nov 17 Manual Web Trading 20%, Nov 18 Autonomous Agent 30%, Nov 20 Final Competition 50%), 6 buyer bots, 90% aggregate market demand cap, 1.5x per-round sack quota cap, and 80% end-of-game central buyback penalty.  
* **Technical Infrastructure Constraints (Section 2):** Documented central server LLM specifications (Qwen 9B family, \~4K token context window, per-team rate limits), REST API (`GET`/`POST` JSON) loop, Git/CI-CD automated execution workflow, and Track 1/Track 2 connectivity scoring requirements.  
* **Complete System Variable Catalog & Mathematical Notation (Section 3):** Cataloged all 25 system variables across Seller Inventory, Buyer Specifications, Market Mechanics, Competitor History, and Technical Limits alongside 8 mathematical runtime tracking symbols using explicit Python data types (`int`, `float`, `string`, `bool`, `list`, `dict`).  
* **Agent Architecture Evaluation & Hybrid Design (Section 4):** Evaluated 3 implementation paradigms (`Hybrid Quantitative-First`, `Pure Rule-Based Heuristics`, and `LLM-Centric`) and locked the 3-layer `Hybrid Quantitative-First + Deterministic Rule-Based Fallback` architecture.  
* **Statistical Market Stage Detection Engine (Section 5):** Defined 5 quantitative indicators (`CPR_t`, `Slope_t`, `CV_t`, `DIR_t`, `IUR_t`) with full mathematical formulas, Python-typed variable definitions, data sources, and step-by-step worked numerical examples.  
* **5-Stage Classification Matrix & Hybrid Pricing Engine (Section 6):** Mapped statistical thresholds to 5 actionable market regimes (`PRICE_DISCOVERY`, `EARLY_DUMPING_WAR`, `HIGH_SEASON_PEAK`, `LATE_SATURATION`, `END_GAME_SQUEEZE`), Minimum-Spec Matching Arbitrage, the `P_target` pricing equation with hard floor (`0.81 * V_i`), and the `< 500 token` LLM prompt interface.  
* **Execution Roadmap & Risk Matrix (Section 7):** Established the 4-phase execution plan and 5-point operational risk and fallback matrix.

---

# **\[Planned / Upcoming\] \- v2.0.0 (Target: 2026-11-17)**

* Integrate the exact official valuation formula (grade, bean size, defect ratio adjustments on the 120.0 THB/kg baseline) distributed during the Nov 17 morning training session.  
* Calibrate buyer bot reserve price ceilings (`buyer_reserve_ceiling`) from Phase 1 manual web trading logs.  
* Implement production Python module (`market_analyzer.py`) with `try-except` timeout fallback and compressed `< 500 token` prompt templates.