# ☀️ Solar PV Plant Sizing Calculator for HPC/ASIC Data Centers

This Streamlit application is a **comprehensive sizing and design tool** for solar photovoltaic (PV) power plants meant to supply energy to **High Performance Computing (HPC)** and **ASIC Crypto Mining Data Centers** in **Alberta, Canada**.  
It calculates the technical and spatial requirements to power data centers using solar energy, leveraging real-world project data and Alberta's solar resource characteristics.

---

## 🧠 Motivation

HPC and crypto mining data centers are **power-intensive**, requiring stable and often massive energy supplies. This tool enables engineers, energy consultants, and project developers to:

- Evaluate solar PV sizing requirements for specific data center capacities
- Analyze site and equipment needs
- Estimate energy production
- Visualize technical breakdowns and monthly generation
- Benchmark against a real Canadian utility-scale PV plant (CA_PV_ED)

---

## 📌 Project Reference – CA_PV_ED

The calculator uses the real-world specifications from the **CA_PV_ED** utility-scale PV project (presumably located in Alberta or similar region) as a **scaling reference**. This includes:

- AC/DC capacity (MWac and MWdc)
- Module count and power
- Inverter details
- Ground coverage ratio (GCR)
- Land area per MW
- Module string configuration
- Electrical losses and design parameters


## 🚀 Features

### 1. **Interactive Inputs (Streamlit Sidebar)**

| Input                          | Description                                                 |
|-------------------------------|-------------------------------------------------------------|
| **Data Center Power (MW)**     | User selects HPC/ASIC load (1–10 MW)                        |
| **PUE (Power Usage Effectiveness)** | Multiplier for actual facility energy needs (1.1–1.5 typical) |
| **Solar Capacity Factor**      | Adjusts to site irradiance quality (15%–25%)                |

---

### 2. **Main Outputs**

#### ⚙️ Technical Sizing:

| Metric                   | Description |
|--------------------------|-------------|
| **Total Power (MW)**     | Data Center Load × PUE |
| **Solar AC Capacity**    | Total Power ÷ Capacity Factor |
| **Solar DC Capacity**    | AC × DC/AC Ratio (1.3 by default) |

---

### 3. **Site Requirements**

| Component         | Description |
|------------------|-------------|
| **Land Area (ha/acres)** | Estimated based on reference plant |
| **Fence Area**    | 93.7% of land area |
| **Topography**    | Displays tilt, azimuth, and GCR from CA_PV_ED |
| **Horizon Profile** | Static assumption for terrain blocking |

---

### 4. **Solar Resource**

Pulls from Alberta solar resource data:

| Metric | Description |
|--------|-------------|
| **Annual Irradiance** | 1276 kWh/kW/yr |
| **Monthly GHI (Global Horizontal Irradiance)** | Used to compute month-by-month production |
| **Monthly Temperatures** | Currently for reference, not used directly in calculations |

🔋 **Energy Production:**

- **Annual**: AC Capacity × 8760 × Capacity Factor
- **Monthly**: Adjusted with normalized GHI and day count

---

### 5. **Main Equipment**

Breaks down all physical equipment required:

| Equipment          | Description |
|-------------------|-------------|
| **PV Modules**     | Longi LR8-66HGD-625M |
| **Structures**     | 3P (3-portrait) frames, ~52 modules/structure |
| **Strings**        | ~26 modules per string |
| **Combiner Boxes** | 16-string inputs each |
| **Central Inverters** | 3.6 MVA, Sungrow SG3600UD |
| **Power Transformers** | 7.2 MVA, 0.63/20kV |
| **Power Stations** | Combines inverter + transformer (6.485 MW per unit) |

---

### 6. **Electrical Configuration**

| Parameter         | Value            |
|------------------|------------------|
| DC Losses        | 2%               |
| AC Losses        | 1%               |
| MV Voltage       | 20 kV            |
| String Voltage   | 26 modules × 41.1 V = 1069 V |
| DC/AC Ratio      | 1.3              |

---

### 7. **Civil Works**

| Component        | Formula Used |
|------------------|--------------|
| **Perimeter Fence** | √(Area in m²) × 4 × 1.2 |
| **Access Roads**    | 400 m/km per hectare |

Includes security (fencing, lighting), and drainage design assumptions.

---

### 8. **Summary Metrics**

| Metric                 | Value (Example) |
|------------------------|-----------------|
| **Annual CO₂ Savings** | Annual MWh × 0.4 tonnes CO₂ offset |
| **Lifetime**           | 25+ years |
| **Performance Ratio**  | 85–90% |
| **System Availability**| 98%+ |
| **O&M Cost**           | 1–2% of CAPEX/year |
| **Degradation**        | 0.5% per year |

---

## 📊 Technologies Used

- **Python 3.9+**
- **[Streamlit](https://streamlit.io/)** – Dashboard framework
- **Matplotlib/Altair** – Charting
- **Pandas/Numpy** – Data manipulation
- **Math** – Engineering calculations

---

## 🏗️ How It Works

### 📈 Core Calculation Flow:

```python
1. Total Power = Data Center Capacity × PUE
2. Solar AC Capacity = Total Power ÷ Capacity Factor
3. DC Capacity = AC Capacity × 1.3 (DC/AC ratio)
4. Module Count = AC Capacity × Scaling Factor
5. Land Area = AC Capacity × Scaling Factor
6. Strings = Module Count ÷ Modules per String
7. Equipment (Inverters, Transformers, Stations) = Based on plant AC capacity
8. Monthly Energy = AC × 24 × Days × (GHI_norm × CF)
