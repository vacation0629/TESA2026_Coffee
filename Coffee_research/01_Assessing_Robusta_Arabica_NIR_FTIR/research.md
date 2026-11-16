# Research Archive 01: Assessing the Levels of Robusta and Arabica in Roasted Ground Coffee Using NIR-HSI and FTIR Spectroscopy

- **Title:** Assessing the Levels of Robusta and Arabica in Roasted Ground Coffee Using NIR-HSI and FTIR Spectroscopy
- **Authors:** Warangkana Sahachairungrueng, Chuchaat Meechan, Narumon Veerachat, Andrew K. Thompson, Suthipong Teerachaichayut
- **Affiliation:** Department of Agricultural Engineering, School of Engineering, King Mongkut's Institute of Technology Ladkrabang (KMITL), Bangkok, Thailand
- **Journal / Source:** *Foods* (MDPI), 2022, Volume 11, Issue 19, Article 3122
- **DOI / URL:** [https://doi.org/10.3390/foods11193122](https://www.mdpi.com/2304-8158/11/19/3122)
- **Status:** Open Access / Peer-Reviewed

---

## 1. Executive Summary & Problem Statement
*Coffea arabica* (Arabica) commands significantly higher market prices than *Coffea canephora* (Robusta) due to its superior sensory cup profile, nuanced acidity, and sweetness. Consequently, economic adulteration—fraudulently blending cheaper Robusta into ground coffee labeled as "100% Arabica"—is a widespread issue in commercial distribution. Once coffee beans are roasted and ground, physical inspection (size, shape, color, screen retention) is impossible because the material is homogenous in appearance. Traditional wet chemical testing methods (e.g., HPLC profiling of 16-O-methylcafestol, chlorogenic acid ratios, or fatty acid methyl esters) are labor-intensive, destructive, slow, and expensive.

This study validates and benchmarks two rapid, non-destructive optical vibrational spectroscopic technologies combined with machine learning (chemometrics):
1. **Near-Infrared Hyperspectral Imaging (NIR-HSI)**
2. **Fourier Transform Infrared Spectroscopy (FTIR)**

---

## 2. Experimental Methodology & Chemometrics
- **Sample Preparation:** Pure Arabica and pure Robusta beans roasted and ground to standardized particle sizes. Blend calibration sets prepared across varying ratios (0% to 100% Robusta adulteration levels).
- **Spectroscopic Systems:**
  - **NIR-HSI System:** Hyperspectral imaging camera capturing spectral signatures across the near-infrared region (approx. 900–1700 nm), capturing both spatial distribution and reflectance spectra.
  - **FTIR Spectrometer:** Attenuated Total Reflectance (ATR)-FTIR spectrometer recording mid-infrared absorbance spectra across 4000–400 cm⁻¹.
- **Chemometric & Machine Learning Algorithms:**
  - **Qualitative Detection (Pure vs. Adulterated):** Support Vector Machine Classification (SVMC).
  - **Quantitative Quantification (Adulteration Percentage):** Support Vector Machine Regression (SVMR).

---

## 3. Key Findings & Quantitative Performance
- **Qualitative Authentication Accuracy:**
  - **NIR-HSI with SVMC:** Prediction accuracy of **98.04%**.
  - **FTIR with SVMC:** Prediction accuracy of **97.06%**.
  - Both modalities successfully discriminated between 100% pure Arabica and adulterated samples with minimal false positives.
- **Quantitative Regression Performance (Robusta Percentage Determination):**
  - **NIR-HSI (SVMR):**
    - Coefficient of determination in prediction ($R_p^2$): **0.964**
    - Root Mean Square Error of Prediction (RMSEP): **5.47%**
  - **FTIR (SVMR):**
    - Coefficient of determination in prediction ($R_p^2$): **0.956**
    - Root Mean Square Error of Prediction (RMSEP): **6.07%**

---

## 4. Real-Life Coffee Quality Parameters & Discriminative Chemical Markers
1. **Lipid Ester Bonds (C=O Stretching):**
   - Peak around **1745 cm⁻¹** in FTIR spectra corresponds to carbonyl stretching of triglyceride ester bonds. Arabica typically has a significantly higher total lipid content (15–18%) than Robusta (8–12%), making lipid absorption peaks a primary discriminator.
2. **Caffeine & Chlorogenic Acid Fingerprints:**
   - Robusta contains substantially higher caffeine (1.8–2.7% dry weight) compared to Arabica (1.0–1.5%), as well as higher chlorogenic acid (CGA) levels. Spectral absorption peaks associated with cyclic amides, aromatic rings, and C=C vibrations (approx. 1650 cm⁻¹ and 1450 cm⁻¹) exhibit characteristic shifts proportional to Robusta content.
3. **Carbohydrate Fingerprint Regions:**
   - Bands between **1000–1100 cm⁻¹** (C-O and C-C vibrations of polysaccharide backbones) reflect distinct polysaccharide ratios (galactomannans vs. arabinogalactans) between the two species.

---

## 5. Industrial & Operational Quality Control Value
- **Inline / At-Line Screening:** NIR-HSI allows automated conveyor-belt scanning of ground coffee batches without sample destruction, chemical reagents, or solvent disposal.
- **Detection Limit & Practical Tolerance:** The regression RMSEP (~5.5%) establishes that adulteration levels of 5–10% or higher can be detected with high statistical confidence in real-world commercial intake gates.
