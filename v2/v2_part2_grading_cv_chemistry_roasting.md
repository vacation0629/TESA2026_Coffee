# **\[v2.0.0 — Part 2 of 3\] Downstream Grading Gatekeepers, Computer Vision Morphometrics, Roasting Chemistry & Predictive Feature Schema**

**Project:** TESA Top Gun Rally 2026 — End-to-End Coffee Quality & Autonomous Market Agent  
**Version:** v2.0.0 (Self-Contained Modular Suite — Part 2 of 3\)  
**Modular Suite Structure (`v2`):**

* **Part 1 (`v2_part1_upstream_coffee_science.md`):** Upstream Agronomy, Varietal Genetics, Harvesting, Metagenomic Fermentation, Solar/OTA Drying & Post-Hulling Storage Safety.  
* **Part 2 (`v2_part2_grading_cv_chemistry_roasting.md`):** Downstream CQI/TAS 5700 Grading Gatekeepers, Hardware/CV Morphometrics, Active Thermography, NIR/FTIR Spectroscopy, Roasting Chemistry, Carbon Footprint, Circular Bioeconomy & 18-Feature Python Schema.  
* **Part 3 (`v2_part3_competition_agent_and_pricing_engine.md`):** Track 3 Competition Rules, Grade-to-Value Bridge Equations, 25 Market/API Variables, 5 Statistical Market-Stage Indicators (`CPR`, `Slope`, `CV`, `DIR`, `IUR`), Hybrid Quantitative-First \+ Qwen 9B Pricing Engine & Risk Matrix.

**Date:** 2026-11-15  
---

# **0\. Shared Master System Overview & Architecture Anchor**

This **`v2.0.0`** modular suite provides a complete, self-contained specification uniting **real-world Chumphon Robusta coffee science** (synthesized from 11 empirical Chumphon and KMITL research studies plus CQI Fine Robusta and Thai Agricultural Standard TAS 5700-2561) with the **autonomous Python AI trading agent** built for TESA Top Gun Rally 2026 (Track 3: The Next-Gen Market):

* **End-to-End Pipeline:** Track 1 (Hardware/Sensors: moisture, water activity, bulk density, fermentation pH, MOS VOC odor array) and Track 2 (Computer Vision & Spectroscopy: screen size, defect counts/mass, green `L*a*b*` color, peaberry contour ratio, post-roast quakers, active thermography destoning, NIR-HSI/FTIR authenticity) feed an **18-feature Python schema** (`int`, `float`, `string`, `bool`, `tuple`).  
* **Grade-to-Value & Autonomous Market Engine:** Those physical and chemical quality metrics map into green-bean grade tiers (`Fine Robusta`, `Premium Robusta`, `TAS 5700 Special/Class I/II`, or Track 3 `lot_grade`, `bean_size`, `defect_ratio`) and intrinsic lot value `V_i` (around the `120.0` THB/kg baseline). During live sealed-bid rounds against 35–55 teams and 6 buyer bots, the Python agent computes 5 statistical market indicators (`CPR_t`, `Slope_t`, `CV_t`, `DIR_t`, `IUR_t`) and consults the central Qwen 9B LLM (`< 500` tokens within a `4K` context limit) with an automatic `15s` deterministic rule-based fallback.

---

# **1\. Official Grading Gatekeepers (CQI Fine Robusta & Thai TAS 5700\)**

To predict real-world commercial or specialty green-bean grade accurately, a predictive model cannot rely solely on raw defect counts. It must enforce the two official gatekeeper frameworks governing Thai and international Robusta trade: **CQI/UCDA Fine Robusta Standards** (for specialty/premium lots) and **Thai Agricultural Standard TAS 5700-2561 / ASEAN Coffee Standard** (for commercial mass-graded lots).

## **1.1 CQI / UCDA Fine Robusta & Premium Robusta Standards**

Evaluated using a **`350 g +/- 0.2 g`** green-bean sample and a **`100 g +/- 0.2 g`** sample-roasted batch:

| Grade Classification (`string`) | Green Defects (`350 g` sample) | Sample-Roasted Quakers (`quaker_count_100g` \- `int`) | Moisture & Clean Odor Gate | Screen Retention Variance (`size_retention_std` \- `float`) | Cupping Score (`cupping_score` \- `float`) |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Fine Robusta** (Specialty Tier) | **0** Category 1 (Primary) defects AND **`<= 5`** Category 2 (Secondary) defects | **`<= 3` quakers** per `100 g` roasted sample | Moisture `10.0%–12.0%`; `clean_odor_flag == True` (zero foreign/mold/sour odor) | Maximum **`<= 5.0%`** deviation from contracted screen retention | **`>= 80.00`** points (100-pt CQI scale) |
| **Premium Robusta** (High Commercial) | **`<= 12`** combined Category 1 \+ Category 2 defect equivalents in `350 g` | **`<= 5` quakers** per `100 g` roasted sample | Moisture `10.0%–12.0%`; `clean_odor_flag == True` | Maximum **`<= 5.0%`** deviation from contracted screen retention | **`>= 80.00`** points |
| **Commercial / Commodity** | Exceeds 12 combined defects or contains primary defects | `> 5` quakers per `100 g` | Graded by Thai TAS 5700 mass limits | Standard commercial screen tolerance | **`< 80.00`** points (e.g., `7.2` industrial scale) |

**Why Quaker Count (`quaker_count_100g` \- `int`) Is Mandatory:**

* Quakers are unripe/immature beans lacking sufficient sucrose for Maillard browning during roasting, appearing noticeably pale against dark roasted beans.  
* Because strip-picking in Chumphon mixes green unripe cherries with red cherries (see Part 1, Section 2C), green-bean sorting alone can miss immature beans that look normal before roasting. Sample-roasting `100 g` and counting quakers is the decisive gatekeeper separating Fine (`<= 3`), Premium (`<= 5`), and Commercial Robusta.

## **1.2 CQI Defect Equivalency Weighting Table (`350 g` Green Sample)**

Under CQI rules, if a single bean exhibits multiple defects, only the most severe defect is counted, and total defect equivalents are rounded down to whole integers (`int`):

| Defect Category | Defect Type | Beans Required for 1 Full Defect Equivalent | Visual / Physical Cause |
| :---- | :---- | :---- | :---- |
| **Category 1 (Primary)** | Full Black Bean | **1 bean** \= 1.0 defect | Over-fermentation, frost/drought stress, or severe fungal rot |
| **Category 1 (Primary)** | Full Sour Bean | **1 bean** \= 1.0 defect | Anaerobic/uncontrolled fermentation contamination (yellowish-brown, vinegar odor) |
| **Category 1 (Primary)** | Dried Cherry / Pod | **1 pod** \= 1.0 defect | Incomplete hulling leaving whole dried cherry husk intact |
| **Category 1 (Primary)** | Fungus / Mold Damage | **1 bean** \= 1.0 defect | *Aspergillus* / *Penicillium* spores from slow monsoon drying (`aw >= 0.70`) |
| **Category 1 (Primary)** | Severe Insect Damage | **5 beans** \= 1.0 defect | Deep coffee berry borer (*Hypothenemus hampei*) tunnels (`>= 3` holes) |
| **Category 1 (Primary)** | Foreign Matter | **1 piece** \= 1.0 defect | Stones, twigs, soil clods, metal fragments |
| **Category 2 (Secondary)** | Partial Black / Partial Sour | **3 beans** \= 1.0 defect | Localized blackening or souring covering `< 50%` of bean surface |
| **Category 2 (Secondary)** | Parchment / Hull | **5 pieces** \= 1.0 defect | Unremoved endocarp parchment skin |
| **Category 2 (Secondary)** | Floater / Immature / Withered | **5 beans** \= 1.0 defect | Low-density pale, wrinkled, or unripe beans |
| **Category 2 (Secondary)** | Shell / Broken / Chipped / Cut | **5 beans** \= 1.0 defect | Malformed shell beans or mechanical huller breakage |
| **Category 2 (Secondary)** | Slight Insect Damage | **10 beans** \= 1.0 defect | Shallow surface pinholes (`< 3` holes) |

## **1.3 Thai Agricultural Standard TAS 5700-2561 (มกษ. 5700\) Mass-Based Commercial Grading**

Whereas CQI counts individual defect equivalents, **Thai TAS 5700** (and the harmonized ASEAN Coffee Bean Standard) grades commercial Robusta green beans by **percentage by mass (`defect_mass_pct` \- `float`)** in a `350 g` sample:

| Quality Parameter (`TAS 5700`) | Extra / Special Class (ชั้นพิเศษ) | Class I (ชั้นหนึ่ง) | Class II (ชั้นสอง) | Inspection Method |
| :---- | :---- | :---- | :---- | :---- |
| **Total Allowable Defects (`defect_mass_pct`)** | **`<= 7.0%` by mass** | **`<= 15.0%` by mass** | **`<= 25.0%` by mass** | Gravimetric separation (`350 g` sample) |
| **Full Black Beans** | `<= 2.0%` by mass | `<= 4.0%` by mass | `<= 6.0%` by mass | Manual / Vision \+ precision scale |
| **Moldy Beans** | `<= 0.5%` by mass | `<= 1.0%` by mass | `<= 2.0%` by mass | Visual / UV / Spectroscopy |
| **Broken / Chipped Beans** | `<= 2.0%` by mass | `<= 5.0%` by mass | `<= 10.0%` by mass | Sieve & contour filtering |
| **Insect-Damaged Beans** | `<= 4.0%` by mass | `<= 8.0%` by mass | `<= 12.0%` by mass | Vision pinhole detection |
| **Dried Cherry Pods & Foreign Matter** | `<= 0.5%` each by mass | `<= 1.0%` each by mass | `<= 1.5%` each by mass | Gravimetric / Thermography |
| **Live Coffee Weevils (*Araecerus fasciculatus*)** | **0 (Zero tolerance)** | **0 (Zero tolerance)** | **0 (Zero tolerance)** | Mandatory phytosanitary check |
| **Adjacent Screen Size Tolerance** | **`<= 10.0%` by weight** above/below label | **`<= 10.0%` by weight** | **`<= 10.0%` by weight** | Round-hole sieve stack (ISO 4150\) |

# **2\. Hardware & Computer Vision Morphometrics (Track 1 & Track 2 Domain)**

## **2.1 Physical & Morphometric Predictors**

* **Volumetric Bulk Density (`bulk_density_g_l` \- `float`):**  
  * Measured in grams per liter (`g/L`) using a standard chondrometer / graduated cylinder.  
  * **Benchmark:** High-quality green Robusta measures **`650.0 – 720.0 g/L`**. Lots falling below **`620.0 g/L`** possess porous cellular structure, scorch rapidly in drum roasters, and cup flat regardless of screen size.  
* **Raw Green Bean Color (`green_color_lab` \- `tuple` of `float` / `string`):**  
  * Quantified in CIELAB (`L*`, `a*`, `b*`) color space via calibrated RGB camera or colorimeter prior to roasting.  
  * **Benchmark:** Fresh, properly dried green Robusta exhibits a **bluish-green to greenish** hue (negative `a*`, low `b*`). Elevated **`+b*` (yellowish, bleached, or brownish)** signals moisture reabsorption, lipid oxidation, or past-crop aging.  
* **Bean Shape & Peaberry Ratio (`shape_peaberry_pct` \- `float`):**  
  * Extracted via Computer Vision contour analysis (`aspect_ratio`, `roundness`, `contour_convexity`).  
  * **Benchmark:** Unseparated peaberry (`เมล็ดโทน`) content should remain **`< 5.0%`** (or be sorted into a separate peaberry lot). Because round peaberries roll faster and absorb convective heat differently than flat-sided beans (`เมล็ดแบน`, common in *Chumphon 2*), mixed shapes cause uneven roast development.  
* **Screen Size Retention Distribution (`size_retention_std` \- `float`):**  
  * Standard round-hole sieves (ISO 4150 / TAS 5700): **Screen 18** (`>= 7.1 mm`), **Screen 16** (`6.3 – 7.1 mm`), **Screen 14** (`5.6 – 6.3 mm`).  
  * **Benchmark:** **`>= 90.0%`** retention on the contracted target screen (`<= 5.0%` deviation under CQI; `<= 10.0%` adjacent screen spillover under TAS 5700).  
* **Clean Odor / Volatile VOC Gate (`clean_odor_flag` \- `bool` / `float`):**  
  * Because optical cameras cannot detect off-odors, hardware grading pipelines pair a Metal-Oxide Semiconductor (MOS) gas sensor array (e.g., `BME688` / `MQ-135` VOC profile) with moisture sensors to verify `clean_odor_flag == True` (absence of musty, smoky, fermented sour, or chemical volatiles).

## **2.2 Inline Foreign Body Detection via Active Thermography (KMITL Paper 02\)**

* **Operational Problem:** Traditional RGB color sorters fail when dark stones match the color of dark roasted coffee beans.  
* **Physical Principle:** Emissivity and thermal heat capacity divergence:  
  * **Roasted Coffee Emissivity (`eps_coffee` \- `float`):** **`0.75 – 0.78`** (porous structure, low heat capacity, cools rapidly).  
  * **Stone / Rock Emissivity (`eps_stone` \- `float`):** **`0.80 – 0.85`** (dense mineral matrix, high heat capacity, retains thermal energy).  
* **Optimal Detection Protocol:** Apply a **4.0-second** thermal heating stimulation followed by infrared thermal imaging during the **first 1.0 second** cooling window, achieving **100% batch detection** of foreign stones.

# **3\. Spectroscopy, Species Authenticity & Green-Bean Cup Chemistry**

## **3.1 Species Authenticity & Adulteration Detection (KMITL Paper 01\)**

* **Operational Problem:** Fraudulent blending of lower-cost Robusta into ground coffee marketed as "100% Arabica".  
* **NIR-HSI (`900 – 1700 nm`):** Support Vector Machine Classification (SVMC) achieves **98.04%** classification accuracy; Support Vector Regression (SVMR) quantifies Robusta adulteration ratio (`1%–99% w/w`) with **`Rp^2 = 0.964`** and **`RMSEP = 5.47%`**.  
* **FTIR Spectroscopy (`4000 – 400 cm^-1`):** SVMC achieves **97.06%** accuracy; SVMR achieves **`Rp^2 = 0.956`** and **`RMSEP = 6.07%`**.  
* **Key Spectral Marker:** Lipid carbonyl ester absorption peak at **`1745 cm^-1`** (Arabica contains `15%–18%` lipids vs. Robusta `8%–12%`), reinforced by caffeine and chlorogenic acid (CGA) bands.

## **3.2 Pre-Roast Chemical Predictors of Sensory Cup Score (New in v2)**

Predicting sensory cup quality from green beans via NIR spectroscopy requires measuring the balance between sweetness precursors and bitter/astringent alkaloids:

* **Sucrose-to-Chlorogenic Acid Ratio (`sucrose_to_cga_ratio` \- `float`):**  
  * **Green Robusta Sucrose:** **`3.0% – 7.0%`** dry weight (drives Maillard browning, caramel sweetness, and aromatic complexity).  
  * **Green Robusta Chlorogenic Acids (CGA):** **`7.0% – 10.0%`** dry weight (excess CGA produces harsh, metallic bitterness and astringency).  
  * Higher `sucrose_to_cga_ratio` correlates directly with higher CQI cupping scores (`>= 80.0`).  
* **Trigonelline (`trigonelline_pct` \- `float`):** **`0.6% – 1.2%`** dry weight; degrades during roasting into desirable pyridines and nicotinic acid (niacin), contributing to roasted aroma and pleasant acidity balance.

# **4\. Precision Roasting Profiles & Bioactive Chemistry**

Evidence from **Research Papers 04, 10, and 11**:

* **Commercial Roasting Temperature Benchmarks (Ban Tham Sing):**  
  * **Dark Roast:** **186.0 °C** drum exit temperature (intense bold body, dark chocolate notes, low acidity, dense crema).  
  * **Medium / Light Roast:** **183.0 °C** drum exit temperature (caramel sweetness, subtle acidity, balanced mouthfeel).  
  * **Dynamic Moisture Offset Rule:** Roast masters adjust drop/exit temperature dynamically by **`+/- 2.0 – 3.0 °C`** based on initial green-bean `moisture_pct`.  
  * **Primary Control Metric:** Visual and **Agtron color development** serves as the primary roast termination metric; time and bean temperature act as supporting controls.  
  * **Post-Roast Cooling & Sorting:** Forced-air cooling halts residual exothermic cooking, followed by hand-sorting to remove scorched or unexpanded quaker beans and packaging in `0.5 kg` one-way degassing valve bags.  
* **Bioactive Extraction & Degradation Dynamics (KMITL Paper 04):**  
  * Roasting pyrolyzes free chlorogenic acids (CGA) into bitter lactones and polymerizes them with proteins/sugars into high-molecular-weight **melanoidin polymers** (measured via UV-Vis absorbance at **`A420 nm`**).  
  * **Hydrothermal Brewing Exhaustion:** The **first brewing extraction cycle strips 75% – 85% of water-soluble bioactive compounds** (caffeine and free phenolics). After primary brewing, residual bioactive differences across light-, medium-, and dark-roast spent grounds converge significantly.

# **5\. Carbon Footprint & Environmental Decarbonization**

Evidence from **Research Paper 11 (KMUTT / JGSEE Survey of 180 Chumphon Farms)**:

* **Life Cycle GHG Inventory:**  
  * **Roasted Coffee:** **1.67 kg CO2e / kg product**.  
  * **Ground Coffee:** **1.69 kg CO2e / kg product**.  
* **Emission Hotspots across the Supply Chain:**  
  * **Cultivation Phase (75.4%):** Emits **1.26 kg CO2e / kg coffee**, driven primarily by nitrous oxide (`N2O`, Global Warming Potential \= `298`) volatilized from excess synthetic nitrogen fertilizer.  
  * **Roasting Phase (24.5%):** Emits **0.41 kg CO2e / kg coffee** from LPG burner combustion.  
  * **Grinding Phase (1.2%):** Emits **0.02 kg CO2e / kg coffee** from grid electricity.  
* **Decarbonization Interventions (43% Total GHG Reduction):**  
  * Soil-tested optimal nitrogen fertilization (Chumphon Horticultural Research Center protocol) cuts **0.60 kg CO2e / kg**.  
  * High-efficiency roaster burners cut LPG consumption by **69%**, reducing emissions by **0.11 kg CO2e / kg**.  
  * Combined interventions lower total carbon intensity from `1.67` down to **0.96 kg CO2e / kg coffee**.

# **6\. Circular Bioeconomy & Byproduct Valorization**

Evidence from **Research Papers 06 and 07 (KMITL Prince of Chumphon Campus)**:

* **Coffee Biomass Pellets & Clean Syngas (Paper 06):**  
  * Co-pelletizing wet coffee cherry pulp (CCP) and parchment husks (CPM) produces durable fuel pellets (`> 95%` mechanical durability, bulk density `> 600 kg/m^3`, Higher Heating Value **17.5 – 19.8 MJ/kg HHV**). Silica in CPM balances potassium salts in CCP, preventing ash slagging and clinker formation.  
  * Downdraft gasification converts pellets into producer syngas (`CO` `16%–21%`, `H2` `10%–15%`, `CH4` `1.5%–3.2%`, heating value **4.5 – 5.6 MJ/Nm^3**, flame temperature `850 – 1,050 °C`), replacing **100% of LPG** in mechanical dryers and roasters.  
* **Spent Coffee Ground Activated Carbon (Paper 07):**  
  * Spent coffee grounds (SCG) washed with **1.0 M H2SO4** and carbonized at **600 °C for 2 hours** under limited-oxygen conditions (without requiring expensive `N2` purge gas), followed by microwave-assisted `KOH` activation, yield ash-free activated carbon with a maximum monolayer adsorption capacity of **16.0 mg/g** for Rhodamine B dye removal at pH 7.0 (Langmuir isotherm, pseudo-second-order chemisorption kinetics), applicable to treating high-COD coffee depulping wastewater.

# **7\. Complete 18-Feature Python Predictive Schema & Market Bridge Mapping**

| Feature Name | Python Type | Optimal Benchmark / Range | Sensor / Acquisition Domain | Track 3 Market Variable Bridge (Part 3\) |
| :---- | :---- | :---- | :---- | :---- |
| `variety_clone` | `string` | `"Chumphon 1"`, `"Chumphon 2"`, `"Chumphon 5"` | Farm / Lot Metadata | Sets baseline yield & harvest season risk |
| `moisture_pct` | `float` | `10.0` to `12.0` (`%` wet basis) | Track 1 (Capacitive / RF Moisture) | Gatekeeper for safe storage & roast offset |
| `water_activity` | `float` | `< 0.60` (`aw`) | Track 1 (Hygrometric aw Sensor) | Halts Aspergillus / OTA (\<= 5.0 ug/kg) |
| `bulk_density_g_l` | `float` | `650.0` to `720.0` (`g/L`) | Track 1 (Load Cell \+ Fixed Volume) | Predicts heat tolerance & roast development |
| `clean_odor_flag` | `bool` | `True` (zero off-odor VOCs) | Track 1 (MOS Gas Sensor Array) | Mandatory CQI / TAS 5700 pass/fail gate |
| `fermentation_ph` | `float` | `3.8` to `4.2` (end of fermentation) | Track 1 (Inline pH Probe) | Tracks LAB/yeast aromatic precursor synthesis |
| `screen_size` | `int / float` | Screen `16`–`18` (`6.3–7.1+ mm`) | Track 2 (Vision Bounding Box) | Maps directly to bean\_size (float) |
| `size_retention_std` | `float` | `>= 90.0%` on target (`<= 5%` CQI dev) | Track 2 (Vision Size Histogram) | Prevents uneven roasting & scorching |
| `primary_defects` | `int` | `0` per `350 g` (Fine Robusta) | Track 2 (Vision Classifier) | Aggregates into defect\_ratio (float) |
| `secondary_defects` | `int` | `<= 5` per `350 g` (Fine Robusta) | Track 2 (Vision Classifier) | Aggregates into defect\_ratio (float) |
| `defect_mass_pct` | `float` | `<= 7.0%` (TAS 5700 Special Class) | Track 2 \+ Scale (350 g sample) | Commercial Thai grading mass compliance |
| `green_color_lab` | `tuple of float` | Bluish-green (`low +b*`) | Track 2 (Calibrated RGB / Colorimeter) | Detects moisture damage & lipid aging |
| `shape_peaberry_pct` | `float` | `< 5.0%` (or sorted separately) | Track 2 (Contour aspect\_ratio) | Ensures uniform drum rolling in roasting |
| `quaker_count_100g` | `int` | `<= 3` (Fine), `<= 5` (Premium) | Track 2 (Post-Sample Roast Vision) | Catches unripe strip-picked beans |
| `is_authentic_species` | `bool` | `True` (`1745 cm^-1` lipid signature) | NIR-HSI / FTIR Spectroscopy | Prevents Robusta/Arabica fraud penalties |
| `sucrose_to_cga_ratio` | `float` | Sucrose `3–7%` vs CGA `7–10%` | NIR Spectroscopy | Predicts cup sweetness vs bitterness |
| `storage_age_months` | `int` | `< 6` months (or `is_hermetic == True`) | Lot Metadata / Bag Sensor | Prevents past-crop woody/papery fade |
| `cupping_score` | `float` | `>= 80.0` (Fine) vs `7.2` (Commercial) | Target Label (y\_grade) | Maps to lot\_grade (string/int) in Part 3 |

# **8\. Comprehensive 14-Stage End-to-End Operational Scorecard**

| \# | Stage | Essential Quality Parameter | Operational Target / Specification | Failure Mode if Neglected |
| :---- | :---- | :---- | :---- | :---- |
| 1 | **Planting** | Clonal Composition (`variety_clone`) | `>= 3–4` synchronized clones (`Chumphon 1, 2, 5, 84-4`) | Pollination and yield failure due to self-incompatibility |
| 2 | **Harvest** | Cherry Ripeness | `> 20–24 °Brix`; `>= 90%` ripe crimson red cherries | Green astringency, high quaker count, flat cup |
| 3 | **Flotation** | Density Separation | Water tank flotation; skim all low-density floaters | Hollow and insect-bored beans taint roast batch |
| 4 | **Fermentation** | pH & Microbiology (`fermentation_ph`) | Anaerobic tank, pH `3.8–4.2`, LAB-to-yeast succession | Acetic vinegar taint, putrefaction, flat aroma |
| 5 | **Drying** | Moisture & Water Activity | `10.0%–12.0%` moisture; `aw < 0.60`; Parabolic Solar Dome | Mold growth and Ochratoxin A (`OTA > 5.0 ug/kg`) |
| 6 | **Storage** | Storage Age & Hermetic Seal | `storage_age_months < 6` or `is_hermetic == True` | Free fatty acid oxidation and papery past-crop fade |
| 7 | **Density** | Volumetric Bulk Density | `bulk_density_g_l` `650.0 – 720.0 g/L` | Porous beans scorch during drum roasting |
| 8 | **Screening** | Screen Size & Uniformity | Screen `16–18` (`>= 6.3 mm`); `>= 90%` retention (`<= 5%` dev) | Uneven heat transfer between small and large beans |
| 9 | **Morphometrics** | Color, Shape & Odor Gate | Bluish-green `L*a*b*`, `< 5%` peaberry, `clean_odor_flag == True` | Instant CQI/TAS 5700 disqualification or uneven roast |
| 10 | **Defect Grading** | CQI Count & TAS 5700 Mass | CQI: `0` Primary, `<= 5` Secondary; TAS 5700: `<= 7.0%` mass | Downgrade from Fine/Special tier to commodity price |
| 11 | **Destoning** | Foreign Body Removal | `0` stones via Active Thermography (`Delta eps`, `1.0 s` window) | Broken grinder burrs and food safety recall |
| 12 | **Sample Roast** | Quaker & Cup Verification | `quaker_count_100g <= 3`; `cupping_score >= 80.0` | Unripe beans introduce peanut/astringent off-flavors |
| 13 | **Roasting** | Temperature & Agtron Color | `183 °C` (Med) to `186 °C` (Dark) `+/- 2–3 °C` moisture offset | Surface scorching, baked core, or excess CGA bitterness |
| 14 | **Authenticity & ESG** | Species Purity & Carbon Intensity | NIR/FTIR (`1745 cm^-1`); `<= 0.96 kg CO2e/kg` \+ syngas/SCG | Adulteration liability and carbon border penalties |

