# \[PRE-CAMP DATA\] Track 3 Q\&A Transcript & Briefing Reference Notes

> **⚠️ LIFECYCLE WARNING — PRE-CAMP REFERENCE ONLY (`OBSOLETE AT CAMP`):**  
> This document captures pre-camp briefing notes and organizer Q\&A explanations (`Track_3_Transcript.md` & `Track 3.pdf`) collected prior to camp start. While it provides essential baseline context for designing our initial architecture and strategy, **all rules, field names, formulas, and assumptions below become OBSOLETE the moment official camp materials, live JSON API schemas, and Nov 17–20 rulebooks are distributed.** Whenever live camp data conflicts with this file, **live camp inputs strictly override everything here.**

**Project:** TESA Top Gun Rally 2026 — Track 3: The Next-Gen Market (Python & AI)  
**Data Classification:** `PRE-CAMP BRIEFING & Q&A TRANSCRIPT` (`v0` Reference)  
**Archived Date:** 2026-11-16

---

## 1\. Competition Overview, Schedule & Scoring Weights

In Track 3 (**"The Next-Gen Market"**), each team acts as a raw Robusta coffee bean seller (`ผู้ขายเมล็ดกาแฟโรบัสตาดิบ`) competing against **35–55 teams** in a simulated sealed-bid auction market. Teams build an autonomous Python AI Agent that queries market states via REST API (`GET`), consults a central LLM server, and submits sealed sell offers (`POST`) to up to **6 distinct buyer bots** (representing roasters and factories).

### Table 1.1: Competition Phases & Score Weights (Pre-Camp Schedule)

| Phase | Date | Mode | Score Weight | Pre-Camp Briefing Scope & Rules |
| :---- | :---- | :---- | :---- | :---- |
| **Phase 1** | Nov 17 (PM) | Manual Web Trading | **20%** | Practice rounds (`6–8` rounds) via web UI to observe market mechanics, test buyer bot reserve price ceilings, and record clearing price logs. Official valuation formula released on Nov 17\. |
| **Phase 2** | Nov 18 (PM) | Autonomous AI Agent | **30%** | Deploy Python agent via Git / CI-CD (GitHub Actions) to compete live against all teams. No manual bid submission permitted during rounds; live code/parameter tuning permitted between rounds. |
| **Phase 3** | Nov 20 (AM) | Final Competition | **50%** | Full ruleset with **15 rounds**, **6 coffee lot types** per team, and dynamic **seasonal demand shifts** (`High Season` vs. `Late Trading Season / ช่วงท้ายฤดู`). |

### Additional Evaluation Components

* **Track 1 & Track 2 Connectivity Points:** Track 3 auction trading uses synthetic/dummy lot datasets (`ข้อมูลจำลอง`) because physical coffee samples from Hardware (Track 1\) and Vision (Track 2\) are too small. However, separate connectivity points are awarded for successfully receiving and ingesting Track 1 and Track 2 payloads into the unified agent pipeline.  
* **Pitching / Business Evaluation:** Separate presentation session evaluating technical architecture and domain/business value.

---

## 2\. Core Market Mechanics & Sealed-Bid Auction Rules

| Rule / Mechanism | Pre-Camp Specification | Strategic & Engineering Implications |
| :---- | :---- | :---- |
| **Valuation-Relative Scoring** | Score is measured by profit margin achieved relative to your own lot's intrinsic evaluated value (\$V\_{\\text{lot}}\$), not absolute revenue. | Teams assigned lower-grade lots can still win if they sell above their lot's evaluated baseline. |
| **Baseline Reference Price** | **120.0 THB/kg**, adjusted by an official formula incorporating **grade (`เกรด`)**, **bean size (`ขนาด`)**, and **defect/damage level (`ความเสียหาย / เม็ดเสีย`)**. | Exact formula weights are distributed on **Nov 17** and shared identically by your agent and the market server. |
| **Sealed-Bid Simultaneous Clearing** | Each round runs **\~5 minutes (\~300 seconds)**. All bids resolve simultaneously when the round closes. | Submission speed within the 5-minute window gives **zero advantage**; take time to compute accurate bids before round close. |
| **Buyer Bot Filtering & Priority** | Up to **6 buyer bots** filter offers meeting or exceeding their minimum spec (`เกรดขั้นต่ำ`, `เม็ดเสียไม่เกิน`), then buy from the **lowest-priced valid sellers first**. | If the lowest-priced seller cannot fill a buyer's full sack order, the buyer fills remaining demand from the next-lowest valid offer. You may bid to one, several, or all 6 buyers in the same round. |
| **90% Aggregate Demand Cap** | Total market demand across all rounds equals roughly **90% (`0.9`)** of total sacks held by all competing teams combined. | At least **10%** of total market supply will go unsold to buyer bots; inventory cannot be held indefinitely. |
| **1.5x Per-Round Quota Cap** | Maximum sacks offered in a single round are capped at **1.5x** your team's average sacks per round (`1.5 * (initial_sacks / total_rounds)`). | Anti-dumping rule preventing teams from hoarding all inventory to dump in one round. |
| **80% End-of-Game Buyback Penalty** | Unsold sacks remaining after the final round are automatically bought back by the central market at **80% (`0.8`)** of their evaluated value. | Never sell below `0.80 * V_lot` during active rounds, and aggressively liquidate remaining stock in final rounds above `0.81 * V_lot`. |

---

## 3\. Data Visibility Matrix (Received vs. Hidden During Trade)

### Table 3.1: Pre-Trade Initialization Data (Received at Match Start)

| Data Item | Pre-Camp Details | Persistence During Match |
| :---- | :---- | :---- |
| **Team Coffee Lots (`ล็อตกาแฟ`)** | **4 lot types** in practice rounds and **6 lot types** in the final match, totaling roughly **30–34 sacks (`กระสอบ`)**. | Fixed at game start; only remaining sack quantities decrease as offers succeed. |
| **Lot Quality Attributes** | Simulated per-lot attributes: **grade (`เกรด`)**, **bean size (`ขนาด`)**, and **defect/damage level (`ความเสียหาย / เม็ดเสีย`)**. | Different teams receive different randomized quality distributions. |
| **Official Valuation Formula** | Distributed on Nov 17; calculates standard lot value (`THB/kg`) from the `120.0` THB/kg baseline. | Used identically by your agent and the server to score profit margins. |
| **Track 1 & 2 Payloads** | Sensor/vision outputs passed from Track 1 and Track 2 into your unified script. | Not used in auction pricing (market uses dummy data), but required for **Connectivity** points. |
| **Team API Key** | Unique authentication credential assigned to your team. | Authenticates both Market API calls and Central 9B LLM server requests. |

### Table 3.2: Live Round Board Data (Fetched Every Round via `GET` API)

| Data Item | Pre-Camp Details | Strategic Meaning |
| :---- | :---- | :---- |
| **Schedule & Market Status** | Current round/stage number and whether the market window is open (`เปิดตลาดหรือยัง`). | Controls polling loop timing and remaining-round liquidation calculations. |
| **Seasonal Regime (`ฤดูกาล`)** | Announced per round in the Nov 20 final match (e.g., **High Season / High Demand** vs. **Late Trading Season / `ช่วงท้ายฤดู`**). | Signals when buyers accept higher markups (`High Season`) vs. when buyers already hold stock and push prices down (`Late Season`). |
| **Buyer Identities (6 Bots)** | Up to **6 distinct buyer bots** posting orders on the board, each with distinct preferences (e.g., specialty roasters vs. volume factories). | Allows multi-buyer targeting and buyer-specific reserve ceiling profiling. |
| **Buyer Minimum Specs** | Each buyer's required **minimum grade (`เกรดขั้นต่ำ`)** and **maximum defect tolerance (`เม็ดเสียไม่เกิน`)**. | Offers below a buyer's minimum spec are automatically rejected (`off-spec`). |
| **Buyer Demand Quantity** | Exact number of **sacks (`กี่กระสอบ`)** each buyer wants to buy in that round. | Determines total round demand intensity (`DIR_t`) and partial-fill opportunities. |
| **Per-Round Sack Quota** | Maximum sacks you can submit in the current round (`1.5x` average sacks per round). | Hard constraint enforced by server validation. |

### Table 3.3: Post-Round Feedback & Strictly Hidden Information

| Visibility | Data Item | Pre-Camp Details |
| :---- | :---- | :---- |
| **Returned** | **Your Bid Outcome** | Whether each submitted offer succeeded (`ขายได้`) or failed (`ขายไม่ได้`). |
| **Returned** | **Failure Reason** | Why an unsold offer failed (`ขายไม่ได้เพราะอะไร` — e.g., outbid on price or spec mismatch). |
| **Returned** | **Actual Clearing Prices** | The exact transaction price (`ราคาเท่าไหร่`) each buyer bot actually paid in the round that just ended. |
| **Hidden** | **Rival Bids & Inventories** | Individual rival teams' submitted bid prices, remaining sack counts, and private lot valuations are **never exposed**. |
| **End-Game** | **Buyback Settlement** | Any unsold sacks remaining after the final round settle at **80% of evaluated lot value**. |

---

## 4\. Technical Infrastructure & Central LLM Constraints

* **Headless Execution via Git CI/CD:** Agents run as headless Python scripts (`GET`/`POST` JSON REST API) triggered automatically via organizer Git / GitHub Actions workflows. No graphical UI is needed or evaluated.  
* **Central LLM Server Specifications:**  
  * **Model:** Shared **9B parameter model** (Qwen 9B family) hosted by organizers.  
  * **Context Window:** **\~4,000 tokens (`4K`)** with per-team rate limits.  
  * **Runtime Restrictions:** Local GPUs, local LLMs, and external commercial LLM APIs are **not permitted** during live rounds (external AI tools are allowed only during pre-camp/offline development).  
  * **Context Truncation Risk:** Forwarding raw multi-round JSON logs directly into the 4K context window risks truncating trailing market data and causing erratic pricing; Python must pre-aggregate market statistics into a compact prompt (`< 500 tokens`).

---

## 5\. Strategic Hints from Organizer Q\&A (Ajarn Thana)

1. **Surviving Early-Round Price Dumping:** Many teams panic-dump sacks below evaluated value in Rounds 1–4. Holding quality lots above the `80%` buyback floor (`> 0.81 * V_i`) lets you capture strong margins in mid-game rounds once early dumpers exhaust their inventory.  
2. **Minimum-Spec Matching Arbitrage:** Never waste high-grade lots on low-spec buyers when lower-grade lots qualify. Match each buyer with your lowest-evaluated-value lot that satisfies their minimum spec so you can undercut competitors while preserving positive profit margin.  
3. **Probing Buyer Reserve Ceilings in Phase 1:** Use the Nov 17 manual web trading rounds (`6–8` rounds) to test the hidden maximum price ceiling (`Buyer Reserve Price`) of each of the 6 buyer bots and log every clearing price.

---

## 6\. Obsolescence & Camp Override Checklist (Nov 17–20)

When official camp instructions and live API endpoints arrive, immediately replace the pre-camp assumptions below:

| Pre-Camp Assumption in This File | What Replaces It at Camp (Nov 17–20) | Where to Plug In (`v2.2.0` Architecture) |
| :---- | :---- | :---- |
| Estimated `120.0` THB/kg baseline \+ unknown grade/size/defect weights | Official Nov 17 valuation equation & Excel sheet | `CONFIG["valuation_mode"]` & `CONFIG["valuation_weights"]` (`Part 3, Section 3.2`) |
| Generic field descriptions (`grade`, `bean_size`, `defect_ratio`) | Exact REST API JSON keys (`GET /market`, `POST /bid`, Track 1/2 payloads) | `CONFIG["feature_map"]` & `SCHEMA_MAP` (`Part 3, Sections 3.2 & 9.2`) |
| Estimated `35–55` teams and `30–34` initial sacks | Actual team count (`M_teams`) and initial sack allocation (`S_initial`) | `FeatureStoreAndStats` runtime initialization (`Part 3, Section 6.4`) |
| Qualitative buyer bot personas & seasonal descriptions | Empirical clearing prices (`P_clear`) and live `season_state` flags | `history_log` & `OptionalXGBPlugin` warm-start training (`Part 3, Section 9.3`) |
| Assumed Python CI/CD package availability | Actual `requirements.txt` supported on organizer GitHub Actions runner | `HAS_XGB` `try...except ImportError` guard (`Part 3, Section 9.3`) |

