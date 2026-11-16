# Research Archive 02: Detection of Foreign Bodies in Roasted Coffee by Using Active Thermography

- **Title:** Detection of Foreign Bodies in Roasted Coffee by Using Active Thermography
- **Authors:** A. Ngoensod, N. Nunak, T. Suesut
- **Affiliation:** Department of Instrumentation and Control Engineering & Department of Food Engineering, Faculty of Engineering, King Mongkut’s Institute of Technology Ladkrabang (KMITL), Bangkok, Thailand
- **Conference / Source:** Proceedings of the International MultiConference of Engineers and Computer Scientists (IMECS 2017), Vol. I, Hong Kong, March 15–17, 2017
- **Publication Details:** ISBN: 978-988-14047-3-2, ISSN: 2078-0958, pp. 391–394
- **URL:** [https://www.iaeng.org/publication/IMECS2017/IMECS2017_pp391-394.pdf](https://www.iaeng.org/publication/IMECS2017/IMECS2017_pp391-394.pdf)

---

## 1. Executive Summary & Problem Statement
In coffee processing, contamination by foreign bodies (such as stones, pebbles, dirt clods, and wood fragments) frequently occurs during harvesting, sun-drying on open yards/patios, and bulk transport. When roasted coffee contains stones:
1. They severely damage commercial coffee grinders, burrs, and industrial milling machinery.
2. They ruin product purity, violate food safety regulations, and reduce commercial cup grade.

Conventional physical sorting methods exhibit distinct operational vulnerabilities:
- **Manual Hand-Sorting:** Labor-intensive, subjective, fatigue-prone, and slow.
- **Optical Color Sorters:** Rely on RGB/monochrome camera contrast. When stones are dark-colored or coated with coffee oil/roast dust, optical contrast drops to near zero, causing false negatives.
- **Pneumatic Destoners / Specific Gravity Separators:** Separate beans based on aerodynamic terminal velocity and density differences; however, stones of specific sizes/aerodynamic profiles or porous volcanic rocks can pass through undetected.

This study proposes an automated inspection approach using **Active Infrared Thermography** coupled with real-time digital thermal image processing on a conveyor system.

---

## 2. Theoretical Principles & System Architecture
Active thermography relies on the Stefan-Boltzmann law and differences in surface thermal emissivity ($\varepsilon$) and volumetric heat capacity ($C_p$) between roasted coffee beans and foreign bodies:

$$E(T) = \varepsilon \sigma T^4$$

Where:
- $\sigma = 5.67 \times 10^{-8} \text{ W} \cdot \text{m}^{-2} \cdot \text{K}^{-4}$ (Stefan-Boltzmann constant)
- $\varepsilon$ depends on material composition, surface roughness, and temperature.

### Hardware & Process Flow:
1. **Conveyor Transport:** PLC-controlled conveyor moves sample trays across an inspection line.
2. **Thermal Excitation Stage:** An external heat source (100W halogen lamp) heats the stopped tray for **50 seconds** to reach approximately $40^\circ\text{C}$.
3. **Detection & Transit Window:** The tray moves across the camera field in a **4.0-second** transit window. The optimal detection window occurs within the **first 1.0 second** of movement, where the temperature gradient between rapidly cooling coffee beans and heat-retaining stones is maximal.
4. **Detection Camera:** FLIR A315 infrared thermal imaging camera (spectral range 7.5–13 $\mu\text{m}$, thermal sensitivity $< 50\text{ mK}$, resolution $320 \times 240$ pixels, span calibrated 27–47 °C).
5. **Image Processing & Performance:** Image segmentation, thresholding, and morphological filtering running on FLIR IR Camera Player and custom software. Achieves **100% stone identification** across all test batches and **96% automated object count accuracy** (48/50 correct).

---

## 3. Empirical Measurements & Material Thermal Properties
From experimental calibration (using an aluminum hot-water bath plate at 85 °C and reference thermocouples), the thermal emissivity values were determined:

| Material | Measured Emissivity ($\varepsilon$) | Thermal Behavior Post-Stimulation (Cooling Curve) |
| :--- | :--- | :--- |
| **Roasted Coffee Bean** | **0.75 – 0.78** | **Rapid heat dissipation / sharp temperature decline** |
| **Stone (Foreign Body)** | **0.80 – 0.85** | **High heat retention / near-constant temperature plateau** |

### Thermal Cooling Dynamics & Detection Window:
- After a 4-second heating stimulation, stones maintained a significantly higher surface temperature because rock has a higher density, higher thermal capacity, and higher emissivity compared to the porous, low-density cellular structure of roasted coffee.
- **Optimal Detection Window:** The **first 1.0 second** immediately after the sample tray exits the heater and enters the camera field of view. During this first second, the differential temperature ($\Delta T$) between stone and coffee bean is at its maximum peak, providing optimal contrast for binary threshold segmentation.

---

## 4. Key Performance Results & Technical Gaps
- **Defect Detection Rate:** The active thermography system achieved **100% detection of foreign bodies across all test batches** (every stone was identified, even when visually indistinguishable from dark-roasted coffee beans).
- **Limitation / Gaps:** Object counting accuracy exhibited errors during automated batch counting. False counts occurred due to image segmentation boundary overlap between stones and the edges of the sample holding tray. The authors highlighted that advanced contour segmentation and edge masking are required for industrial deployment.

---

## 5. Industrial Real-Life Quality Guidelines
- **Target Parameter:** 0% foreign body tolerance in roasted whole bean coffee (Specialty & Commercial Grade 1).
- **Physical Property Differential:** Emissivity differential of $\Delta \varepsilon \approx 0.05 - 0.10$ and thermal dissipation latency can serve as an online inline inspection standard where color sorting fails.
