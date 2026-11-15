# \[v1.0.0\] Baseline Architecture, System Variables & Statistical Pricing Engine

**Project:** TESA Top Gun Rally 2026 — Track 3: The Next-Gen Market (Python & AI)  
**Version:** `v1.0.0` (Consolidated Standalone Pre-Camp Baseline)  
**Date:** 2026-11-15

---

## 1\. Competition Overview & Game Mechanics

In Track 3 ("The Next-Gen Market"), each team acts as a raw Robusta coffee bean seller competing against 35–55 teams in a simulated sealed-bid market. Instead of manual trading during the main rounds, teams build an autonomous Python AI Agent that observes market states via REST API, consults a central LLM advisor, and submits sealed sell offers to 6 distinct buyer bots (representing roasters and factories).

### Core Rules & Scoring Formula

* **Valuation-Relative Scoring:** Score is calculated based on the profit margin achieved relative to the intrinsic evaluated value (\$V\_{\\text{lot}}\$) of your own coffee lot—not absolute revenue. Teams assigned lower-grade lots can still win by selling above their lot's evaluated baseline.  
* **Baseline Price:** **120.0 THB/kg**, adjusted by an official formula incorporating grade, bean size, and defect percentage (released on Nov 17).  
* **Sealed-Bid Auction Resolution:** Each round (\~5 minutes) processes all bids simultaneously at round end. Submission speed within the round has no effect. Buyer bots filter offers that meet or exceed their minimum specification, then purchase from the lowest-priced sellers first until their sack quota is filled.  
* **Market Scarcity (90% Demand Cap):** Total market demand across all rounds equals approximately **90% (`0.9`)** of the total sacks held by all competing teams combined. At least 10% of total supply will fail to sell to buyer bots.  
* **Per-Round Quota Cap (Anti-Dumping):** Sellers cannot dump all inventory in a single round; maximum sacks offered per round are capped at **1.5x** the average sacks per round.  
* **End-of-Game Buyback Penalty:** Any unsold sacks remaining after the final round are automatically bought by the central market at **80% (`0.8`)** of their evaluated value, resulting in a steep score penalty.

### Competition Schedule & Weights

| Phase | Date | Mode | Score Weight | Key Objectives & Rules |
| :---- | :---- | :---- | :---- | :---- |
| **Phase 1** | Nov 17 (PM) | Manual Web Trading | **20%** | Understand market mechanics, test buyer reserve ceilings, and record clearing price logs (6–8 practice rounds). |
| **Phase 2** | Nov 18 (PM) | Autonomous Agent | **30%** | Deploy Python agent via Git/CI-CD to compete live against all teams. No manual bid submission allowed; live code tuning permitted. |
| **Phase 3** | Nov 20 (AM) | Final Competition | **50%** | Full ruleset with 15 rounds, 6 coffee lots per team, and dynamic seasonal demand shifts (`High Season` vs. `Late Season`). |

---

## 2\. Technical Constraints & Scope Boundaries

### System Prerequisites & Constraints

* **Runtime Environment:** Python 3.10+ with `venv`, `requests` / `httpx` for REST API (`GET`/`POST` JSON), and Git repository structured for organizer CI/CD (GitHub Actions) automated execution.  
* **Central LLM Server:** Organizers host a shared **9B parameter model** (Qwen 9B family) with a **\~4,000-token (`4K`) context window** and per-team rate limits. Local GPUs or local LLMs are not required and not permitted during live rounds.  
* **Track 1 & Track 2 Integration:** Market trading uses synthetic/dummy lot datasets because physical samples from Hardware (Track 1\) and Vision (Track 2\) are too small. However, separate connectivity points are awarded for successfully ingesting Track 1/Track 2 payloads into the unified agent pipeline.

### Explicit Non-Goals

* Do not build a graphical user interface (UI); evaluation is strictly headless/automated via Git CI/CD.  
* Do not use external commercial LLM APIs at runtime (external AI tools are allowed only during development).  
* Do not pass raw multi-round JSON logs directly to the 9B LLM due to the 4K token truncation risk.

---

## 3\. Complete System Variable Catalog & Mathematical Notation

All variables required by the Python agent are categorized below with explicit Python data types (`int`, `float`, `string`, `bool`, `list`, `dict`).

### Table 3.1: Seller Inventory & Buyer Specification Variables

| Variable Name | Category | Python Type | Value Range / Format | Source |
| :---- | :---- | :---- | :---- | :---- |
| `num_lots` | Seller Inventory | `int` | `4` (practice) or `6` (final) | Initial Market API |
| `initial_sacks` | Seller Inventory | `int` | `30` to `34` sacks | Initial Market API |
| `remaining_sacks` | Seller Inventory | `int` | `0` to `initial_sacks` | Tracked per round |
| `lot_grade` | Bean Quality | `string` / `int` | Grade tier per lot | Sample Measurement Data |
| `bean_size` | Bean Quality | `float` | Millimeters / screen size | Sample Measurement Data |
| `defect_ratio` | Bean Quality | `float` | `0.0` to `1.0` (percentage) | Sample Measurement Data |
| `base_price` | Valuation | `float` | `120.0` THB/kg | Official Rulebook |
| `lot_evaluated_value` | Valuation | `float` | Calculated THB/kg per lot | Official Valuation Formula |
| `buyer_ids` | Market Buyers | `list` of `string` | 6 distinct buyer identifiers | Market Board API |
| `buyer_min_spec` | Buyer Requirements | `dict` | Min grade (`string`/`int`), max defect (`float`) | Market Board API (per round) |
| `buyer_demand_sacks` | Buyer Demand | `int` | Sacks requested on board | Market Board API (per round) |
| `buyer_reserve_ceiling` | Buyer Behavior | `float` | Hidden max price willingness | Inferred from historical logs |

### Table 3.2: Market Rules, Competitor History & Technical Constraint Variables

| Variable Name | Category | Python Type | Value Range / Format | Source |
| :---- | :---- | :---- | :---- | :---- |
| `current_round` | Time & Schedule | `int` | `1` to `8` (practice) or `1` to `15` (final) | Market Schedule API |
| `total_rounds` | Time & Schedule | `int` | `6`–`8` (practice) or `15` (final) | Competition Rules |
| `round_duration_sec` | Time & Schedule | `int` | `~300` seconds (5 minutes) | Market Server |
| `market_status` | Environment | `string` | `"OPEN"`, `"CLOSED"`, `"PROCESSING"` | Market Schedule API |
| `season_state` | Environment | `string` | e.g. `"NORMAL"`, `"HIGH_SEASON"`, `"LATE_SEASON"` | Market Board API (Final) |
| `max_sacks_per_round` | Quota Constraint | `float` / `int` | `1.5 * (initial_sacks / total_rounds)` | Competition Rules |
| `market_demand_ratio` | Market Balance | `float` | `0.9` (90% of total market supply) | Competition Rules |
| `buyback_penalty_rate` | End-Game Rule | `float` | `0.8` (80% of evaluated lot value) | Competition Rules |
| `num_competing_teams` | Competition | `int` | `35` to `55` teams | Market Metadata |
| `prev_clearing_prices` | Round Feedback | `dict` (`string`: `float`) | Actual deal price per buyer in round `t-1` | Round Result API |
| `bid_outcome_status` | Round Feedback | `bool` | `True` (sold) or `False` (unsold) | Round Result API |
| `bid_failure_reason` | Round Feedback | `string` | Reason code if unsold | Round Result API |
| `llm_context_limit` | Technical Limit | `int` | `4096` tokens (\~4K) | Organizer Server Spec Table 3.3: Mathematical Symbols & Runtime Tracking Variables **Symbol** **Python Type** **Description** **Range / Value in Game** **Data Source** `t` `int` Current competition round `1` to `8` (practice) or `1` to `15` (final) Market Schedule API `R_total` `int` Total rounds in the match `6`–`8` (practice) or `15` (final) Competition Rules `j` `int` Buyer bot index `1` to `6` Market Board API `S_initial` `int` Total sacks assigned at game start `30` to `34` sacks Initial Inventory API `V_base` `float` Standard baseline coffee price `120.0` THB/kg Official Rulebook `V_i` `float` Evaluated intrinsic value of lot `i` Calculated THB/kg Official Valuation Formula `bid_valid` `bool` Whether lot `i` meets buyer `j` min spec `True` or `False` Python Spec Filter `history_log` `list` of `dict` Per-round clearing prices & outcomes Appended every round Round Result API  |

---

## 4\. Agent Architecture Evaluation & Selected Design

### Table 4.1: Agent Architecture Alternatives

| Architecture | Python Role | LLM (9B) Role | Primary Types | Key Trade-off |
| :---- | :---- | :---- | :---- | :---- |
| **1\. Hybrid Quantitative-First** | Computes exact valuations, filters specs, calculates safe price bounds & stats | Selects tactical price/lot within pre-validated bounds | `float`, `int`, `bool`, `string` | Moderate code complexity; highest accuracy & fault tolerance |
| **2\. Pure Rule-Based Heuristics** | Executes all valuation, matching, and dynamic pricing via math formulas | Unused (or emergency fallback only) | `float`, `int`, `bool`, `dict` | Ultra-fast & immune to LLM outages; less adaptive to human mind-games |
| **3\. LLM-Centric** | Acts strictly as REST API pipe forwarding raw JSON to prompt | Performs all arithmetic, spec checks, and pricing | `string`, `dict` | High risk of 4K token overflow, arithmetic hallucination, and invalid spec bids |

### Selected Baseline Strategy: Hybrid Quantitative-First with Deterministic Rule-Based Fallback

Build **Architecture 2 (Pure Rule-Based)** first as a deterministic core, then wrap **Architecture 1 (Hybrid Quantitative-First)** around it across three layers:

* **Python Quantitative Layer:** Computes exact lot valuations (`float`), filters invalid buyer-lot pairs (`bool`), calculates 5 statistical market indicators (`float`), and enforces hard price floors (`> 0.81 * V_lot`) and per-round sack quotas (`<= 1.5x` average).  
* **Compressed LLM Advisory Layer (Qwen 9B):** Receives only a compact `< 500 token` state summary (classified Market Stage \+ pre-computed price bounds) to make tactical adjustments for seasonal shifts and competitor psychology without risking 4K context overflow.  
* **Automatic Timeout Fallback:** If the central LLM API times out or returns unparseable output, Python immediately executes the deterministic target price formula so no round is ever missed.

---

## 5\. Statistical Parameters for Market Stage Detection

Rather than relying solely on raw round numbers (`int`) or season labels (`string`), Python computes **5 statistical indicators** at the start of every round `t` to detect live market regimes.

### 5.1 Clearing Price-to-Valuation Ratio (CPR\_t)

Measures whether competitors are trading at a profit above evaluated value or dumping below cost.  
`CPR_t = (1 / N) * sum_{j=1..N} ( P_clear[j, t-1] / V_min_spec[j] )`

* **Variable Definitions:**  
  * `CPR_t` (`float`): Average clearing price ratio entering round `t`. Values `> 1.0` indicate profitable market pricing; values `< 1.0` indicate active price dumping below evaluated value.  
  * `N` (`int`): Number of buyer bots (`1` to `6`) that completed at least one purchase in round `t-1`.  
  * `P_clear[j, t-1]` (`float`): Actual transaction price (THB/kg) paid by buyer `j` in round `t-1`, fetched from the round feedback API.  
  * `V_min_spec[j]` (`float`): Evaluated value (THB/kg) of buyer `j`'s minimum required specification calculated via the official 120 THB/kg formula.  
* **Worked Example:** Suppose `N = 2` buyers closed deals in round `t-1`. Buyer 1 required a spec valued at `V_min_spec[1] = 110.0` THB and bought at `P_clear[1] = 115.5` THB. Buyer 2 required a spec valued at `V_min_spec[2] = 120.0` THB and bought at `P_clear[2] = 122.4` THB:  
  `CPR_t = (1 / 2) * ((115.5 / 110.0) + (122.4 / 120.0)) = (1 / 2) * (1.05 + 1.02) = 1.035`  
  The market is currently clearing at **\+3.5% above** standard valuation.

### 5.2 Clearing Price Momentum Slope (Slope\_t)

Measures the directional velocity of market prices across consecutive rounds.  
`Slope_t = CPR_t - CPR_{t-1}`

* **Variable Definitions:**  
  * `Slope_t` (`float`): Round-over-round change in `CPR`. Positive values signal price recovery (dumpers running out of stock); negative values signal intensifying price wars.  
  * `CPR_t` (`float`): Current round clearing price ratio from Section 5.1.  
  * `CPR_{t-1}` (`float`): Previous round clearing price ratio stored in `history_log` (`list` of `dict`).  
* **Worked Example:** If heavy dumping in the prior round yielded `CPR_{t-1} = 0.960` and current deals rebound to `CPR_t = 1.035`, then `Slope_t = 1.035 - 0.960 = +0.075`, confirming upward price recovery.

### 5.3 Cross-Buyer Coefficient of Variation (CV\_t)

Measures price dispersion across all 6 buyer bots to identify unexploited arbitrage gaps.  
`CV_t = sigma_CPR[t] / mu_CPR[t]`  
`where sigma_CPR[t] = sqrt( (1 / N) * sum_{j=1..N} (r[j, t-1] - mu_CPR[t])^2 )`

* **Variable Definitions:**  
  * `CV_t` (`float`): Coefficient of variation across buyers. High values (`> 0.08`) indicate inefficient price discovery where certain buyers are overlooked and paying high margins. Low values (`< 0.03`) indicate tight market equilibrium.  
  * `r[j, t-1]` (`float`): Individual buyer clearing ratio defined as `P_clear[j, t-1] / V_min_spec[j]`.  
  * `mu_CPR[t]` (`float`): Mean of `r[j, t-1]` across active buyers (equals `CPR_t`).  
  * `sigma_CPR[t]` (`float`): Standard deviation of `r[j, t-1]` across the `N` active buyers.

### 5.4 Demand Intensity Ratio (DIR\_t)

Quantifies live seasonal demand surges or late-season contractions directly from board order volumes.  
`DIR_t = ( sum_{j=1..6} D[j, t] ) / D_bar_expected`  
`where D_bar_expected = (0.9 * M_teams * S_initial) / R_total`

* **Variable Definitions:**  
  * `DIR_t` (`float`): Ratio of current round board demand to expected per-round demand. Values `> 1.15` confirm a **High Season** spike allowing higher markups; values `< 0.85` signal market saturation.  
  * `D[j, t]` (`int`): Number of sacks requested by buyer `j` on the market board in round `t`.  
  * `D_bar_expected` (`float`): Expected aggregate market demand per round (can also be updated dynamically as a running average of observed board totals).  
  * `0.9` (`float`): Aggregate market demand factor (90% of total supply).  
  * `M_teams` (`int`): Number of active teams in the market (`35` to `55`).

### 5.5 Inventory Urgency Ratio (IUR\_t)

Measures liquidation pressure to prevent unsold sacks from incurring the 80% end-of-game buyback penalty.  
`IUR_t = S_rem[t] / (R_rem[t] * Q_max)`  
`where Q_max = 1.5 * (S_initial / R_total)`

* **Variable Definitions:**  
  * `IUR_t` (`float`): Liquidation urgency index (`0.0` to `1.0+`). Values `< 0.50` allow patient, high-margin bidding; values `> 0.75` require immediate price concessions to clear stock within quota limits.  
  * `S_rem[t]` (`int`): Unsold sacks remaining in our inventory at the start of round `t`.  
  * `R_rem[t]` (`int`): Remaining rounds including the current round (`R_total - t + 1`).  
  * `Q_max` (`float` / `int`): Maximum sacks allowed per round under the 1.5x anti-dumping rule.  
* **Worked Example:** With `S_initial = 30` sacks over `R_total = 15` rounds, average sales \= 2 sacks/round, so `Q_max = 1.5 * 2 = 3` sacks/round. At round `t = 12` (`R_rem[12] = 15 - 12 + 1 = 4` rounds left), if we still hold `S_rem[12] = 9` sacks:  
  `IUR_12 = 9 / (4 * 3) = 9 / 12 = 0.75`  
  We must sell at nearly full capacity every remaining round to avoid the 80% buyback penalty.

## 6\. Market Stage Classification Matrix & Pricing Engine

### Table 6.1: Five-Stage Market Classification Matrix

| Market Stage (`string`) | Typical Rounds (`int`) | Statistical Trigger (`float`) | Market Condition | Agent Execution Policy |
| :---- | :---- | :---- | :---- | :---- |
| `PRICE_DISCOVERY` | Rounds 1–2 | `CV > 0.08` or limited history | Competitors probing buyer reserve ceilings | Bid small sack quantities at high initial markups (`+12%` to `+18%`) to map buyer ceilings |
| `EARLY_DUMPING_WAR` | Rounds 2–6 | `CPR < 0.98` and `Slope < 0` | Panic undercutting below evaluated cost | Hold high-grade lots; offer only borderline-spec lots above `0.98 * V_lot` |
| `HIGH_SEASON_PEAK` | Mid-Game | `DIR > 1.15` and `Slope > 0` | Demand surge; early dumpers out of stock | Maximize volume up to `Q_max` (`1.5x` quota) with aggressive markups |
| `LATE_SATURATION` | Rounds 10–13 | `DIR < 0.85` and `CPR` declining | Buyers nearly full; downward price pressure | Use Minimum-Spec Matching Arbitrage; undercut `P_clear` by `0.5%`–`1.5%` |
| `END_GAME_SQUEEZE` | Rounds 14–15 | `IUR > 0.70` or `R_rem <= 2` | Race to avoid 80% central buyback penalty | Prioritize 100% clearance; decay margin down toward hard floor `0.81 * V_lot` |

### 6.2 Minimum-Spec Matching Arbitrage & Target Price Formula

* **Minimum-Spec Matching (`bool` Filter \+ Cost Sort):** Never offer a premium lot to a low-spec buyer. Sort our valid lots (`lot_grade >= min_grade` and `defect_ratio <= max_defect`) by ascending `V_i` (`float`) and assign the cheapest qualifying lot to each buyer so we can undercut rivals while preserving positive margin over `V_i`.  
* **Pre-Calculated Target Price (`P_target`):**

`P_target(i, j, t) = max( 0.81 * V_i, V_i * (1 + M_base[j] + alpha * Slope_t + beta * (DIR_t - 1.0) - gamma * IUR_t) )`

* `M_base[j]` (`float`): Base markup calibrated per buyer `j` from Phase 1 manual trading.  
* `alpha, beta, gamma` (`float`): Tunable sensitivity weights stored in a top-level `CONFIG` dictionary for rapid live adjustment between rounds on Nov 18 and Nov 20\.  
* `0.81 * V_i` (`float`): Hard price floor—selling below `0.80 * V_i` yields worse points than letting the central market buy back unsold stock at game end.

### 6.3 Compressed LLM Prompt Interface (\< 500 Tokens)

Python passes only the pre-computed summary to the central 9B LLM:

* **Input (`string`):** Current round `t/total_rounds`, `Market Stage`, `CPR`, `DIR`, `IUR`, and top 3 valid `(lot_id, buyer_id, V_i, P_target, prev_P_clear)` tuples.  
* **Output (`string` \-\> parsed to `dict`):** Selected `(lot_id, buyer_id, sacks_int, final_price_float)` validated against `bid_valid == True`, `sacks <= Q_max`, and `final_price >= 0.81 * V_i`. If validation fails or API exceeds `15s` timeout, Python immediately submits `P_target`.

## 7\. Phased Execution Roadmap & Risk Matrix

### Execution Milestones

| Phase | Timeline | Key Actions | Deliverables | Verification Check |
| :---- | :---- | :---- | :---- | :---- |
| **1\. Prep** | Pre-Camp | Build Python data structures, API client skeleton, CSV/JSON logger, and Track 1/2 stub | Modular codebase \+ logging schema | Unit test with mock JSON payloads |
| **2\. Manual** | Nov 17 | Receive official valuation formula; log all 6 buyer bots' clearing prices during manual rounds | Calibrated valuation function & buyer reserve table | Python valuation matches organizer Excel to 2 decimal places |
| **3\. Auto** | Nov 18 | Deploy Hybrid Agent via Git CI/CD; monitor live logs and tune margin parameters between rounds | Autonomous agent passing CI/CD checks | Zero spec-violation rejections; latency `< 10s` per round |
| **4\. Final** | Nov 20 | Activate seasonal multiplier and end-game urgency decay for 15-round full ruleset | Final competition agent (`v2+`) | 100% inventory cleared before Round 15 close |

### Risk & Edge-Case Mitigation

| Risk Event | Impact | Mitigation Protocol |
| :---- | :---- | :---- |
| Prompt exceeds 4K context limit | Trailing market data truncated; erratic pricing | Pre-aggregate all history in Python; cap prompt payload at `< 500 tokens` |
| Central 9B LLM server timeout / rate limit | Missed bid window (\~5 min/round) | Wrap LLM API call in `try-except` with short timeout (`15s`) falling back to deterministic Python formula |
| Unsold inventory at Round 15 | Forced buyback at `0.80 * V_lot` (heavy score loss) | Track `remaining_sacks / remaining_rounds` every turn and decay margin aggressively in final rounds |
| Submitting off-spec lot | Instant bid rejection | Enforce strict `bool` spec filter in Python before generating candidate offers |
| Early-round competitor price dumping | Margin erosion if matched blindly | Set hard price floor (`> 0.81 * V_lot`) and hold premium lots until dumpers exhaust their inventory |

