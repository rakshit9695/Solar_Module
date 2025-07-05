import streamlit as st
import math

# ===============================
# SOLAR PV SIZING CALCULATOR FOR HPC/ASIC DATA CENTERS
# ===============================

# Based on CA_PV_ED Project and Alberta Solar Resource Data
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

# Alberta Solar Resource Constants
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
    """Calculate total power including PUE"""
    return dc_capacity_mw * pue

def calculate_solar_capacity_needed(total_power_mw, capacity_factor=0.20):
    """Calculate required solar AC capacity"""
    return total_power_mw / capacity_factor

def calculate_dc_capacity(ac_capacity_mw, dc_ac_ratio=1.30):
    """Calculate DC capacity from AC capacity"""
    return ac_capacity_mw * dc_ac_ratio

def calculate_module_count(ac_capacity_mw, module_power_w=625):
    """Calculate number of PV modules required"""
    # Using CA_PV_ED scaling factor
    modules_per_mw = PROJECT_REFERENCE["ca_pv_ed_modules"] / PROJECT_REFERENCE["ca_pv_ed_ac_capacity"]
    return int(ac_capacity_mw * modules_per_mw)

def calculate_land_area(ac_capacity_mw):
    """Calculate land area in hectares and acres"""
    # Using CA_PV_ED scaling factor  
    area_per_mw = PROJECT_REFERENCE["ca_pv_ed_area"] / PROJECT_REFERENCE["ca_pv_ed_ac_capacity"]
    ha = ac_capacity_mw * area_per_mw
    acres = ha * 2.47105  # Convert hectares to acres
    return ha, acres

def calculate_inverter_count(ac_capacity_mw, inverter_power_kva=3600):
    """Calculate number of inverters required"""
    inverters_per_mw = PROJECT_REFERENCE["ca_pv_ed_inverters"] / PROJECT_REFERENCE["ca_pv_ed_ac_capacity"]
    return math.ceil(ac_capacity_mw * inverters_per_mw)

def calculate_string_configuration(module_count, modules_per_string=26):
    """Calculate string configuration"""
    total_strings = math.ceil(module_count / modules_per_string)
    return total_strings, modules_per_string

def calculate_transformer_count(ac_capacity_mw, transformer_mva=7.2):
    """Calculate number of transformers required"""
    return math.ceil(ac_capacity_mw / transformer_mva)

def calculate_power_station_count(ac_capacity_mw, station_capacity_mw=6.485):
    """Calculate number of power stations required"""
    return math.ceil(ac_capacity_mw / station_capacity_mw)

def calculate_civil_works(land_area_ha):
    """Calculate civil works requirements"""
    perimeter_fence = math.sqrt(land_area_ha * 10000) * 4 * 1.2  # 20% additional for irregular shape
    road_length = land_area_ha * 400  # Estimated road density
    return perimeter_fence, road_length

def calculate_electrical_configuration(ac_capacity_mw):
    """Calculate electrical system parameters"""
    dc_losses = 2.0  # % DC cabling losses
    ac_losses = 1.0  # % AC cabling losses
    mv_voltage = 20.0  # kV medium voltage
    string_voltage = 26 * 41.1  # modules per string * Vmpp
    return dc_losses, ac_losses, mv_voltage, string_voltage

def calculate_annual_energy_production(ac_capacity_mw, capacity_factor=0.20):
    """Calculate annual energy production"""
    return ac_capacity_mw * 8760 * capacity_factor  # MWh/year

def calculate_monthly_production(ac_capacity_mw):
    """Calculate monthly energy production"""
    monthly_production = []
    for ghi in ALBERTA_SOLAR["monthly_ghi"]:
        # Simplified calculation based on GHI variation
        monthly_cf = (ghi / 150) * ALBERTA_SOLAR["capacity_factor"]  # Normalized to peak month
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
    """Create the Streamlit dashboard"""
    st.set_page_config(page_title="Solar PV Calculator for HPC/ASIC Data Centers", layout="wide")
    
    # Header
    st.title("🌞 Solar PV Plant Sizing Calculator")
    st.markdown("**For HPC/ASIC Crypto Mining Data Centers in Alberta, Canada**")
    st.markdown("*Based on CA_PV_ED Project Design Parameters*")
    
    # Sidebar inputs
    st.sidebar.header("Data Center Configuration")
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
    
    # Main calculations
    total_power = calculate_data_center_total_power(dc_capacity, pue)
    solar_ac_capacity = calculate_solar_capacity_needed(total_power, capacity_factor)
    solar_dc_capacity = calculate_dc_capacity(solar_ac_capacity)
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Data Center Load", f"{dc_capacity:.1f} MW")
    with col2:
        st.metric("Total Power (w/ PUE)", f"{total_power:.1f} MW")
    with col3:
        st.metric("Solar AC Capacity", f"{solar_ac_capacity:.1f} MWac")
    with col4:
        st.metric("Solar DC Capacity", f"{solar_dc_capacity:.1f} MWdc")
    
    # Site Analysis
    st.header("2. SITE")
    
    # Location
    st.subheader("2.1. Location")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Latitude:** {ALBERTA_SOLAR['location']['latitude']}°")
        st.write(f"**Longitude:** {ALBERTA_SOLAR['location']['longitude']}°")
        st.write(f"**Altitude:** {ALBERTA_SOLAR['location']['altitude']} m")
    
    # Plot Areas
    st.subheader("2.2. Plot Areas")
    land_area_ha, land_area_acres = calculate_land_area(solar_ac_capacity)
    fence_area = land_area_ha * 0.937  # Based on CA_PV_ED ratio
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Area Required", f"{land_area_ha:.1f} ha")
    with col2:
        st.metric("Total Area (Acres)", f"{land_area_acres:.1f} acres")
    with col3:
        st.metric("Fence Area", f"{fence_area:.1f} ha")
    
    # Topography
    st.subheader("2.3. Topography")
    st.write(f"**Optimal Tilt Angle:** {PROJECT_REFERENCE['tilt_angle']}°")
    st.write(f"**Azimuth Angle:** {PROJECT_REFERENCE['azimuth_angle']}°")
    st.write(f"**Ground Coverage Ratio:** {PROJECT_REFERENCE['gcr']}%")
    
    # Horizon Profile
    st.subheader("2.4. Horizon Profile")
    st.write("**Average Horizon Elevation:** 1.0°")
    st.write("**Estimated Annual Blocked Hours:** Based on terrain analysis")
    
    # Solar Resource
    st.header("3. SOLAR RESOURCE")
    annual_energy = calculate_annual_energy_production(solar_ac_capacity, capacity_factor)
    monthly_energy = calculate_monthly_production(solar_ac_capacity)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Annual Energy Production", f"{annual_energy:.0f} MWh/year")
        st.metric("Annual Solar Irradiance", f"{ALBERTA_SOLAR['annual_irradiance']} kWh/kW/yr")
    with col2:
        # Monthly production chart
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        monthly_chart_data = {month: energy for month, energy in zip(months, monthly_energy)}
        st.subheader("Monthly Energy Production (MWh)")
        st.line_chart(monthly_chart_data)
    
    # Main Equipment
    st.header("4. MAIN EQUIPMENT")
    
    # PV Modules
    st.subheader("4.1. Photovoltaic Module")
    module_count = calculate_module_count(solar_ac_capacity)
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Module Model:** LR8-66HGD-625M Bifacial")
        st.write("**Manufacturer:** Longi Solar")
        st.write("**Technology:** Si-mono Bifacial")
        st.write(f"**Peak Power:** {PROJECT_REFERENCE['ca_pv_ed_module_power']} W")
    with col2:
        st.metric("Total Modules Required", f"{module_count:,}")
        st.write("**Efficiency:** 23.14%")
        st.write("**Bifaciality Factor:** 80%")
    
    # Fixed Structure
    st.subheader("4.2. Fixed Structure")
    total_strings, modules_per_string = calculate_string_configuration(module_count)
    structures_needed = math.ceil(module_count / 52)  # 52 modules per structure from CA_PV_ED
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Structures Required", f"{structures_needed:,}")
        st.metric("Total Strings", f"{total_strings:,}")
    with col2:
        st.write(f"**Modules per String:** {modules_per_string}")
        st.write("**Structure Type:** 3P (Portrait)")
        st.write("**Minimum Ground Clearance:** 0.8 m")
    
    # String Combiner Box
    st.subheader("4.3. String Combiner Box")
    combiner_boxes = math.ceil(total_strings / 16)  # 16 strings per combiner
    st.metric("String Combiner Boxes", f"{combiner_boxes}")
    st.write("**Inputs per Box:** 16 strings")
    st.write("**Protection:** Fuses, DC switch, overvoltage arresters")
    
    # Central Inverter
    st.subheader("4.4. Central Inverter")
    inverter_count = calculate_inverter_count(solar_ac_capacity)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Inverters Required", f"{inverter_count}")
        st.write("**Model:** SG3600UD-MV_T2")
        st.write("**Manufacturer:** Sungrow")
    with col2:
        st.write(f"**Rated Power:** {PROJECT_REFERENCE['ca_pv_ed_inverter_power']} kVA")
        st.write("**Efficiency:** 98.90%")
        st.write("**Output Voltage:** 630 V")
    
    # Power Transformer
    st.subheader("4.5. Power Transformer")
    transformer_count = calculate_transformer_count(solar_ac_capacity)
    st.metric("Transformers Required", f"{transformer_count}")
    st.write("**Voltage Ratio:** 0.63/20.0 kV")
    st.write("**Rating:** 7.2 MVA each")
    st.write("**Cooling:** ONAN")
    
    # Power Station
    st.subheader("4.6. Power Station")
    station_count = calculate_power_station_count(solar_ac_capacity)
    st.metric("Power Stations Required", f"{station_count}")
    st.write("**Type:** Outdoor")
    st.write("**Configuration:** Integrated inverter and transformer")
    
    # PV Plant Sizing
    st.header("5. PV PLANT SIZING")
    
    # Electrical Configuration
    st.subheader("5.1. Electrical Configuration")
    dc_losses, ac_losses, mv_voltage, string_voltage = calculate_electrical_configuration(solar_ac_capacity)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Plant Rated Power:** {solar_ac_capacity:.1f} MWac")
        st.write(f"**Plant Peak Power:** {solar_dc_capacity:.1f} MWdc")
        st.write(f"**DC/AC Ratio:** {PROJECT_REFERENCE['dc_ac_ratio']}")
    with col2:
        st.write(f"**String Voltage:** {string_voltage:.0f} V")
        st.write(f"**MV Network Voltage:** {mv_voltage} kV")
        st.write(f"**Modules per String:** {modules_per_string}")
    
    # Electrical Cabling Design
    st.subheader("5.2. Electrical Cabling Design")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**DC Losses:** {dc_losses}%")
        st.write(f"**AC Losses:** {ac_losses}%")
        st.write("**DC Cable Material:** Aluminum XLPE")
    with col2:
        st.write("**AC Cable Material:** Aluminum XLPE")
        st.write("**Installation:** Buried in trenches")
        st.write("**Maximum Voltage Drop:** 1.6% DC, 0.5% AC")
    
    # Civil Works
    st.subheader("5.3. Civil Works")
    perimeter_fence, road_length = calculate_civil_works(land_area_ha)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Perimeter Fence:** {perimeter_fence/1000:.2f} km")
        st.write(f"**Access Roads:** {road_length/1000:.2f} km")
        st.write("**Road Width:** 5.0 m")
    with col2:
        st.write("**Fence Height:** 2.0 m minimum")
        st.write("**Security:** Lighting and monitoring systems")
        st.write("**Drainage:** Road ditches included")
    
    # Summary
    st.header("📊 Project Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Investment", "Contact for Quote")
        st.metric("Construction Time", "12-18 months")
    with col2:
        st.metric("Annual CO₂ Savings", f"{annual_energy * 0.4:.0f} tonnes")
        st.metric("Project Lifetime", "25+ years")
    with col3:
        st.metric("Performance Ratio", "85-90%")
        st.metric("System Availability", "98%+")
    with col4:
        st.metric("Maintenance Cost", "1-2% of CAPEX/year")
        st.metric("Degradation Rate", "0.5%/year")

# Run the dashboard
if __name__ == "__main__":
    create_solar_calculator()
