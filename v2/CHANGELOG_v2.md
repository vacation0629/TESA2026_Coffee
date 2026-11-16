# Changelog — TESA Top Gun Rally 2026 (End-to-End Coffee Quality & Autonomous Market Agent) — Iteration v2

This changelog records all upgrades across the **self-contained modular `v2` suite** inside `TESA_2026_Track3_NextGenMarket/v2/`. Every module in `v2` includes the Shared Master System Overview anchor and stands independently with zero reliance on `v1`.

---

# \[v2.5.0\] \- 2026-11-16 (Milestone M5b Complete: Recyclable Local Analytics Dashboard)

**Added Document in `v2/`:**

* **`v2_part5_telemetry_dashboard_blueprint.md`** (Part 5 of 5 — Local Recyclable Telemetry & Market Analytics Dashboard Blueprint for Local AI Implementation)  
* **`MILESTONE_TRACKER_v2.5.0.md`** (Synchronized to `v2.5.0`; Milestone `M5b` marked `DONE`, Milestone `M6` remains `NEXT`)  
* **`CHANGELOG_v2_v2.5.0.md`** (Updated to `v2.5.0`)

## Added — Polymorphic Recyclable Dashboard & Telemetry Ingestion (`dashboard/`)

* **Schema-Agnostic Log Loader (`dashboard/data_loader.py`):** Implemented `_read_jsonl_safe` (partial-line `JSONDecodeError` guard for concurrent `os.fsync()` writes) and `load_dashboard_frames` reusing `DynamicSchemaAdapter` from `src/adapters.py` to normalize `raw_events.jsonl` and `phase1_*.jsonl` into `rounds_df`, `lots_df`, `buyers_df`, `bids_df`, and `raw_df`.  
* **Five Recyclable UI Primitives (`dashboard/components/*.py`):**  
  1. `MetricKPICard` (`kpi_card.py`): Polymorphic stat card grid recycled across global match summary, per-customer cohort, and per-coffee-grade cohort.  
  2. `EntityDimensionSelector` (`filter_bar.py`): Runtime dimension discovery (`buyer_id`, `lot_grade`, `process`, `humidity_band`, `market_stage`) adapting dynamically to `4` practice grades vs. `6` final grades without hardcoded labels.  
  3. `RecyclableTimeSeriesChart` (`time_series_chart.py`): Parameterized Plotly trend line chart reused for customer clearing prices, grade realized margins vs. `V_i`, and live statistical indicators (`CPR_t`, `DIR_t`, `IUR_t`).  
  4. `RecyclableBreakdownChart` (`breakdown_chart.py`): Parameterized grouped-bar / box distribution chart and 2D `Customer x Coffee Grade` performance heatmap.  
  5. `RecyclableEntityTable` (`entity_table.py`): Configurable sortable audit table recycled for bid execution ledgers, buyer profiles, lot quality ledgers, and raw telemetry payloads.  
* **Multi-Tab Dashboard Orchestrator & Verification (`dashboard/app.py`, `dashboard/requirements-dashboard.txt`, `tests/test_dashboard_loader.py`):** Assembled 4 local monitoring tabs while keeping `streamlit`/`plotly`/`pandas` isolated from headless CI/CD `requirements.txt`.

---

# \[v2.4.0\] \- 2026-11-16 (New Camp Clues Integrated: Humidity 9–11 & Wash/Dry Process)

**Updated Documents in `v2/`:**

* **`v2_part3_competition_agent_and_pricing_engine.md`** (Updated to `v2.4.0` — added `humidity` `9–11%` band feature and `process` `Wash`/`Dry` feature to Section 3 & Section 4\)  
* **`v2_part4_local_ai_implementation_blueprint.md`** (Updated to `v2.4.0` — updated `config.py`, `adapters.py`, `xgb_plugin.py`, `predictors.py`, and `test_pipeline_e2e.py`)

## Added — Native Support for Competition Clues (`humidity` `9–11` & `process` `Wash`/`Dry`)

* **Humidity Sweet-Spot Band (`9.0% – 11.0%`):** Added `"humidity"` (`float`) to `DynamicSchemaAdapter` (mapping `"humidity"`, `"humidity_pct"`, `"moisture"`, `"moisture_pct"`), implemented `"band_penalty"` transform in `FlexibleValuationEngine` (`0.0` penalty inside `[9.0, 11.0]`, linear deviation penalty outside), and added optional `min_humidity` / `max_humidity` board spec filters in `SpecAndQuotaMatcher`.  
* **Processing Method (`"WASHED"` vs `"DRY"`):** Added `"process"` (`string`) to `DynamicSchemaAdapter` with alias normalization (`"WASH"`/`"WASHED"`/`"WET"` \-\> `"WASHED"`, `"DRY"`/`"NATURAL"` \-\> `"DRY"`), configurable `"lookup_map"` valuation weights (`WASHED > DRY`), buyer `required_process` spec filtering, and `is_washed` (`float`) feature extraction for `OptionalXGBPlugin`.

---

# \[v2.3.0\] \- 2026-11-16 (Milestone M5 Complete)

**Added Document in `v2/`:**

* **`v2_part4_local_ai_implementation_blueprint.md`** (Part 4 of 4 — Complete Local-AI Python Codebase, Telemetry Sniffers, CI/CD & Tests, consolidated directly inside `v2/` rather than a separate `v3` folder)

## Added — Complete Local-AI-Ready Python Codebase (Part 4 of 4, 13 Files)

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

# \[v2.2.0\] \- 2026-11-16

* Replaced hardcoded real-world agronomic/CQI gates with the 4-Step Config-Driven Pluggable Feature-to-Valuation Framework (`v2_part3_competition_agent_and_pricing_engine.md`, Section 3).

# \[v2.1.0\] \- 2026-11-15

* Designed the 6-stage schema-agnostic pipeline, multi-perspective advisory review, and optional XGBoost integration (`v2_part3_competition_agent_and_pricing_engine.md`, Section 9).

# \[v2.0.0\] \- 2026-11-15

* Created the self-contained 3-part modular suite uniting 11 Chumphon/KMITL coffee research studies, 9 added grading/CV/chemistry predictors, and the Track 3 autonomous pricing engine.

# \[v1.0.0\] \- 2026-11-15 (Superseded Baseline)

* Initial Track 3 simulated market baseline (`v1_baseline_architecture_and_pricing_engine.md`) and initial synthesis of 11 Chumphon & KMITL coffee studies (`coffee_quality_parameters_real_life.md`).

---

# \[Planned / Upcoming\] \- v2.6.0 (Milestone M6 — Target: 2026-11-17 On-Site Calibration)

* Generate local repository files via local AI assistant from `v2_part4_local_ai_implementation_blueprint.md` and `v2_part5_telemetry_dashboard_blueprint.md`, then verify `unittest` suites.  
* Plug official Nov 17 valuation weights and live REST API JSON keys into `src/config.py` and warm-start `OptionalXGBPlugin` on Phase 1 manual web trading logs.