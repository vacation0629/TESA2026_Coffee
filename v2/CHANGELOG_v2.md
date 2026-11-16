# **Changelog — TESA Top Gun Rally 2026 (End-to-End Coffee Quality & Autonomous Market Agent) — Iteration v2**

This changelog records all upgrades across the **self-contained modular `v2` suite** inside `TESA_2026_Track3_NextGenMarket/v2/`. Every module in `v2` includes the Shared Master System Overview anchor and stands independently with zero reliance on `v1`.  
---

# **\[v2.2.0\] \- 2026-11-16**

# **\[v2.3.0\] \- 2026-11-16 (Milestone M5 Complete)**

**Added Document in `v2/`:**

* **`v2_part4_local_ai_implementation_blueprint.md`** (Part 4 of 4 — Complete Local-AI Python Codebase, Telemetry Sniffers, CI/CD & Tests, consolidated directly inside `v2/` rather than a separate `v3` folder)  
* **`MILESTONE_TRACKER.md`** (Synchronized to `v2.3.0`; Milestone M5 marked `DONE`, Milestone M6 marked `NEXT`)  
* **`CHANGELOG_v2.md`** (Updated to `v2.3.0`)

## **Added — Complete Local-AI-Ready Python Codebase (Part 4 of 4, 13 Files)**

* **Central Configuration (`src/config.py`):** Consolidated all API endpoints, IP/port/MIME filters, schema-agnostic field mappings (`schema_map`), 4-step pluggable valuation rules (`"LINEAR_WEIGHTED"`, `"ADDITIVE_POINTS"`, `"CUSTOM_LAMBDA"`), statistical pricing sensitivities (`alpha_slope`, `beta_demand`, `gamma_urgency`), and ensemble weights into a single hot-swappable `PIPELINE_CONFIG` dictionary.  
* **Zero-Loss Black-Box Telemetry (`src/logger.py` & `tools/auto_sniffer.py`):**  
  * Implemented `FlightRecorder` writing append-only `raw_events.jsonl` with immediate `os.fsync()` buffer flushing and atomic `state_snapshot.json` checkpoints.  
  * Implemented `create_monitored_session` (`requests.Session` response hook) and `tools/auto_sniffer.py` (`mitmdump` Phase 1 browser proxy addon) with exact filtering by target IP/host, port, HTTP method, and `Content-Type`.  
* **Schema-Agnostic Adapters & Hot-Swappable Valuation (`src/adapters.py`):** Implemented `DynamicSchemaAdapter` (auto-normalizing percentage vs. ratio defects and capturing unexpected organizer fields into `extra_features`), `FlexibleValuationEngine`, and `SpecAndQuotaMatcher` (Minimum-Spec Matching Arbitrage).  
* **Statistical Market-Stage Engine (`src/stats_engine.py`):** Implemented `FeatureStoreAndStats` calculating all 5 quantitative indicators (`CPR_t`, `Slope_t`, `CV_t`, `DIR_t`, `IUR_t`) and classifying all 5 market stages (`PRICE_DISCOVERY`, `EARLY_DUMPING_WAR`, `HIGH_SEASON_PEAK`, `LATE_SATURATION`, `END_GAME_SQUEEZE`).  
* **Pluggable Predictors & Optional XGBoost (`src/xgb_plugin.py` & `src/predictors.py`):**  
  * Implemented `OptionalXGBPlugin` supporting `"MODE_A_RESIDUAL"`, `"MODE_B_WIN_PROB"`, and `"MODE_C_WEIGHT_TUNER"` behind a `try...except ImportError` guard and `min_samples = 18` cold-start gate, paired with a pure-Python `EWMAFallbackPlugin`.  
  * Implemented `CompressedLLMAdvisor` (`< 500` token prompt payload \+ `15s` timeout fallback) and `PluggablePredictorEnsemble` with automatic weight redistribution.  
* **Hard Guardrails & End-to-End Orchestrator (`src/guardrails.py`, `src/agent_loop.py`, `tests/test_pipeline_e2e.py`, `.github/workflows/trade.yml`):** Implemented `0.81 * V_i` floor clamping, `Q_max` quota enforcement, Track 1/2 connectivity payload logging, automated GitHub Actions `telemetry-logs` persistence, and an offline `unittest` verification suite.

---

**Updated Documents in `v2/`:**

* **`v2_part3_competition_agent_and_pricing_engine.md`** (Replaced Section 3 with Pluggable Feature-to-Valuation Framework & Guidelines)  
* **`MILESTONE_TRACKER.md`** (Synchronized to v2.2.0)  
* **`CHANGELOG_v2.md`** (Updated to v2.2.0)

## **Changed — Replaced Hardcoded Real-World Rules with Pluggable Feature-to-Valuation Framework (Part 3, Section 3\)**

* **Removed Hardcoded Agronomic/CQI Gates:** Removed rigid `is_marketable` thresholds (`10.0 <= moisture_pct <= 12.5`, `water_activity < 0.60`, `350 g` defect divisions, and `6.35 mm` fixed offsets) from code logic so synthetic competition datasets (ข้อมูลจำลอง) with unknown schemas cannot be falsely disqualified.  
* **Domain Polarity Guidelines Matrix (Section 3.1):** Re-scoped Parts 1 & 2 real-world parameters strictly as directional polarity guidelines (`Positive Quality Drivers +w`, `Negative Defect Drivers -w`, and `Boundary/Gate Features` disabled by default).  
* **4-Step Config-Driven Plugin Workflow (Section 3.2):**  
  * **`FeatureRegistry`** (`dict`): Dynamic feature discovery ignoring absent real-world columns (`weight = 0.0`) and capturing unexpected organizer fields into `extra_features` (`dict`).  
  * **`FeatureNormalizerPlugin`** (`callable`): Supports `"raw"`, `"reference_delta"`, and `"lookup_map"` scaling modes per feature.  
  * **`SpecMatcherPlugin`** (`callable`): Checks `bid_valid` (`bool`) dynamically against only the keys actually posted in `buyer_min_spec` (`dict`).  
  * **`ValuationPlugin`** (`callable`): Supports 3 switchable formula templates (`"LINEAR_WEIGHTED"`, `"ADDITIVE_POINTS"`, and `"CUSTOM_LAMBDA"` 1-line Excel drop-in) around `V_base = 120.0` (`float`).

---

# **\[v2.1.0\] \- 2026-11-15**

**Updated & Added Documents in `v2/`:**

* **`v2_part3_competition_agent_and_pricing_engine.md`** (Updated with Section 9: High-Level Pluggable Price Prediction Pipeline & Optional XGBoost Architecture)  
* **`MILESTONE_TRACKER.md`** (New Master Continuity & Token-Recovery Tracker)  
* **`CHANGELOG_v2.md`** (Updated to `v2.1.0`)

## **Added — High-Level Pluggable Pipeline & Optional XGBoost Architecture (Part 3, Section 9\)**

* **Multi-Perspective Advisory Review (Section 9.1):** Evaluated pluggable XGBoost \+ Heuristic \+ LLM blending across 5 lenses (*Operator*, *Skeptic*, *Visionary*, *Customer Advocate*, *Finance Mind*), locking a `4 For, 1 Conditional` consensus with a strict minimum sample gate (`xgb_min_samples = 18` `int`) and zero-dependency fallback.  
* **6-Stage Schema-Agnostic Pipeline (Section 9.2):** Designed a decoupled pipeline (`DynamicSchemaAdapter` \-\> `FlexibleValuationEngine` \-\> `FeatureStoreAndStats` \-\> `SpecAndQuotaMatcher` \-\> `PluggablePredictorEnsemble` \-\> `SafetyGuardrailEnforcer`) so unknown JSON field names or last-minute Nov 17 rule changes require only config map edits.  
* **3 Pluggable XGBoost Operating Modes (Section 9.3):**  
  * `MODE_A_RESIDUAL`: Predicts buyer-specific clearing price ratio residual (`float`) over `CPR_t`.  
  * `MODE_B_WIN_PROB`: Predicts bid acceptance probability `P(Win | price_ratio)` (`float`) to maximize expected score value.  
  * `MODE_C_WEIGHT_TUNER`: Dynamically tunes heuristic sensitivity weights (`alpha_slope`, `beta_demand`, `gamma_urgency` \- `float`).  
* **Session Continuity & Milestone Tracker (`MILESTONE_TRACKER.md`):** Created a dedicated milestone checklist (`M1`–`M8`), locked architecture summary, Nov 17 unknown checklist, and one-line session resume prompt to protect against token exhaustion.

---

# **\[v2.0.0\] \- 2026-11-15**

## **Added — Self-Contained Modular Architecture & Grade-to-Value Bridge**

* **Shared Master System Overview Anchor (Section 0 in Parts 1–3):** Added a unified architectural summary to every module so each file can be read and executed independently without cross-referencing `v1`.  
* **Part 3 Competition & Pricing Engine Module (`v2_part3_competition_agent_and_pricing_engine.md`):** Integrated all Track 3 competition mechanics, 25 typed market/API variables, 3 agent architecture comparisons, 5 statistical market-stage indicators with worked examples, the `P_target` hybrid pricing formula, and the risk mitigation matrix directly into `v2`.  
* **Grade-to-Value Bridge Equations (Part 3, Section 3):** Added explicit mathematical and Boolean equations mapping the 18 green-bean quality features (`Part 2`) into `is_marketable` (`bool`), `lot_grade` (`string`), `bean_size` (`float`), `defect_ratio` (`float`), and intrinsic valuation `V_i` (`float`).

## **Added — 9 Missing Grade & Property-Prediction Parameters (Part 1 & Part 2\)**

To close the gap between general agronomic/processing knowledge (`v1`) and an executable ML/rule-based model capable of predicting official green-bean grade and roasting/cup properties, **9 critical parameters** were integrated with explicit Python data types (`int`, `float`, `string`, `bool`, `tuple`):

* **`bulk_density_g_l` (`float`):** Volumetric green-bean density benchmark (`650.0 – 720.0 g/L`; `< 620.0 g/L` scorch risk threshold).  
* **`quaker_count_100g` (`int`):** Mandatory post-sample-roast count per `100 g` (`<= 3` for CQI Fine Robusta, `<= 5` for Premium Robusta) to catch unripe strip-picked beans.  
* **`defect_mass_pct` (`float`):** Gravimetric defect percentage under **Thai Agricultural Standard TAS 5700-2561** (`<= 7.0%` Special Class total mass in `350 g`, plus specific mass caps for black, moldy, broken, insect-damaged, dried cherry, foreign matter, and zero live *Araecerus fasciculatus* weevils).  
* **`clean_odor_flag` (`bool`):** Mandatory zero-off-odor gate (CQI & TAS 5700\) measured via MOS gas sensor array (`BME688` / `MQ-135` VOC baseline).  
* **`green_color_lab` (tuple of `float` / `string`):** Pre-roast CIELAB (`L*a*b*`) color metric distinguishing fresh bluish-green beans from `+b*` yellowed/oxidized beans.  
* **`shape_peaberry_pct` (`float`):** Computer vision contour/aspect-ratio metric (`< 5.0%` unseparated peaberry tolerance) governing drum rolling and heat transfer uniformity.  
* **`size_retention_std` (`float`):** Screen size distribution variance (`>= 90.0%` target screen retention; `<= 5.0%` CQI deviation; `<= 10.0%` TAS 5700 adjacent screen tolerance).  
* **`sucrose_to_cga_ratio` (`float`):** Pre-roast NIR chemical balance between sucrose (`3.0%–7.0%`) and chlorogenic acids (`7.0%–10.0%`), alongside trigonelline (`0.6%–1.2%`), to predict sweetness vs. bitterness before roasting.  
* **`storage_age_months` (`int`) & `is_hermetic` (`bool`):** Post-hulling storage duration (`< 6` months unsealed) and hermetic barrier status to prevent free fatty acid oxidation and past-crop woody/papery cup defects in Chumphon's `~81%` ambient RH.

## **Added — Reference Standards & Schemas**

* **CQI Defect Equivalency Weighting Table (Part 2, Section 1.2):** Added exact `350 g` sample conversion ratios (`1:1` primary defects vs. `3:1`, `5:1`, and `10:1` secondary defect ratios).  
* **Complete 18-Feature Python Predictive Schema (Part 2, Section 7):** Mapped every physical, optical, chemical, and storage variable to Python data types (`int`, `float`, `string`, `bool`, `tuple`), acquisition sensors, and Part 3 market variables.  
* **Expanded 14-Stage Operational Scorecard (Part 2, Section 8):** Upgraded the 10-stage `v1` scorecard to 14 stages incorporating storage stability, bulk density, morphometrics/odor gate, and sample-roast quaker verification.

---

# **\[v1.0.0\] \- 2026-11-15 (Superseded Baseline)**

* Initial Track 3 simulated market baseline (`v1_baseline_architecture_and_pricing_engine.md`) and initial synthesis of 11 Chumphon & KMITL coffee studies (`coffee_quality_parameters_real_life.md`).

---

---

# **\[Planned / Upcoming\] \- v2.4.0 (Milestone M6 — Target: 2026-11-17 On-Site Calibration)**

* Generate local repository files via local AI assistant from `v2_part4_local_ai_implementation_blueprint.md` and verify `unittest` suite.  
* Plug official Nov 17 valuation weights and live REST API JSON keys into `src/config.py` and warm-start `OptionalXGBPlugin` on Phase 1 manual web trading logs.