# Solar_Module

# 🌞 Solar PV Plant Analysis Dashboard

A comprehensive **Streamlit dashboard** for analyzing the **CA_PV_ED Solar PV Project** in **Highvale, Alberta, Canada**. This tool provides clear, formula-based insights into the site, resource, equipment, and system configuration — entirely using **built-in Python functions** and **Streamlit** for visualization.

---

## 🚀 Features

### 📍 Site Analysis
- Location coordinates and altitude
- Plot area vs. usable area estimation
- Topography and slope analysis
- Horizon profile impact on solar resource

### ☀️ Solar Resource Analysis
- Monthly **Global Horizontal Irradiance (GHI)**
- **Plane of Array (POA)** calculations based on tilt/azimuth
- Temperature modeling (ambient & module)
- Astronomical solar position tracking

### ⚙️ Equipment Performance
- PV module power output with temperature correction
- Fixed mounting system and **shading analysis** via GCR
- Efficiency modeling for:
  - String combiner
  - Central inverter (load-based)
  - Power transformer
- Full power station integration

### 🔧 System Configuration
- DC/AC electrical sizing and voltage design
- DC/AC cable losses
- Civil infrastructure and impact modeling

---

## 📐 Key Mathematical Formulas

| **Parameter**         | **Formula**                                                                                     |
|----------------------|--------------------------------------------------------------------------------------------------|
| Solar Elevation       | $$ \text{asin}(\sin(\delta) \cdot \sin(\phi) + \cos(\delta) \cdot \cos(\phi) \cdot \cos(h)) $$  |
| Module Power Output   | $$ P = P_{rated} \cdot \frac{Irradiance}{1000} \cdot [1 + \alpha(T_{cell} - 25)] $$             |
| Capacity Factor       | $$ CF = \frac{Energy_{actual}}{Rated\ Capacity \cdot Hours} \cdot 100 $$                        |
| Performance Ratio     | $$ PR = \frac{Energy_{actual}}{Energy_{theoretical}} \cdot 100 $$                               |
| Shading Losses        | $$ Loss = [1 - GCR \cdot (1/\tan(solar\_elevation))] \cdot 100\% $$                              |

---

## 📊 Dashboard Structure

- **Project Summary:** Key specifications and site layout
- **Monthly Analysis:** Interactive line charts (Net AC Output, PR, etc.)
- **Tabbed Layout:** Organized for efficient navigation
- **Performance Metrics:** Annual summaries, KPIs, and losses
- **Equipment Sizing:** Breakdown of modules, inverters, strings, etc.

---

## 🗂️ Project Specifications

| **Attribute**        | **Details**                            |
|----------------------|----------------------------------------|
| **Location**          | Highvale, Alberta (53.49°N, -114.49°W) |
| **Capacity**          | 50.6 MWdc / 38.9 MWac (DC/AC: 1.30)    |
| **Modules**           | 80,912 × 625W Longi Solar bifacial     |
| **Inverters**         | 12 × 3.6 MVA Sungrow central units     |
| **Area**              | 130.04 ha total, 71.2 ha usable        |

---

## ▶️ How to Run

1. **Save the script**  
   Save the file as: `solar_pv_dashboard.py`

2. **Install Streamlit**  
   ```bash
   pip install streamlit
