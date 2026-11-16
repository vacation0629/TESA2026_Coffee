# **Milestone & Session Continuity Tracker — TESA Top Gun Rally 2026 (Track 3: The Next-Gen Market)**

**Project:** End-to-End Coffee Quality & Autonomous Market Agent  
**Active Version Suite:** v2.3.0 (4-Part Self-Contained Modular Suite \+ Local-AI Implementation Blueprint)  
Last Updated: 2026-11-16  
Purpose: Seamless session handoff and token-exhaustion recovery tracker. Any new session can read this file first to resume work immediately without losing context.

# **1\. Current Workspace & File Inventory (`TESA_2026_Track3_NextGenMarket`)**

| File Name | Version | Status | Primary Scope |
| :---- | :---- | :---- | :---- |
| **v2/v2\_part1\_upstream\_coffee\_science.md** | v2.0.0 | Complete | Agronomy, Chumphon 1/2/5 genetics, harvesting, fermentation, drying, storage age & hermetic seal |
| **v2/v2\_part2\_grading\_cv\_chemistry\_roasting.md** | v2.0.0 | Complete | CQI Fine Robusta & TAS 5700 gates, CV morphometrics, thermography, NIR/FTIR, roasting, ESG, 18-feature schema |
| **v2/v2\_part3\_competition\_agent\_and\_pricing\_engine.md** | v2.2.0 | Complete | Track 3 rules, 4-step pluggable valuation framework, 5 statistical indicators, pluggable 6-stage pipeline \+ optional XGBoost |
| **v2/v2\_part4\_local\_ai\_implementation\_blueprint.md** | v2.3.0 | Complete | Full 13-file Python codebase blueprint (`config`, `logger`/`sniffer`, `adapters`, `stats_engine`, `xgb_plugin`, `predictors`, `guardrails`, `agent_loop`, CI/CD, e2e tests) ready for local AI execution |
| **v2/CHANGELOG\_v2.md** | v2.3.0 | Updated | Cumulative release notes covering `v2.0.0` through `v2.3.0` (Milestone M5 codebase blueprint) |
| **v2/MILESTONE\_TRACKER.md** | v2.3.0 | Active | Master progress checklist, architectural decisions, open unknowns for Nov 17, and next-session resume prompt |
| **precamp/\[PRECAMP\_DATA\]\_Track3\_QA\_Transcript\_and\_Briefing\_Notes.md** | Pre-Camp (v0) | Reference Only (Obsolete at Camp) | Pre-camp Q\&A transcript & briefing rules — superseded once live Nov 17–20 camp data arrives |

# **2\. Phased Work Milestones & Completion Checklist**

| Milestone ID | Phase Name | Status | Key Deliverable | Blocking Dependency |
| :---- | :---- | :---- | :---- | :---- |
| **M1** | Competition Rules & Transcript Synthesis | DONE | Extracted 120 THB/kg base, 90% demand, 1.5x quota, 80% buyback, Qwen 9B 4K limit | None |
| **M2** | Real-Life Coffee Science & Grading Synthesis | DONE | 11 Chumphon/KMITL papers \+ 9 CQI/TAS 5700/CV/chemistry predictors (`v2` Parts 1 & 2\) | None |
| **M3** | Statistical Market-Stage Detection Engine | DONE | 5 indicators (`CPR_t`, `Slope_t`, `CV_t`, `DIR_t`, `IUR_t`) \+ 5-stage matrix (`v2` Part 3\) | None |
| **M4** | High-Level Pluggable Pricing Pipeline & XGBoost Design | DONE | 6-stage schema-agnostic pipeline \+ optional `XGBPriceAdjuster` plugin (`v2.1.0` Part 3\) | None |
| **M5** | Pre-Camp Python Skeleton & Local-AI Blueprint (`v2.3.0`) | DONE | Completed `v2/v2_part4_local_ai_implementation_blueprint.md` (13-file modular codebase \+ FlightRecorder \+ auto\_sniffer.py \+ CI/CD \+ e2e tests) | User trigger in next turn/session |
| **M6** | Nov 17 On-Site Calibration & Local-AI Code Generation | NEXT | Generate repo locally from v2 Part 4, plug in official Nov 17 valuation weights & JSON keys, and log 6 buyer ceilings | Nov 17 AM Training Session |
| **M7** | Nov 18 Autonomous Agent Deployment (`Phase 2`) | PENDING | Push calibrated codebase to organizer Git CI/CD; train optional XGBoost on Phase 1–2 logs | Nov 18 AM Agent Training |
| **M8** | Nov 20 Final Competition Tuning (`Phase 3`) | PENDING | Enable seasonal regime multipliers & 15-round urgency decay | Nov 20 AM Final Match |

# **3\. Locked Architectural Decisions (For Seamless Continuity)**

* **Schema-Agnostic Data Ingestion (`FeatureAdapter`):** Because the exact JSON keys from the organizer's REST API and Track 1/2 payloads are unknown until Nov 17, all raw `dict` payloads pass through a configurable key-mapping dictionary (`FIELD_MAP: dict`) with safe default fallbacks (`float`, `int`, `string`, `bool`).  
* **Pluggable Strategy Pattern (`BasePricePredictor`):** The pricing engine never hardcodes a single model. It runs an ensemble/chain of independent predictor plugins (`HeuristicPredictor`, `OptionalXGBPredictor`, `LLMAdvisoryPredictor`) combined via dynamic confidence weights (`dict` of `string`: `float`).  
  * Imported inside a `try...except ImportError` block (`HAS_XGB: bool`).  
  * **Cold-Start Guard (`min_samples_int = 18`):** In Rounds 1–3 (or if `xgboost` is not installed in CI/CD, or training rows `< min_samples_int`), `w_xgb` automatically defaults to `0.0` (`float`).  
  * **Residual Learning Target (`delta_margin_float`):** Predicts clearing price ratio residual (`y_residual = P_clear / V_i - CPR_t`), win probability (`bool`/`float`), or dynamic formula weights (`[alpha, beta, gamma]`).  
* **Hard Safety Envelope (`SafetyGuardrailLayer`):** Enforces `bid_valid == True` (`bool`), `sacks_int <= Q_max` (`int`), and `final_price_float >= 0.81 * V_i` (`float`).  
* **Zero Hardcoded Real-World Thresholds (`Pluggable Feature-to-Valuation Framework` — Part 3, Section 3):** Real-world parameters from Parts 1 & 2 act strictly as directional polarity guidelines (`+w` positive quality drivers, `-w` negative defect drivers, and disabled-by-default boundary gates). Feature discovery (`FeatureRegistry`: `dict`), scaling (`"raw"`, `"reference_delta"`, `"lookup_map"`), dynamic buyer spec matching (`SpecMatcherPlugin`), and intrinsic valuation (`"LINEAR_WEIGHTED"`, `"ADDITIVE_POINTS"`, or `"CUSTOM_LAMBDA"`) are 100% config-driven so unknown synthetic competition datasets never trigger false disqualifications.  
* **Zero-Loss Black-Box Telemetry & Filtered Capture (`FlightRecorder` \+ `auto_sniffer.py` \+ `requests` Hook):** Every HTTP `GET`/`POST` payload matching target IP, port, and `Content-Type` is flushed immediately (`os.fsync()`) to `logs/<match_id>/raw_events.jsonl` and checkpointed atomically to `state_snapshot.json`, with GitHub Actions pushing `logs/` to a `telemetry-logs` branch (`if: always()`) so ephemeral runners never lose round history.

# **4\. Open Unknowns to Resolve on Nov 17 (Camp Day 1\)**

* **Exact Valuation Formula:** Exact mathematical weights for `lot_grade`, `bean_size`, and `defect_ratio` around `120.0` THB/kg.  
* **Exact JSON Schema:** Endpoint paths and field names for `GET /market`, `POST /bid`, and Track 1/2 connectivity payloads.  
* **CI/CD Environment Packages:** Whether the organizer's GitHub Actions runner allows `xgboost` / `scikit-learn` in `requirements.txt`.

# **5\. Quick-Resume Instructions for Next Session**

If your current chat session runs out of tokens, start a new chat and type:"Read MILESTONE\_TRACKER.md and v2\_part4\_local\_ai\_implementation\_blueprint.md in TESA\_2026\_Track3\_NextGenMarket/v2 and proceed with Milestone M6 (local AI implementation verification and Nov 17 on-site formula/API calibration)."