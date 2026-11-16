# **\[v2.0.0 — Part 1 of 3\] Upstream Coffee Science: Agronomy, Harvesting, Fermentation, Drying & Safe Storage**

**Project:** TESA Top Gun Rally 2026 — End-to-End Coffee Quality & Autonomous Market Agent  
**Version:** v2.0.0 (Self-Contained Modular Suite — Part 1 of 3\)  
**Modular Suite Structure (**`v2`):

* **Part 1 (**`v2_part1_upstream_coffee_science.md`**):** Upstream Agronomy, Varietal Genetics, Harvesting, Metagenomic Fermentation, Solar/OTA Drying & Post-Hulling Storage Safety.  
* **Part 2 (**`v2_part2_grading_cv_chemistry_roasting.md`**):** Downstream CQI/TAS 5700 Grading Gatekeepers, Hardware/CV Morphometrics, Active Thermography, NIR/FTIR Spectroscopy, Roasting Chemistry, Carbon Footprint, Circular Bioeconomy & 18-Feature Python Schema.  
* **Part 3 (**`v2_part3_competition_agent_and_pricing_engine.md`**):** Track 3 Competition Rules, Grade-to-Value Bridge Equations, 25 Market/API Variables, 5 Statistical Market-Stage Indicators (`CPR`, `Slope`, `CV`, `DIR`, `IUR`), Hybrid Quantitative-First \+ Qwen 9B Pricing Engine & Risk Matrix.

**Date:** 2026-11-15  
---

# **0\. Shared Master System Overview & Architecture Anchor**

This `v2.0.0` modular suite provides a complete, self-contained specification uniting **real-world Chumphon Robusta coffee science** (synthesized from 11 empirical Chumphon and KMITL research studies plus CQI Fine Robusta and Thai Agricultural Standard TAS 5700-2561) with the **autonomous Python AI trading agent** built for TESA Top Gun Rally 2026 (Track 3: The Next-Gen Market):

* **End-to-End Pipeline:** Track 1 (Hardware/Sensors: moisture, water activity, bulk density, fermentation pH, MOS VOC odor array) and Track 2 (Computer Vision & Spectroscopy: screen size, defect counts/mass, green `L*a*b*` color, peaberry contour ratio, post-roast quakers, active thermography destoning, NIR-HSI/FTIR authenticity) feed an **18-feature Python schema** (`int`, `float`, `string`, `bool`, `tuple`).  
* **Grade-to-Value & Autonomous Market Engine:** Those physical and chemical quality metrics map into green-bean grade tiers (`Fine Robusta`, `Premium Robusta`, `TAS 5700 Special/Class I/II`, or Track 3 `lot_grade`, `bean_size`, `defect_ratio`) and intrinsic lot value `V_i` (around the `120.0` THB/kg baseline). During live sealed-bid rounds against 35–55 teams and 6 buyer bots, the Python agent computes 5 statistical market indicators (`CPR_t`, `Slope_t`, `CV_t`, `DIR_t`, `IUR_t`) and consults the central Qwen 9B LLM (`< 500` tokens within a `4K` context limit) with an automatic `15s` deterministic rule-based fallback.

---

# **1\. Executive Value-Chain Matrix (v2 Complete Pipeline)**

This two-part v2.0.0 reference synthesizes empirical findings from 11 scientific studies on Chumphon Robusta coffee and KMITL engineering/food science research, expanded with official CQI Fine Robusta, Thai Agricultural Standard TAS 5700-2561, Computer Vision morphometrics, and chemical/storage stability gatekeepers required to predict green-bean grade and roasting properties.

* **Stage 1 — Agronomy & Variety (Part 1, Section 2A–2B):** Recommended clones (`Chumphon 1`, `Chumphon 2`, `Chumphon 5`); polyclonal planting (`>= 3–4` synchronized clones due to self-incompatibility); tree density `145 trees/rai`; lifespan `30–50 years`; yield `~9.0 kg` fresh cherry/tree/year; multi-strata agroforestry shade (durian, mangosteen, longkong, betel nut, rubber).  
* **Stage 2 — Harvesting & Ripeness (Part 1, Section 2C):** Target ripeness `> 20–24 °Brix` deep crimson red cherries; water flotation density sorting to skim floaters; socio-economic bottleneck where flat middleman pricing and piece-rate labor trigger strip-picking (`85.9%` farmer knowledge vs `8.00/12.00` compliance).  
* **Stage 3 — Post-Harvest Fermentation & Microbiome (Part 1, Section 2D):** Microbial consortium of `64` bacterial genera (LAB) and `59` fungal/yeast genera; Day 0–2 LAB acidification followed by Day 3–6 yeast surge (*Pichia* peak Day 4, *Hanseniaspora*); controlled pH drop from `6.0` to `3.8–4.2`; volatile aroma precursors (linalool, linalyl formate, cis-isoeugenol, trans-geraniol, esters); sealed anaerobic tanks with one-way CO2 airlocks.  
* **Stage 4 — Drying & Food Safety Standards (Part 1, Section 2E):** Target safe moisture `10.0%–12.0%` (ALRO standard `11.0%–13.0%`); water activity `aw < 0.60`; Ochratoxin A (OTA) defense against *Aspergillus ochraceus* / *carbonarius* (`<= 5.0 ug/kg` roasted EU/Thai FDA; `<= 10.0 ug/kg` green TAS 5700); Raised African Beds \+ Parabolic Solar Domes (`40–50 °C`, `< 50%` RH, drying in `7–10 days`).  
* **Stage 5 — Post-Hulling Storage & Oxidation Control (Part 1, Section 2F — New in v2):** Post-hulling storage age `storage_age_months < 6` months; hermetic barrier packaging (`is_hermetic == True`) to prevent lipid hydrolysis and past-crop woody/papery fade in Chumphon's `~81%` ambient RH.  
* **Stage 6 — Official Grading Gatekeepers, CV Morphometrics & Spectroscopy (Part 2):** CQI Fine Robusta (`0` primary defects, `<= 5` secondary defects per `350 g`, `<= 3` quakers per `100 g`, cupping `>= 80.0`), Thai TAS 5700-2561 mass grading (`<= 7.0%` total defect mass), bulk density (`650–720 g/L`), green `L*a*b*` color, peaberry ratio (`< 5.0%`), clean odor VOC gate, active thermography destoning (`eps_coffee 0.75–0.78` vs `eps_stone 0.80–0.85`), NIR-HSI/FTIR authenticity (`1745 cm^-1`), and `sucrose_to_cga_ratio`.  
* **Stage 7 — Roasting, Carbon Footprint, Bioeconomy & Market Bidding (Parts 2 & 3):** Roasting (`186 °C` dark, `183 °C` medium/light, `+/- 2–3 °C` moisture offset, Agtron color), carbon footprint (`1.67–1.69 kg CO2e/kg` reduced by `43%` to `0.96 kg CO2e/kg`), closed-loop CCP+CPM syngas pellets (`17.5–19.8 MJ/kg`) \+ SCG activated carbon (`16.0 mg/g`), and autonomous sealed-bid market pricing (`P_target`).

# **2\. Detailed Upstream Technical Breakdown**

## **2A. Genetic & Varietal Quality Benchmarks (DOA Chumphon 1, 2, 5\)**

Evidence from **Research Paper 09 (Chumphon Horticultural Research Center)** establishes that variety selection is the primary determinant of bean size, out-turn yield, caffeine content, and weather resilience:

1. **Polyclonal Obligation:** Robusta is genetically self-incompatible. Monoculture planting causes pollination failure. Commercial farms must interplant **at least 3–4 synchronized clones** in alternating rows (e.g., `Chumphon 1` \+ `Chumphon 2` \+ `Chumphon 5` \+ `Chumphon 84-4`).  
2. **Bean Physical Specifications by Variety:**

| Varietal Clone (`string`) | Screen Size Distribution | 100-Bean Dry Weight (float) | Out-Turn Ratio (float) | Caffeine Content (float) | Long-Term Dry Yield (float) | Industrial Cupping & Traits |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Chumphon 1** (Indigenous Selection) | **77.5%** retained on Screen No. 16–20 (`>= 6.3–7.1 mm`) | **18.2 g** | **21.8%** | `2.05% – 2.15%` | **202.0 kg/rai/yr** (5-yr range `143–249`) | Scored **7.2** (Nestlé / QCP acceptable grade); zero defect flags; late maturity. |
| **Chumphon 2** (Exotic Selection / Control) | Medium size, dominated by Screen No. 14–16 | **15.26 – 16.0 g** | **19.5% – 20.2%** | `2.15%` | **163.18 kg/rai/yr** | Scored **7.2**; higher peaberry/flat defect incidence; severe fruit drop in drought. |
| **Chumphon 5** (Improved Exotic Line) | **46.9%** on Screens 16–20; `> 52%` on Screens 11–15 | **16.7 g** | **24.0% – 24.2%** (peak `25.7%`) | `2.10% – 2.22%` | **149.0 kg/rai/yr** (range `119–175`) | Scored **7.2**; yields **\+21% more** green coffee per cherry ton than Chumphon 2\. |

3. **The Microclimate Harvest Window Rule:**  
   * **Chumphon 2** matures early (**October–December**), coinciding with peak Southern monsoon rainfall, exposing harvested cherries to severe mold and uncontrolled fermentation risk during open sun-drying.  
   * **Chumphon 1** matures late (**November–January/February**), enabling harvesting and drying during drier, sunnier weather, yielding cleaner green beans with lower defect ratios.

## **2B. Agronomic Cultivation & On-Farm Production Parameters**

Evidence from **Research Papers 03, 10, and 11**:

1. **Planting Density & Tree Longevity:**  
   * Standard Chumphon density: **145 trees per rai** (spacing approximately `3.3 m x 3.3 m`).  
   * Economic productive lifespan: **30 to 50 years** when maintained with periodic rejuvenation pruning (stumping / การตัดทำสาว).  
2. **Crop Yield Baseline:**  
   * First commercial harvest: **Year 3** after field planting.  
   * Fresh cherry yield: **\~9.0 kg fresh cherries / tree / year**, equivalent to **\~1,305 kg fresh cherries / rai / year** or **\~260–280 kg dry green bean / rai / year** at a `21%` out-turn ratio.  
3. **Soil & Microclimate Requirements:**  
   * Soil type: Deep basaltic or limestone red clay loam with soil **pH 5.0 – 6.5**.  
   * Climate profile: Annual mean temperature **27.0 °C** (range `17 °C – 37 °C`); mean ambient relative humidity **\~81%**.  
4. **Agroforestry Intercropping Polyculture:**  
   * Cultivated under multi-canopy shade alongside durian, mangosteen, southern langsat (longkong), betel nut, and rubber.  
   * Buffers extreme solar heat stress, suppresses weed biomass naturally (cutting herbicide requirements), and diversifies smallholder income.  
5. **Fertilizer Regime:**  
   * Standard practice: **0.60 kg chemical fertilizer per tree every 4 months** (`1.80 kg/tree/year`) utilizing formulas **46-0-0 (Urea)**, **15-15-15 (Complete NPK)**, and **13-13-21 (Finishing)**.

## **2C. Harvesting Realities & The Socio-Economic Quality Bottleneck**

Evidence from **Research Paper 03 (Rab Ro, Tha Sae, Chumphon)** and **Paper 10 (Ban Tham Sing)**:

1. **The Peak Ripeness Target:**  
   * Cherries must be harvested at peak sugar accumulation: **`> 20 – 24 °Brix`** (deep crimson/wine red skin), maximizing mucilage fermentable sugars for volatile aroma synthesis.  
2. **The Piece-Rate Labor Dilemma:**  
   * An empirical survey of **312 Chumphon farmers** revealed that while **85.9%** possessed high technical knowledge of good harvesting practices, actual harvesting compliance scored only **8.00 out of 12.00 (Partially Compliant)**.  
   * **Root Cause:** Casual pickers paid per kilogram of total weight strip-pick entire branches (mixing green unripe, yellow semi-ripe, red ripe, and black overripe cherries). Because local middlemen buy bulk unhulled coffee at flat weight prices without quality premiums, farmers lack financial incentive to fund selective hand-picking.  
3. **Flotation Density Grading:**  
   * Leading community enterprises (such as Ban Tham Sing) enforce immediate post-harvest water immersion flotation: hollow, insect-bored, and immature low-density cherries float and are skimmed off, while dense, fully ripe cherries sink for processing.

## **2D. Post-Harvest Fermentation & Microbial Flavor Synthesis**

Evidence from **Research Paper 05 (KMITL Metagenomics)** and **Paper 08 (Thammasat Ethnography)**:

1. **Microbial Diversity:**  
   * **64 bacterial genera** and **59 fungal/yeast genera** interact dynamically during wet post-harvest fermentation.  
2. **Succession Dynamics:**  
   * **Days 0–2 (Bacterial Acidification):** Fast-acting Lactic Acid Bacteria (*Lactococcus lactis*, *Leuconostoc citreum-holzapfelii*, *Leuconostoc pseudomesenteroides*, *Weissella*, *Lactobacillus*) hydrolyze free sugars and rapidly lower tank pH.  
   * **Days 3–6 (Yeast Aromatic Phase):** Yeast populations surge (*Pichia fermentans-kluyveri* peaks at **Day 4**, alongside *Hanseniaspora uvarum*, *Saccharomyces cerevisiae*, *Candida parapsilosis*, and *Wickerhamomyces anomalus*).  
3. **Pectinase Degradation & Acidification:**  
   * Yeasts secrete pectinase enzymes that break down complex mucilage pectin gel within **24–48 hours**.  
   * Medium pH drops from `~6.0` down to **pH 3.8 – 4.2**, creating a natural biological hurdle that suppresses foodborne pathogens and spoilage molds.  
4. **Volatile Flavor Compound Precursors:**  
   * *Hanseniaspora* and *Rhodotorula* correlate strongly with **linalool** (floral, citrus, sweet rose notes).  
   * *Lactococcus* and *Leuconostoc* correlate with **linalyl formate** (bergamot/citrus) and **cis-isoeugenol** (warm spicy clove).  
   * Yeasts synthesize **trans-geraniol** (rose/geranium) and fruity esters (**isoamyl acetate**, **ethyl acetate**).  
5. **Anaerobic Fermentation Protocol:**  
   * Sealed fermentation tanks fitted with one-way airlock valves vent CO2 while blocking oxygen ingress, preventing oxidative browning and mold growth while promoting clean, fruit-forward ester formation.

## **2E. Sun-Drying, Moisture Standards & Mycotoxin Food Safety**

Evidence from **Research Papers 08, 10, and 11**:

1. **Target Moisture & Water Activity Thresholds:**  
   * **Safe Storage Moisture Content (`moisture_pct`):** **10.0% – 12.0%** wet basis (ALRO commercial standard: `11.0% – 13.0%`). Below `9.5%` causes brittle beans that shatter during hulling and roast unevenly; above `12.5%` accelerates fungal growth.  
   * **Water Activity (`water_activity`):** Must be maintained strictly below **`aw < 0.60`** (maximum regulatory safety ceiling `< 0.70`) to halt fungal sporulation and enzymatic degradation.  
2. **Pluvial Climate Ochratoxin A (OTA) Defense:**  
   * Chumphon's pluvial monsoon humidity (`> 80%`) fosters *Aspergillus ochraceus* and *Aspergillus carbonarius*, which synthesize nephrotoxic **Ochratoxin A (OTA)**.  
   * Regulatory limits: **`<= 5.0 ug/kg`** in roasted coffee beans (EU / Thai FDA) and **`<= 10.0 ug/kg`** in green coffee beans (Thai TAS 5700-2018).  
3. **Drying Infrastructure Solutions:**  
   * **Raised African Beds:** Mesh wire tables elevated `0.8 – 1.0 m` above ground for 360-degree airflow.  
   * **Parabolic Solar Domes:** Transparent polycarbonate greenhouse dryers maintaining internal temperatures of **40 °C – 50 °C** and **`< 50%` RH**, shielding beans from sudden monsoon rain and reducing drying duration from \~20 days down to **7–10 days**.  
   * Layer protocol: Cherries/parchment spread thin (`2 – 3 cm`) and raked every `1 – 2 hours`.

## **2F. Post-Hulling Storage Age, Oxidation & Packaging Stability (New in v2)**

Added in v2.0.0 to close the post-drying predictive gap for cup freshness:

1. **Storage Age Decay (`storage_age_months` \- `int`):**  
   * Even when properly dried to `10.0%–12.0%` moisture and `aw < 0.60`, green Robusta stored in conventional jute or woven polypropylene bags in Chumphon's `~81%` ambient RH undergoes free fatty acid hydrolysis and lipid oxidation within **4 to 6 months**.  
   * Beans stored **`> 6 – 12 months`** ("past-crop" / "old-crop") lose volatile aromatic precursors and develop flat, woody, or papery cup defects that visual defect inspection cannot detect.  
2. **Hermetic Barrier Packaging (`is_hermetic` \- `bool`):**  
   * Storing hulled green beans inside high-barrier hermetic liners (e.g., GrainPro / Ecotact) stabilizes internal moisture and oxygen levels, preserving bluish-green color and sensory cup score for `12+ months`.  
   * Any predictive grading model must track both `storage_age_months` (`int`) and `is_hermetic` (`bool`) alongside `moisture_pct` (`float`).

