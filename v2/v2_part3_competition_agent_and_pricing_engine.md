# **Competition AI Agent, Grade-to-Value Bridge & Statistical Pricing Engine**

## **v2.2.0 — Part 3 of 3 \| TESA Top Gun Rally 2026 — End-to-End Coffee Quality & Autonomous Market Agent**

**Modular Suite Structure (`v2`):**

* **Part 1 (`v2_part1_upstream_coffee_science.md`):** Upstream Agronomy, Varietal Genetics, Harvesting, Metagenomic Fermentation, Solar/OTA Drying & Post-Hulling Storage Safety.  
* **Part 2 (`v2_part2_grading_cv_chemistry_roasting.md`):** Downstream CQI/TAS 5700 Grading Gatekeepers, Hardware/CV Morphometrics, Active Thermography, NIR/FTIR Spectroscopy, Roasting Chemistry, Carbon Footprint, Circular Bioeconomy & 18-Feature Python Schema.  
* **Part 3 (`v2_part3_competition_agent_and_pricing_engine.md`):** Track 3 Competition Rules, Grade-to-Value Bridge Equations, 25 Market/API Variables, 5 Statistical Market-Stage Indicators (`CPR`, `Slope`, `CV`, `DIR`, `IUR`), Hybrid Quantitative-First \+ Qwen 9B Pricing Engine & Risk Matrix.

---

# **0\. Shared Master System Overview & Architecture Anchor**

This `v2.0.0` modular suite provides a complete, self-contained specification uniting **real-world Chumphon Robusta coffee science** (synthesized from 11 empirical Chumphon and KMITL research studies plus CQI Fine Robusta and Thai Agricultural Standard TAS 5700-2561) with the autonomous Python AI trading agent built for TESA Top Gun Rally 2026 (Track 3: The Next-Gen Market):

* **End-to-End Pipeline:** Track 1 (Hardware/Sensors: moisture, water activity, bulk density, fermentation pH, MOS VOC odor array) and Track 2 (Computer Vision & Spectroscopy: screen size, defect counts/mass, green `L*a*b*` color, peaberry contour ratio, post-roast quakers, active thermography destoning, NIR-HSI/FTIR authenticity) feed an **18-feature Python schema** (`int`, `float`, `string`, `bool`, `tuple`).  
* **Grade-to-Value & Autonomous Market Engine:** Those physical and chemical quality metrics map into green-bean grade tiers (`Fine Robusta`, `Premium Robusta`, `TAS 5700 Special/Class I/II`, or Track 3 `lot_grade`, `bean_size`, `defect_ratio`) and intrinsic lot value `V_i` (around the `120.0` THB/kg baseline). During live sealed-bid rounds against 35–55 teams and 6 buyer bots, the Python agent computes 5 statistical market indicators (`CPR_t`, `Slope_t`, `CV_t`, `DIR_t`, `IUR_t`) and consults the central Qwen 9B LLM (`< 500` tokens within a `4K` context limit) with an automatic `15s` deterministic rule-based fallback.

---

# **1\. Competition Overview & Game Mechanics**

In Track 3 ("The Next-Gen Market"), each team acts as a raw Robusta coffee bean seller competing against 35–55 teams in a simulated sealed-bid market. Instead of manual trading during the main rounds, teams build an autonomous Python AI Agent that observes market states via REST API, consults a central LLM advisor, and submits sealed sell offers to 6 distinct buyer bots (representing roasters and factories).

## **1.1 Core Rules & Scoring Formula**

* **Valuation-Relative Scoring:** Score is calculated based on the profit margin achieved relative to the intrinsic evaluated value (`V_lot` / `V_i`) of your own coffee lot—not absolute revenue. Teams assigned lower-grade lots can still win by selling above their lot's evaluated baseline.  
* **Baseline Price:** **120.0 THB/kg** (`float`), adjusted by an official formula incorporating grade, bean size, and defect percentage (released on Nov 17).  
* **Sealed-Bid Auction Resolution:** Each round (`~300` seconds / 5 minutes) processes all bids simultaneously at round end. Submission speed within the round has no effect. Buyer bots filter offers that meet or exceed their minimum specification, then purchase from the lowest-priced sellers first until their sack quota is filled.  
* **Market Scarcity (90% Demand Cap):** Total market demand across all rounds equals approximately **90% (`0.9`)** of the total sacks held by all competing teams combined. At least 10% of total supply will fail to sell to buyer bots.  
* **Per-Round Quota Cap (Anti-Dumping):** Sellers cannot dump all inventory in a single round; maximum sacks offered per round are capped at **1.5x** the average sacks per round.  
* **End-of-Game Buyback Penalty:** Any unsold sacks remaining after the final round are automatically bought by the central market at **80% (`0.8`)** of their evaluated value, resulting in a steep score penalty.

## **1.2 Competition Schedule & Weights**

| Phase | Date | Mode | Score Weight | Key Objectives & Rules |
| :---- | :---- | :---- | :---- | :---- |
| **Phase 1** | Nov 17 (PM) | Manual Web Trading | **20%** | Understand market mechanics, test buyer reserve ceilings, and record clearing price logs (6–8 practice rounds). |
| **Phase 2** | Nov 18 (PM) | Autonomous Agent | **30%** | Deploy Python agent via Git/CI-CD to compete live against all teams. No manual bid submission allowed; live code tuning permitted. |
| **Phase 3** | Nov 20 (AM) | Final Competition | **50%** | Full ruleset with 15 rounds, 6 coffee lots per team, and dynamic seasonal demand shifts (`HIGH_SEASON` vs. `LATE_SEASON`). |

---

# **2\. Technical Constraints & Scope Boundaries**

## **2.1 System Prerequisites & Constraints**

* **Runtime Environment:** Python 3.10+ with `venv`, `requests` / `httpx` for REST API (`GET`/`POST` JSON), and Git repository structured for organizer CI/CD (GitHub Actions) automated execution.  
* **Central LLM Server:** Organizers host a shared **9B parameter model** (Qwen 9B family) with a **\~4,000-token (`4K`) context window** and per-team rate limits. Local GPUs or local LLMs are not required and not permitted during live rounds.  
* **Track 1 & Track 2 Integration:** Market trading uses synthetic/dummy lot datasets because physical samples from Hardware (Track 1\) and Vision (Track 2\) are too small. However, separate connectivity points are awarded for successfully ingesting Track 1/Track 2 payloads into the unified agent pipeline.

## **2.2 Explicit Non-Goals**

* Do not build a graphical user interface (UI); evaluation is strictly headless/automated via Git CI/CD.  
* Do not use external commercial LLM APIs at runtime (external AI tools are allowed only during development).  
* Do not pass raw multi-round JSON logs directly to the 9B LLM due to the 4K token truncation risk.

---

# **3\. Pluggable Feature-to-Valuation Framework & Guidelines (Replacing Hardcoded Real-World Rules)**

Because the competition uses a **synthetic dataset (ข้อมูลจำลอง)** whose exact feature columns, numeric scales, and valuation weights will only be revealed during the **Nov 17 training session**, we **must not hardcode real-world agronomic or CQI/TAS 5700 thresholds** (such as fixed moisture percentages, water activity caps, or 350 g defect counts) as rigid boolean gates in code. Doing so risks falsely disqualifying valid competition lots or crashing when synthetic data omits those columns.  
Instead, real-world coffee parameters (from Parts 1 and 2\) serve strictly as **domain polarity guidelines** (telling us *which direction* a feature pushes value), while the code implements a **4-Step Config-Driven Plugin Workflow** where exact fields, operators, and weights are plugged in via `CONFIG` (`dict`) once the competition data arrives.

## **3.1 Real-World Domain Guidelines vs. Competition Plugin Roles**

| Feature Category | Real-World Examples (Parts 1 & 2\) | Expected Competition Equivalents | Directional Guideline (Polarity) | How the Flexible Plugin Handles It |
| :---- | :---- | :---- | :---- | :---- |
| **Positive Quality Drivers** | `screen_size`, `cupping_score`, `bulk_density_g_l`, `sucrose_to_cga_ratio` | `lot_grade` (`string`/`int`), `bean_size` (`float`), extra quality scores | **Higher \= Higher Value (+w)** | Mapped via configurable weight `w_pos >= 0.0` (`float`) or tier lookup `dict`; defaults to `0.0` if column is absent |
| **Negative Defect Drivers** | `primary_defects`, `secondary_defects`, `defect_mass_pct`, `quaker_count_100g` | `defect_ratio` (`float`), `defect_count` (`int`) | **Higher \= Lower Value (-w) & Buyer Ceiling** | Mapped via penalty weight `w_neg <= 0.0` (`float`) and checked against buyer `max_defect` only if specified on board |
| **Boundary / Gate Features** | `moisture_pct` (10–12.5%), `water_activity` (\< 0.60), `clean_odor_flag` | Optional status flags or range bounds (if any exist in synthetic data) | **Pass/Fail or Out-of-Range Penalty** | **Disabled by default (enabled: False)**; only activated in `CONFIG["gate_rules"]` if official Nov 17 rules explicitly require it |

## **3.2 Four-Step Pluggable Feature-to-Valuation Workflow**

### **Step 1: Dynamic Feature Discovery & Schema Mapping (FeatureRegistry \- dict)**

When the initial inventory JSON (`dict`) arrives from the Market API, the adapter inspects whatever columns actually exist and maps them via `CONFIG["feature_map"]` (`dict`) without assuming fixed real-world names:

* **Unmapped / Missing Columns:** Any real-world parameter not present in the competition dataset is automatically ignored (assigned weight `0.0` as `float` and `enabled = False` as `bool`).  
* **Unexpected New Columns:** Any new synthetic attribute introduced by the organizers is captured into `lot["extra_features"]` (`dict` of `string`: `float` / `string`) so it can be bound to a weight in `CONFIG` without editing pipeline classes.

### **Step 2: Configurable Feature Normalization (FeatureNormalizerPlugin \- callable)**

Because we do not know whether competition features will be raw numbers, percentages (`0–100`), ratios (`0.0–1.0`), or string labels (`"A"`, `"B"`, `"C"`), each active feature `k` specifies a transform mode (`string`) in `CONFIG["transforms"]`:

* `"raw"`: Passes the `float` or `int` value directly (`f_k(x_k) = float(x_k)`).  
* `"reference_delta"`: Computes deviation from a configurable baseline (`f_k(x_k) = (float(x_k) - ref_k) / scale_k`), where `ref_k` (`float`) and `scale_k` (`float`) are set on Nov 17\.  
* `"lookup_map"`: Converts categorical `string` or `int` grades into numeric multipliers via a configurable `dict` (e.g., `{"Grade_1": 0.10, "Grade_2": 0.0, "Grade_3": -0.10}`).

### **Step 3: Dynamic Buyer Eligibility Matcher (SpecMatcherPlugin \- callable)**

Instead of hardcoding real-world `is_marketable` gates, eligibility (`bid_valid` \- `bool`) is evaluated dynamically against only the keys posted in `buyer_min_spec` (`dict`) on the live Market Board API:  
`bid_valid = all( compare(lot_features[key], op, buyer_min_spec[key]) for key, op in CONFIG["buyer_spec_operators"].items() if key in buyer_min_spec )`

* If a buyer bot only specifies `min_grade` and `max_defect`, only those two keys are checked (`lot_grade >= min_grade` and `defect_ratio <= max_defect`).  
* If no gatekeeper rules are active, every lot in inventory is treated as marketable (`is_marketable = True` as `bool`).

### **Step 4: Hot-Swappable Valuation Formula Plugin (ValuationPlugin \- callable)**

To guarantee 100% compatibility with whatever formula the organizers teach on Nov 17 (matching their Excel sheet), `FlexibleValuationEngine` supports three switchable calculation templates (`CONFIG["valuation_mode"]` \- `string`) around `V_base = 120.0` (`float`):

* **Mode 1 — "LINEAR\_WEIGHTED" (Parameterized Default):**`V_i = V_base * (1.0 + sum_{k in active_features} ( w_k * f_k(x_{i,k}) ))`  
* Where `w_k` (`float`) are tunable weights stored in `CONFIG["valuation_weights"]` (`dict` of `string`: `float`). Adjusting to the competition dataset only requires typing the organizer's weights into `CONFIG`.  
* **Mode 2 — "ADDITIVE\_POINTS" (Point/Baht Offset Formula):**`V_i = V_base + sum_{k in active_features} ( w_k * f_k(x_{i,k}) )`  
* Used if the official formula adds/subtracts exact Baht amounts per grade tier, millimeter of bean size, or percentage point of defects.  
* **Mode 3 — "CUSTOM\_LAMBDA" (Direct 1-Line Excel Drop-In):**`V_i = custom_organizer_fn(lot_dict, V_base)`  
* If the Nov 17 training introduces a non-linear or piecewise rule (such as `if-else` bracket tables in Excel), you paste that exact function into `config.py` and set `valuation_mode = "CUSTOM_LAMBDA"` without touching any downstream statistical, XGBoost, or LLM modules.

---

# **4\. Complete System Variable Catalog & Mathematical Notation**

## **Table 4.1: Seller Inventory & Buyer Specification Variables**

| Variable Name | Category | Python Type | Value Range / Format | Source |
| :---- | :---- | :---- | :---- | :---- |
| `num_lots` | Seller Inventory | `int` | `4` (practice) or `6` (final) | Initial Market API |
| `initial_sacks` | Seller Inventory | `int` | `30` to `34` sacks | Initial Market API |
| `remaining_sacks` | Seller Inventory | `int` | `0` to `initial_sacks` | Tracked per round |
| `lot_grade` | Bean Quality | `string / int` | Grade tier per lot | Sample Measurement Data |
| `bean_size` | Bean Quality | `float` | Millimeters / screen size (`5.6`–`7.1+` mm) | Sample Measurement Data |
| `defect_ratio` | Bean Quality | `float` | `0.0` to `1.0` (normalized defect share) | Sample Measurement Data |
| `base_price` | Valuation | `float` | `120.0` THB/kg | Official Rulebook |
| `lot_evaluated_value` | Valuation | `float` | Calculated THB/kg per lot (`V_i`) | Official Valuation Formula |
| `buyer_ids` | Market Buyers | `list of string` | `6` distinct buyer identifiers | Market Board API |
| `buyer_min_spec` | Buyer Requirements | `dict` | Min grade (`string`/`int`), max defect (`float`) | Market Board API (per round) |
| `buyer_demand_sacks` | Buyer Demand | `int` | Sacks requested on board | Market Board API (per round) |
| `buyer_reserve_ceiling` | Buyer Behavior | `float` | Hidden max price willingness | Inferred from historical logs |

## **Table 4.2: Market Rules, Competitor History & Technical Constraint Variables**

| Variable Name | Category | Python Type | Value Range / Format | Source |
| :---- | :---- | :---- | :---- | :---- |
| `current_round` | Time & Schedule | `int` | `1` to `8` (practice) or `1` to `15` (final) | Market Schedule API |
| `total_rounds` | Time & Schedule | `int` | `6`–`8` (practice) or `15` (final) | Competition Rules |
| `round_duration_sec` | Time & Schedule | `int` | `~300` seconds (5 minutes) | Market Server |
| `market_status` | Environment | `string` | `"OPEN"`, `"CLOSED"`, `"PROCESSING"` | Market Schedule API |
| `season_state` | Environment | `string` | e.g. `"NORMAL"`, `"HIGH_SEASON"`, `"LATE_SEASON"` | Market Board API (Final) |
| `max_sacks_per_round` | Quota Constraint | `float / int` | `1.5 * (initial_sacks / total_rounds)` | Competition Rules |
| `market_demand_ratio` | Market Balance | `float` | `0.9` (90% of total market supply) | Competition Rules |
| `buyback_penalty_rate` | End-Game Rule | `float` | `0.8` (80% of evaluated lot value) | Competition Rules |
| `num_competing_teams` | Competition | `int` | `35` to `55` teams | Market Metadata |
| `prev_clearing_prices` | Round Feedback | `dict (string: float)` | Actual deal price per buyer in round `t-1` | Round Result API |
| `bid_outcome_status` | Round Feedback | `bool` | `True` (sold) or `False` (unsold) | Round Result API |
| `bid_failure_reason` | Round Feedback | `string` | Reason code if unsold | Round Result API |
| `llm_context_limit` | Technical Limit | `int` | `4096` tokens (`~4K`) | Organizer Server Spec |

## **Table 4.3: Mathematical Symbols & Runtime Tracking Variables**

| Symbol | Python Type | Description | Range / Value in Game | Data Source |
| :---- | :---- | :---- | :---- | :---- |
| `t` | `int` | Current competition round | `1` to `8` (practice) or `1` to `15` (final) | Market Schedule API |
| `R_total` | `int` | Total rounds in the match | `6`–`8` (practice) or `15` (final) | Competition Rules |
| `j` | `int` | Buyer bot index | `1` to `6` | Market Board API |
| `S_initial` | `int` | Total sacks assigned at game start | `30` to `34` sacks | Initial Inventory API |
| `V_base` | `float` | Standard baseline coffee price | `120.0` THB/kg | Official Rulebook |
| `V_i` | `float` | Evaluated intrinsic value of lot `i` | Calculated THB/kg | Official Valuation Formula |
| `bid_valid` | `bool` | Whether lot `i` meets buyer `j` min spec | `True` or `False` | Python Spec Filter |
| `history_log` | `list of dict` | Per-round clearing prices & outcomes | Appended every round | Round Result API |

---

# **5\. Agent Architecture Evaluation & Selected Design**

## **Table 5.1: Agent Architecture Alternatives**

| Architecture | Python Role | LLM (9B) Role | Primary Types | Key Trade-off |
| :---- | :---- | :---- | :---- | :---- |
| **1\. Hybrid Quantitative-First** | Computes exact valuations, filters specs, calculates safe price bounds & stats | Selects tactical price/lot within pre-validated bounds | `float`, `int`, `bool`, `string` | Moderate code complexity; highest accuracy & fault tolerance |
| **2\. Pure Rule-Based Heuristics** | Executes all valuation, matching, and dynamic pricing via math formulas | Unused (or emergency fallback only) | `float`, `int`, `bool`, `dict` | Ultra-fast & immune to LLM outages; less adaptive to human mind-games |
| **3\. LLM-Centric** | Acts strictly as REST API pipe forwarding raw JSON to prompt | Performs all arithmetic, spec checks, and pricing | `string`, `dict` | High risk of 4K token overflow, arithmetic hallucination, and invalid spec bids |

## **Selected Strategy: Hybrid Quantitative-First with Deterministic Rule-Based Fallback**

Build **Architecture 2 (Pure Rule-Based)** first as a deterministic core, then wrap **Architecture 1 (Hybrid Quantitative-First)** around it across three layers:

1. **Python Quantitative Layer:** Computes exact lot valuations (`float`), filters invalid buyer-lot pairs (`bool`), calculates 5 statistical market indicators (`float`), and enforces hard price floors (`> 0.81 * V_i`) and per-round sack quotas (`<= 1.5x` average).  
2. **Compressed LLM Advisory Layer (Qwen 9B):** Receives only a compact `< 500 token` state summary (classified Market Stage \+ pre-computed price bounds) to make tactical adjustments for seasonal shifts and competitor psychology without risking 4K context overflow.  
3. **Automatic Timeout Fallback:** If the central LLM API times out (`> 15s`) or returns unparseable output, Python immediately executes the deterministic target price formula so no round is ever missed.

---

# **6\. Statistical Parameters for Market Stage Detection**

Rather than relying solely on raw round numbers (`int`) or season labels (`string`), Python computes **5 statistical indicators** at the start of every round t to detect live market regimes.

## **6.1 Clearing Price-to-Valuation Ratio (CPR\_t)**

Measures whether competitors are trading at a profit above evaluated value or dumping below cost.

`CPR_t = (1 / N) * sum_{j=1..N} ( P_clear[j, t-1] / V_min_spec[j] )`

* **Variable Definitions:**  
  * `CPR_t` (`float`): Average clearing price ratio entering round `t`. Values `> 1.0` indicate profitable market pricing; values `< 1.0` indicate active price dumping below evaluated value.  
  * `N` (`int`): Number of buyer bots (`1` to `6`) that completed at least one purchase in round `t-1`.  
  * `P_clear[j, t-1]` (`float`): Actual transaction price (THB/kg) paid by buyer `j` in round `t-1`, fetched from the round feedback API.  
  * `V_min_spec[j]` (`float`): Evaluated value (THB/kg) of buyer `j`'s minimum required specification calculated via the official 120 THB/kg formula.  
* **Worked Example:** Suppose `N = 2` buyers closed deals in round `t-1`. Buyer 1 required a spec valued at `V_min_spec[1] = 110.0` THB and bought at `P_clear[1] = 115.5` THB. Buyer 2 required a spec valued at `V_min_spec[2] = 120.0` THB and bought at `P_clear[2] = 122.4` THB:  
    
  `CPR_t = (1 / 2) * ((115.5 / 110.0) + (122.4 / 120.0)) = (1 / 2) * (1.05 + 1.02) = 1.035`The market is currently clearing a

t **\+3.5% above** standard valuation.

## **6.2 Clearing Price Momentum Slope (`Slope_t`)**

Measures the directional velocity of market prices across consecutive rounds.

`Slope_t = CPR_t - CPR_{t-1}`

* **Variable Definitions:**  
  * `Slope_t` (`float`): Round-over-round change in `CPR`. Positive values signal price recovery (dumpers running out of stock); negative values signal intensifying price wars.  
  * `CPR_t` (`float`): Current round clearing price ratio from Section 6.1.  
  * `CPR_{t-1}` (`float`): Previous round clearing price ratio stored in `history_log` (`list` of `dict`).  
* **Worked Example:** If heavy dumping in the prior round yielded `CPR_{t-1} = 0.960` and current deals rebound to `CPR_t = 1.035`, then `Slope_t = 1.035 - 0.960 = +0.075`, confirming upward price recovery.

## **6.3 Cross-Buyer Coefficient of Variation (`CV_t`)**

Measures price dispersion across all 6 buyer bots to identify unexploited arbitrage gaps.

`CV_t = sigma_CPR[t] / mu_CPR[t]`where `sigma_CPR[t] = sqrt( (1 / N) * sum_{j=1..N} (r[j, t-1] - mu_CPR[t])^2 )`

* **Variable Definitions:**  
  * `CV_t` (`float`): Coefficient of variation across buyers. High values (`> 0.08`) indicate inefficient price discovery where certain buyers are overlooked and paying high margins. Low values (`< 0.03`) indicate tight market equilibrium.  
  * `r[j, t-1]` (`float`): Individual buyer clearing ratio defined as `P_clear[j, t-1] / V_min_spec[j]`.  
  * `mu_CPR[t]` (`float`): Mean of `r[j, t-1]` across active buyers (equals `CPR_t`).  
  * `sigma_CPR[t]` (`float`): Standard deviation of `r[j, t-1]` across the `N` active buyers.

## **6.4 Demand Intensity Ratio (`DIR_t`)**

Quantifies live seasonal demand surges or late-season contractions directly from board order volumes.

DIR\_t \= ( sum\_{j=1..6} D\[j, t\] ) / D\_bar\_expectedwhere `D_bar_expected = (0.9 * M_teams * S_initial) / R_total`

* **Variable Definitions:**  
  * `DIR_t` (`float`): Ratio of current round board demand to expected per-round demand. Values `> 1.15` confirm a **High Season** spike allowing higher markups; values `< 0.85` signal market saturation.  
  * `D[j, t]` (`int`): Number of sacks requested by buyer `j` on the market board in round `t`.  
  * `D_bar_expected` (`float`): Expected aggregate market demand per round (can also be updated dynamically as a running average of observed board totals).  
  * `0.9` (`float`): Aggregate market demand factor (90% of total supply).  
  * `M_teams` (`int`): Number of active teams in the market (`35` to `55`).

## **6.5 Inventory Urgency Ratio (`IUR_t`)**

Measures liquidation pressure to prevent unsold sacks from incurring the 80% end-of-game buyback penalty.

IUR\_t \= S\_rem\[t\] / (R\_rem\[t\] \* Q\_max)where `Q_max = 1.5 * (S_initial / R_total)`

* **Variable Definitions:**  
  * `IUR_t` (`float`): Liquidation urgency index (`0.0` to `1.0+`). Values `< 0.50` allow patient, high-margin bidding; values `> 0.75` require immediate price concessions to clear stock within quota limits.  
  * `S_rem[t]` (`int`): Unsold sacks remaining in our inventory at the start of round `t`.  
  * `R_rem[t]` (`int`): Remaining rounds including the current round (`R_total - t + 1`).  
  * `Q_max` (`float` / `int`): Maximum sacks allowed per round under the 1.5x anti-dumping rule.  
* **Worked Example:** With `S_initial = 30` sacks over `R_total = 15` rounds, average sales \= 2 sacks/round, so `Q_max = 1.5 * 2 = 3` sacks/round. At round `t = 12` (`R_rem[12] = 15 - 12 + 1 = 4` rounds left), if we still hold `S_rem[12] = 9` sacks:  
    
  `IUR_12 = 9 / (4 * 3) = 9 / 12 = 0.75`W

e must sell at nearly full capacity every remaining round to avoid the 80% buyback penalty.

---

# **7\. Market Stage Classification Matrix & Pricing Engine**

## **Table 7.1: Five-Stage Market Classification Matrix**

| Market Stage (string) | Typical Rounds (int) | Statistical Trigger (float) | Market Condition | Agent Execution Policy |
| :---- | :---- | :---- | :---- | :---- |
| `PRICE_DISCOVERY` | Rounds 1–2 | `CV > 0.08` or limited history | Competitors probing buyer reserve ceilings | Bid small sack quantities at high initial markups (`+12%` to `+18%`) to map buyer ceilings |
| `EARLY_DUMPING_WAR` | Rounds 2–6 | `CPR < 0.98` and `Slope < 0` | Panic undercutting below evaluated cost | Hold high-grade lots; offer only borderline-spec lots above `0.98 * V_i` |
| `HIGH_SEASON_PEAK` | Mid-Game | `DIR > 1.15` and `Slope > 0` | Demand surge; early dumpers out of stock | Maximize volume up to `Q_max` (`1.5x` quota) with aggressive markups |
| `LATE_SATURATION` | Rounds 10–13 | `DIR < 0.85` and `CPR` declining | Buyers nearly full; downward price pressure | Use Minimum-Spec Matching Arbitrage; undercut `P_clear` by `0.5%`–`1.5%` |
| `END_GAME_SQUEEZE` | Rounds 14–15 | `IUR > 0.70` or `R_rem <= 2` | Race to avoid 80% central buyback penalty | Prioritize 100% clearance; decay margin down toward hard floor `0.81 * V_i` |

## **7.2 Minimum-Spec Matching Arbitrage & Target Price Formula**

1. **Minimum-Spec Matching (`bool` Filter \+ Cost Sort):** Never offer a premium lot to a low-spec buyer. Sort our valid lots (`lot_grade >= min_grade` and `defect_ratio <= max_defect`) by ascending `V_i` (`float`) and assign the cheapest qualifying lot to each buyer so we can undercut rivals while preserving positive margin over `V_i`.  
2. **Pre-Calculated Target Price (`P_target`):**

`P_target(i, j, t) = max( 0.81 * V_i, V_i * (1 + M_base[j] + alpha * Slope_t + beta * (DIR_t - 1.0) - gamma * IUR_t) )`

* `M_base[j]` (`float`): Base markup calibrated per buyer `j` from Phase 1 manual trading.  
* `alpha, beta, gamma` (`float`): Tunable sensitivity weights stored in a top-level `CONFIG` dictionary for rapid live adjustment between rounds on Nov 18 and Nov 20\.  
* `0.81 * V_i` (`float`): Hard price floor—selling below `0.80 * V_i` yields worse points than letting the central market buy back unsold stock at game end.

## **7.3 Compressed LLM Prompt Interface (`< 500 Tokens`)**

Python passes only the pre-computed summary to the central 9B LLM:

* **Input (`string`):** Current round `t/total_rounds`, `Market Stage`, `CPR`, `DIR`, `IUR`, and top 3 valid `(lot_id, buyer_id, V_i, P_target, prev_P_clear)` tuples.  
* **Output (`string` \-\> parsed to `dict`):** Selected `(lot_id, buyer_id, sacks_int, final_price_float)` validated against `bid_valid == True`, `sacks <= Q_max`, and `final_price >= 0.81 * V_i`. If validation fails or API exceeds `15s` timeout, Python immediately submits `P_target`.

---

# **8\. Phased Execution Roadmap & Risk Matrix**

## **Table 8.1: Execution Milestones**

| Phase | Timeline | Key Actions | Deliverables | Verification Check |
| :---- | :---- | :---- | :---- | :---- |
| **1\. Prep** | Pre-Camp | Build Python data structures, API client skeleton, CSV/JSON logger, and Track 1/2 stub | Modular codebase \+ logging schema | Unit test with mock JSON payloads |
| **2\. Manual** | Nov 17 | Receive official valuation formula; log all 6 buyer bots' clearing prices during manual rounds | Calibrated valuation function & buyer reserve table | Python valuation matches organizer Excel to 2 decimal places |
| **3\. Auto** | Nov 18 | Deploy Hybrid Agent via Git CI/CD; monitor live logs and tune margin parameters between rounds | Autonomous agent passing CI/CD checks | Zero spec-violation rejections; latency `< 10s` per round |
| **4\. Final** | Nov 20 | Activate seasonal multiplier and end-game urgency decay for 15-round full ruleset | Final competition agent (`v3+`) | 100% inventory cleared before Round 15 close |

## **Table 8.2: Risk & Edge-Case Mitigation**

| Risk Event | Impact | Mitigation Protocol |
| :---- | :---- | :---- |
| **Prompt exceeds 4K context limit** | Trailing market data truncated; erratic pricing | Pre-aggregate all history in Python; cap prompt payload at `< 500 tokens` |
| **Central 9B LLM server timeout / rate limit** | Missed bid window (\~5 min/round) | Wrap LLM API call in `try-except` with short timeout (`15s`) falling back to deterministic Python formula |
| **Unsold inventory at Round 15** | Forced buyback at `0.80 * V_i` (heavy score loss) | Track `remaining_sacks / remaining_rounds` every turn and decay margin aggressively in final rounds |
| **Submitting off-spec lot** | Instant bid rejection | Enforce strict `bool` spec filter in Python before generating candidate offers |
| **Early-round competitor price dumping** | Margin erosion if matched blindly | Set hard price floor (`> 0.81 * V_i`) and hold premium lots until dumpers exhaust their inventory |

---

# **9\. High-Level Pluggable Price Prediction Pipeline & Optional XGBoost Architecture (v2.1.0 Upgrade)**

Because the exact JSON field names, official Nov 17 valuation coefficients, and buyer bot reserve functions are unknown prior to camp, the price prediction engine is designed as a **6-Stage Schema-Agnostic, Pluggable Pipeline** using the **Strategy and Chain-of-Responsibility patterns**. Every stage communicates via standardized Python dictionaries (`dict`) and primitive types (`int`, `float`, `string`, `bool`, `list`), allowing any module—including **XGBoost (`xgb`)** and the **Central 9B LLM**—to be hot-swapped, re-weighted, or disabled via a single top-level `PIPELINE_CONFIG` (`dict`) without breaking execution.

## **9.1 Multi-Perspective Panel Review on Pluggable Pipeline & XGBoost Integration**

* **Vote:** 4 For **Pluggable Residual-XGBoost \+ Heuristic Base**, 1 Conditional (**Skeptic** requiring a strict minimum sample gate and pure-Python fallback).  
* **Consensus:** Implement a **Decoupled 6-Stage Pipeline** where a deterministic **Heuristic Engine** provides the baseline price (`P_base` \- `float`), an optional **Pluggable XGBoost Module** predicts either the **Clearing Price Residual (`delta_margin` \- `float`)** or **Bid Win Probability (`win_prob` \- `float`)** once sufficient rounds (`>= 18` buyer-round observations) are logged, and the **Central Qwen 9B LLM** acts as a bounded tactical adjuster—all wrapped inside a hard **Safety Guardrail Envelope**.  
* **Most Weighted Lens:** **Operator** and **Skeptic** — in a 6-to-15 round game with unknown API schemas and shared CI/CD runners, cold-start survival (Rounds 1–3) and zero-crash resilience outweigh complex ML architectures.  
* **Key Condition:** The XGBoost plugin must never predict raw price directly on small samples; it must train on **normalized valuation residuals** (`P_clear / V_i`) and automatically set its blending weight `w_xgb = 0.0` (`float`) whenever `xgboost` is unavailable or historical sample count is below `min_samples` (`int`).

### **Advisor Perspectives**

* **OPERATOR (For — Pluggable Adapter \+ Registry Pattern):** Hardcoding feature columns before Nov 17 will break the moment the organizer changes a JSON key name or adds a seasonal flag. By routing all inputs through a schema-agnostic `FeatureAdapter` (`dict` mapper) and a `PredictorRegistry` (`list` of `callable` plugins), we can toggle XGBoost, Heuristic, or LLM modules on or off in 5 seconds between rounds via `CONFIG` flags.  
* **SKEPTIC (Conditional — Beware Small-Sample Overfitting & CI/CD Dependencies):** Directly challenging the **Visionary's** ML enthusiasm: 6 buyer bots across 3 rounds yield at most 18 data points—way too small for deep gradient-boosted trees, which will memorize noise from early price-dumpers. Furthermore, if the organizer's CI/CD runner restricts compiling heavy C-extensions, `import xgboost` could fail. Keep `xgb` strictly optional (`try-except ImportError`), limit `max_depth = 2` or `3`, and only activate `w_xgb > 0.0` after collecting Phase 1 manual logs or `>= 3` live rounds.  
* **VISIONARY (For — Three High-Value XGBoost Use Cases):** While simple rules handle average rounds, human competitors in Phases 2 and 3 create non-linear interactions between `season_state` (`string`), buyer demand spikes (`DIR_t` \- `float`), and round urgency (`IUR_t` \- `float`). A lightweight, shallow `XGBRegressor` or `XGBClassifier` trained on Phase 1 and Phase 2 logs can dynamically adjust the sensitivity weights (`alpha`, `beta`, `gamma` \- `float`) or estimate each buyer's hidden reserve ceiling faster than manual tuning.  
* **CUSTOMER ADVOCATE (For — Buyer-Specific Behavioral Profiling):** The 6 buyer bots have distinct personalities (premium-focused vs. volume-driven roasters). Treating all 6 buyers with one global formula leaves margin on the table; a pluggable predictor that accepts `buyer_id` (`string` one-hot or target encoded) alongside `buyer_demand_sacks` (`int`) learns exactly which buyer pays a premium when supply tightens.  
* **FINANCE MIND (For — Risk-Bounded Ensemble Blending):** Expected score maximization equals `(P_bid - V_i) * P_win + (0.80 * V_i - V_i) * (1 - P_win)` in final rounds. Using a pluggable estimator to approximate `P_win` (`float`) lets us solve for the exact expected-value-maximizing bid price while locking the hard floor at `0.81 * V_i` (`float`).

## **9.2 Six-Stage Schema-Agnostic Pipeline Architecture**

### **Table 9.1: High-Level Pipeline Stages & Data Contracts**

| Stage \# | Stage Name | Input Type | Output Type | Failure or Fallback Behavior |
| :---- | :---- | :---- | :---- | :---- |
| **Stage 1** | `DynamicSchemaAdapter` | Raw API `dict` | Canonical `dict` | Uses default fallback values if keys are missing or renamed |
| **Stage 2** | `FlexibleValuationEngine` | Canonical `dict`, `callable` | `dict` (`lot_id`: `float`) | Uses proxy formula until Nov 17 official formula is plugged in |
| **Stage 3** | `FeatureStoreAndStats` | Canonical `dict`, `list` | Feature vector `dict` (`float`, `int`) | Computes `CPR_t`, `Slope_t`, `CV_t`, `DIR_t`, `IUR_t` (`1.0` default on Round 1\) |
| **Stage 4** | `SpecAndQuotaMatcher` | Lots `list`, Buyers `list` | Valid pairs `list` of `dict` | Filters `bid_valid == True` (`bool`) and sorts by ascending `V_i` (`float`) |
| **Stage 5** | `PluggablePredictorEnsemble` | Feature `dict` per pair | `dict` (`P_pred`, `confidence`) | Blends Heuristic (`float`), Optional XGB (`float`), and LLM (`float`) |
| **Stage 6** | `SafetyGuardrailEnforcer` | Candidate bids `list` | Final API payload `dict` | Clamps price `>= 0.81 * V_i` (`float`) and total sacks `<= Q_max` (`int`) |

### **Detailed Explanation of the 6 Pipeline Stages**

* **1\. Stage 1 — `DynamicSchemaAdapter` (Zero-Lock-In Ingestion):** Maps arbitrary JSON keys from the market API and Track 1/2 payloads into internal canonical keys using a configurable lookup table (`SCHEMA_MAP: dict`). Any extra unknown fields provided by the organizers on competition day are automatically captured into an `extra_features: dict` bag (`string`: `float`) so downstream models can use them immediately without rewriting class definitions.  
* **2\. Stage 2 — `FlexibleValuationEngine` (Hot-Swappable Valuation):** Accepts any Python `callable` (`valuation_fn(lot_dict) -> float`). Before Nov 17, it runs the proxy Grade-to-Value formula (Section 3.3); on Nov 17 morning, you drop in the exact 3-line organizer formula into `config.py`.  
* **3\. Stage 3 — `FeatureStoreAndStats` (Rolling State & Feature Engineering):** Appends each round's feedback to an in-memory and disk-backed `history_log` (`list` of `dict`), computes the 5 statistical regime parameters (`CPR_t`, `Slope_t`, `CV_t`, `DIR_t`, `IUR_t` as `float`), and flattens lot \+ buyer \+ market state into a tabular feature `dict` ready for both rule equations and tree models.  
* **4\. Stage 4 — `SpecAndQuotaMatcher` (Feasibility Filter):** Evaluates every `(lot_i, buyer_j)` combination, sets `bid_valid` (`bool`), discards off-spec pairs, and ranks valid matches using Minimum-Spec Matching Arbitrage.  
* **5\. Stage 5 — `PluggablePredictorEnsemble` (Multi-Model Blending):** Queries all active predictor plugins registered in `ACTIVE_PREDICTORS` (`list` of `string`) and computes the weighted target price:  
  `P_ensemble = w_heur * P_heur + w_xgb * P_xgb + w_llm * P_llm`  
  where `w_heur + w_xgb + w_llm = 1.0` (`float`). If any plugin is disabled, times out, or raises an exception, its weight (`float`) is automatically redistributed to `w_heur`.  
* **6\. Stage 6 — `SafetyGuardrailEnforcer` (Hard Boundary Clamping):** Enforces non-negotiable competition invariants (`final_price >= max(0.81 * V_i, min_margin_floor)` and `sum(sacks) <= Q_max`) before serializing to the POST API JSON format.

## **9.3 Pluggable XGBoost (`xgb`) Integration Design: 3 Supported Modes**

Because we do not yet know which target signal will be cleanest in the live market logs, the `OptionalXGBPlugin` supports **3 selectable operating modes** (`xgb_mode: string` in `CONFIG`), all using shallow trees (`max_depth: int = 3`, `n_estimators: int = 30`, `learning_rate: float = 0.1`) to prevent overfitting on small round counts:

### **Table 9.2: Three Pluggable Operating Modes for XGBoost**

| Mode ID (`string`) | Target Variable (`y`) | Target Type | How Output Adjusts Pipeline | Best Scenario to Activate |
| :---- | :---- | :---- | :---- | :---- |
| `"MODE_A_RESIDUAL"` | `P_clear / V_min_spec - CPR_t` | `float` (Regression) | Predicts buyer-specific markup residual `delta_m` (`float`) added to `P_heur` | When clearing prices per buyer are published every round |
| `"MODE_B_WIN_PROB"` | `bid_outcome_status` (`1` or `0`) | `bool` / `float` (Classifier) | Predicts `P_win` at candidate price ratio (`float`) to maximize `EV = Margin * P_win` | When we have rich bid-outcome logs from Phase 1 and Phase 2 |
| `"MODE_C_WEIGHT_TUNER"` | Optimal `[alpha, beta, gamma]` | `list` of `float` | Uses feature importance or meta-regression to adjust heuristic formula weights | When we want interpretable formula pricing with ML-tuned weights |

### **Cold-Start & Warm-Start Lifecycle Across Competition Days**

* **Cold Start (Rounds 1–3 of Day 1 / No Prior Logs):** `len(training_rows) < min_samples` (`int`, default `18`). `OptionalXGBPlugin.is_ready()` returns `False` (`bool`). Pipeline runs with `w_xgb = 0.0`, `w_heur = 0.70`, `w_llm = 0.30`.  
* **Warm Start from Phase 1 Manual Logs (Nov 17 Evening to Nov 18 Phase 2):** All clearing prices and buyer demands logged during the Nov 17 manual web rounds (`6–8` rounds x `6` buyers \= `36–48` rows) are saved to `historical_rounds.csv` or `.json`. On Nov 18, `OptionalXGBPlugin` pre-trains on Phase 1 data at startup (`is_ready() == True`) and updates incrementally after each live round (`w_xgb = 0.35`, `w_heur = 0.45`, `w_llm = 0.20`).  
* **Zero-Breakage Fallback:** If `import xgboost` fails or `xgb_enabled == False` (`bool`), a built-in `EWMAFallbackPlugin` (pure Python exponentially weighted moving average residual tracker) seamlessly takes its place using the exact same plugin interface.