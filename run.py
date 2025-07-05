import streamlit as st
import math

# ===============================
# SOLAR PV SIZING CALCULATOR FOR HPC/ASIC DATA CENTERS
# ===============================

PROJECT_REFERENCE = {
    "ca_pv_ed_ac_capacity": 38.9,  # MWac
    "ca_pv_ed_dc_capacity": 50.6,  # MWdc  
    "ca_pv_ed_modules": 80912,
    "ca_pv_ed_module_power": 625,  # W
    "ca_pv_ed_area": 71.2,  # ha suitable area
    "ca_pv_ed_inverters": 12,
    "ca_pv_ed_inverter_power": 3600,  # kVA
    "dc_ac_ratio": 1.30,
    "gcr": 52.57,  # Ground Coverage Ratio %
    "tilt_angle": 18.0,  # degrees
    "azimuth_angle": 0.0  # degrees
}

ALBERTA_SOLAR = {
    "capacity_factor": 0.20,  # 20% capacity factor for Alberta
    "annual_irradiance": 1276,  # kWh/kW/yr
    "monthly_ghi": [28.1, 51.8, 100.0, 136.1, 172.1, 176.2, 179.7, 151.8, 102.0, 59.7, 30.7, 21.0],  # kWh/m²
    "monthly_temp": [-8.47, -2.16, -5.69, 2.17, 11.25, 14.75, 18.2, 15.98, 10.3, 3.13, -7.41, -12.95],  # °C
    "location": {"latitude": 53.49, "longitude": -114.49, "altitude": 742.26}
}

# ===============================
# MATHEMATICAL FORMULAS
# ===============================

def calculate_data_center_total_power(dc_capacity_mw, pue=1.2):
    return dc_capacity_mw * pue

def calculate_solar_capacity_needed(total_power_mw, capacity_factor=0.20):
    return total_power_mw / capacity_factor

def calculate_dc_capacity(ac_capacity_mw, dc_ac_ratio=1.30):
    return ac_capacity_mw * dc_ac_ratio

def calculate_module_count(ac_capacity_mw, module_power_w=625):
    modules_per_mw = PROJECT_REFERENCE["ca_pv_ed_modules"] / PROJECT_REFERENCE["ca_pv_ed_ac_capacity"]
    return int(ac_capacity_mw * modules_per_mw)

def calculate_land_area(ac_capacity_mw):
    area_per_mw = PROJECT_REFERENCE["ca_pv_ed_area"] / PROJECT_REFERENCE["ca_pv_ed_ac_capacity"]
    ha = ac_capacity_mw * area_per_mw
    acres = ha * 2.47105
    return ha, acres

def calculate_inverter_count(ac_capacity_mw, inverter_power_kva=3600):
    inverters_per_mw = PROJECT_REFERENCE["ca_pv_ed_inverters"] / PROJECT_REFERENCE["ca_pv_ed_ac_capacity"]
    return math.ceil(ac_capacity_mw * inverters_per_mw)

def calculate_string_configuration(module_count, modules_per_string=26):
    total_strings = math.ceil(module_count / modules_per_string)
    return total_strings, modules_per_string

def calculate_transformer_count(ac_capacity_mw, transformer_mva=7.2):
    return math.ceil(ac_capacity_mw / transformer_mva)

def calculate_power_station_count(ac_capacity_mw, station_capacity_mw=6.485):
    return math.ceil(ac_capacity_mw / station_capacity_mw)

def calculate_civil_works(land_area_ha):
    perimeter_fence = math.sqrt(land_area_ha * 10000) * 4 * 1.2
    road_length = land_area_ha * 400
    return perimeter_fence, road_length

def calculate_electrical_configuration(ac_capacity_mw):
    dc_losses = 2.0
    ac_losses = 1.0
    mv_voltage = 20.0
    string_voltage = 26 * 41.1
    return dc_losses, ac_losses, mv_voltage, string_voltage

def calculate_annual_energy_production(ac_capacity_mw, capacity_factor=0.20):
    return ac_capacity_mw * 8760 * capacity_factor

def calculate_monthly_production(ac_capacity_mw):
    monthly_production = []
    for ghi in ALBERTA_SOLAR["monthly_ghi"]:
        monthly_cf = (ghi / 150) * ALBERTA_SOLAR["capacity_factor"]
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        monthly_idx = len(monthly_production)
        if monthly_idx < 12:
            monthly_energy = ac_capacity_mw * 24 * days_in_month[monthly_idx] * monthly_cf
            monthly_production.append(monthly_energy)
    return monthly_production

# ===============================
# STREAMLIT DASHBOARD
# ===============================

def create_solar_calculator():
    st.set_page_config(page_title="Solar PV Calculator for HPC/ASIC Data Centers", layout="wide")
    st.markdown(
        "<h1 style='text-align: center; color: #FFB300;'> Solar PV Plant Sizing Calculator</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='text-align: center; color: #666;'>For HPC/ASIC Crypto Mining Data Centers in Alberta, Canada<br><i>Based on CA_PV_ED Project Design Parameters</i></div>",
        unsafe_allow_html=True
    )
    st.sidebar.image("https://img.icons8.com/ios-filled/100/solar-panel.png", width=80)
    st.sidebar.header(" Data Center Configuration")
    dc_capacity = st.sidebar.slider(
        "Data Center Power Capacity (MW)", 
        min_value=1.0, 
        max_value=10.0, 
        value=5.0, 
        step=0.5
    )
    pue = st.sidebar.slider(
        "Power Usage Effectiveness (PUE)", 
        min_value=1.1, 
        max_value=1.5, 
        value=1.2, 
        step=0.1
    )
    capacity_factor = st.sidebar.slider(
        "Solar Capacity Factor (%)", 
        min_value=15, 
        max_value=25, 
        value=20, 
        step=1
    ) / 100

    st.markdown("---")
    st.subheader(" Key Sizing Results")
    total_power = calculate_data_center_total_power(dc_capacity, pue)
    solar_ac_capacity = calculate_solar_capacity_needed(total_power, capacity_factor)
    solar_dc_capacity = calculate_dc_capacity(solar_ac_capacity)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Data Center Load", f"{dc_capacity:.1f} MW")
    kpi2.metric("Total Power (PUE)", f"{total_power:.1f} MW")
    kpi3.metric("Solar AC Capacity", f"{solar_ac_capacity:.1f} MWac")
    kpi4.metric("Solar DC Capacity", f"{solar_dc_capacity:.1f} MWdc")

    st.markdown("---")
    st.header("Site Specifications")
    st.subheader("Location")
    loc1, loc2, loc3 = st.columns(3)
    loc1.metric("Latitude", f"{ALBERTA_SOLAR['location']['latitude']}°")
    loc2.metric("Longitude", f"{ALBERTA_SOLAR['location']['longitude']}°")
    loc3.metric("Altitude", f"{ALBERTA_SOLAR['location']['altitude']} m")

    st.subheader("Plot Areas")
    land_area_ha, land_area_acres = calculate_land_area(solar_ac_capacity)
    fence_area = land_area_ha * 0.937
    pa1, pa2, pa3 = st.columns(3)
    pa1.metric("Total Area", f"{land_area_ha:.1f} ha")
    pa2.metric("Total Area", f"{land_area_acres:.1f} acres")
    pa3.metric("Fence Area", f"{fence_area:.1f} ha")

    st.subheader("Topography")
    st.info(
        f"**Optimal Tilt Angle:** {PROJECT_REFERENCE['tilt_angle']}°\n\n"
        f"**Azimuth Angle:** {PROJECT_REFERENCE['azimuth_angle']}°\n\n"
        f"**Ground Coverage Ratio:** {PROJECT_REFERENCE['gcr']}%"
    )

    st.subheader("Horizon Profile")
    st.success("Average Horizon Elevation: 1.0°\n\nEstimated Annual Blocked Hours: Based on terrain analysis")

    st.markdown("---")
    st.header("Solar Resource")
    annual_energy = calculate_annual_energy_production(solar_ac_capacity, capacity_factor)
    monthly_energy = calculate_monthly_production(solar_ac_capacity)
    sr1, sr2 = st.columns(2)
    sr1.metric("Annual Energy Production", f"{annual_energy:.0f} MWh/year")
    sr1.metric("Annual Solar Irradiance", f"{ALBERTA_SOLAR['annual_irradiance']} kWh/kW/yr")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_chart_data = {month: energy for month, energy in zip(months, monthly_energy)}
    sr2.subheader("Monthly Energy Production (MWh)")
    sr2.line_chart(monthly_chart_data)

    st.markdown("---")
    st.header("Equipment")
    st.subheader("Photovoltaic Module")
    module_count = calculate_module_count(solar_ac_capacity)
    me1, me2 = st.columns(2)
    with me1:
        st.write("**Module Model:** LR8-66HGD-625M Bifacial")
        st.write("**Manufacturer:** Longi Solar")
        st.write("**Technology:** Si-mono Bifacial")
        st.write(f"**Peak Power:** {PROJECT_REFERENCE['ca_pv_ed_module_power']} W")
    with me2:
        st.metric("Total Modules", f"{module_count:,}")
        st.write("**Efficiency:** 23.14%")
        st.write("**Bifaciality Factor:** 80%")

    st.subheader("Fixed Structure")
    total_strings, modules_per_string = calculate_string_configuration(module_count)
    structures_needed = math.ceil(module_count / 52)
    fs1, fs2 = st.columns(2)
    fs1.metric("Structures", f"{structures_needed:,}")
    fs1.metric("Total Strings", f"{total_strings:,}")
    fs2.write(f"**Modules per String:** {modules_per_string}")
    fs2.write("**Structure Type:** 3P (Portrait)")
    fs2.write("**Min Ground Clearance:** 0.8 m")

    st.subheader("String Combiner Box")
    combiner_boxes = math.ceil(total_strings / 16)
    st.metric("String Combiner Boxes", f"{combiner_boxes}")
    st.write("**Inputs per Box:** 16 strings")
    st.write("**Protection:** Fuses, DC switch, overvoltage arresters")

    st.subheader("Central Inverter")
    inverter_count = calculate_inverter_count(solar_ac_capacity)
    ci1, ci2 = st.columns(2)
    ci1.metric("Inverters", f"{inverter_count}")
    ci1.write("**Model:** SG3600UD-MV_T2")
    ci1.write("**Manufacturer:** Sungrow")
    ci2.write(f"**Rated Power:** {PROJECT_REFERENCE['ca_pv_ed_inverter_power']} kVA")
    ci2.write("**Efficiency:** 98.90%")
    ci2.write("**Output Voltage:** 630 V")

    st.subheader("Power Transformer")
    transformer_count = calculate_transformer_count(solar_ac_capacity)
    st.metric("Transformers", f"{transformer_count}")
    st.write("**Voltage Ratio:** 0.63/20.0 kV")
    st.write("**Rating:** 7.2 MVA each")
    st.write("**Cooling:** ONAN")

    st.subheader("Power Station")
    station_count = calculate_power_station_count(solar_ac_capacity)
    st.metric("Power Stations", f"{station_count}")
    st.write("**Type:** Outdoor")
    st.write("**Configuration:** Integrated inverter and transformer")

    st.markdown("---")
    st.header("PV Plant Sizing")
    st.subheader("Electrical Configuration")
    dc_losses, ac_losses, mv_voltage, string_voltage = calculate_electrical_configuration(solar_ac_capacity)
    ec1, ec2 = st.columns(2)
    ec1.write(f"**Plant Rated Power:** {solar_ac_capacity:.1f} MWac")
    ec1.write(f"**Plant Peak Power:** {solar_dc_capacity:.1f} MWdc")
    ec1.write(f"**DC/AC Ratio:** {PROJECT_REFERENCE['dc_ac_ratio']}")
    ec2.write(f"**String Voltage:** {string_voltage:.0f} V")
    ec2.write(f"**MV Network Voltage:** {mv_voltage} kV")
    ec2.write(f"**Modules per String:** {modules_per_string}")

    st.subheader("Electrical Cabling Design")
    cab1, cab2 = st.columns(2)
    cab1.write(f"**DC Losses:** {dc_losses}%")
    cab1.write(f"**AC Losses:** {ac_losses}%")
    cab1.write("**DC Cable Material:** Aluminum XLPE")
    cab2.write("**AC Cable Material:** Aluminum XLPE")
    cab2.write("**Installation:** Buried in trenches")
    cab2.write("**Max Voltage Drop:** 1.6% DC, 0.5% AC")

    st.subheader("Civil Works")
    perimeter_fence, road_length = calculate_civil_works(land_area_ha)
    cw1, cw2 = st.columns(2)
    cw1.write(f"**Perimeter Fence:** {perimeter_fence/1000:.2f} km")
    cw1.write(f"**Access Roads:** {road_length/1000:.2f} km")
    cw1.write("**Road Width:** 5.0 m")
    cw2.write("**Fence Height:** 2.0 m minimum")
    cw2.write("**Security:** Lighting and monitoring systems")
    cw2.write("**Drainage:** Road ditches included")

    st.markdown("---")
    st.header("Project Summary")
    sum1, sum2, sum3, sum4 = st.columns(4)
    sum1.metric("Total Investment", "Contact for Quote")
    sum1.metric("Construction Time", "12-18 months")
    sum2.metric("Annual CO₂ Savings", f"{annual_energy * 0.4:.0f} tonnes")
    sum2.metric("Project Lifetime", "25+ years")
    sum3.metric("Performance Ratio", "85-90%")
    sum3.metric("System Availability", "98%+")
    sum4.metric("Maintenance Cost", "1-2% of CAPEX/year")
    sum4.metric("Degradation Rate", "0.5%/year")

if __name__ == "__main__":
    create_solar_calculator()
