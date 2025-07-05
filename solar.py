
import math
import streamlit as st

# ===============================
# SOLAR PV PLANT ANALYSIS SYSTEM
# ===============================

# Project Configuration
PROJECT_CONFIG = {
    "project_name": "CA_PV_ED Project",
    "location": {"city": "Highvale", "region": "Alberta", "country": "Canada", 
                "latitude": 53.49, "longitude": -114.49, "altitude": 742.26},
    "rated_power_ac": 38.9,  # MWac
    "peak_power_dc": 50.6,   # MWdc
    "dc_ac_ratio": 1.30,
    "total_area": 130.04,    # ha
    "suitable_area": 71.2,   # ha
    "pv_modules": {"peak_power": 625.0, "quantity": 80912, "efficiency": 23.14},
    "inverters": {"quantity": 12, "rated_power": 3600.0, "efficiency": 98.90},
    "tilt_angle": 18.0,      # degrees
    "azimuth_angle": 0.0,    # degrees
    "monthly_ghi": [28.1, 51.8, 100.0, 136.1, 172.1, 176.2, 179.7, 151.8, 102.0, 59.7, 30.7, 21.0],
    "monthly_temp": [-8.47, -2.16, -5.69, 2.17, 11.25, 14.75, 18.2, 15.98, 10.3, 3.13, -7.41, -12.95]
}

# ===============================
# FORMULA DEFINITIONS
# ===============================

def calculate_solar_position(day_of_year, latitude, hour):
    """Calculate solar position parameters"""
    # Solar declination angle
    declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))

    # Hour angle
    hour_angle = 15 * (hour - 12)

    # Solar elevation angle
    elevation = math.asin(
        math.sin(math.radians(declination)) * math.sin(math.radians(latitude)) +
        math.cos(math.radians(declination)) * math.cos(math.radians(latitude)) * 
        math.cos(math.radians(hour_angle))
    )

    # Solar azimuth angle
    azimuth = math.atan2(
        math.sin(math.radians(hour_angle)),
        math.cos(math.radians(hour_angle)) * math.sin(math.radians(latitude)) - 
        math.tan(math.radians(declination)) * math.cos(math.radians(latitude))
    )

    return math.degrees(elevation), math.degrees(azimuth)

def calculate_irradiance_on_tilted_surface(ghi, tilt_angle, surface_azimuth, solar_elevation, solar_azimuth):
    """Calculate irradiance on tilted surface"""
    if solar_elevation <= 0:
        return 0

    # Angle of incidence
    cos_incidence = (
        math.sin(math.radians(solar_elevation)) * math.cos(math.radians(tilt_angle)) +
        math.cos(math.radians(solar_elevation)) * math.sin(math.radians(tilt_angle)) *
        math.cos(math.radians(solar_azimuth - surface_azimuth))
    )

    # Direct normal irradiance (simplified)
    dni = ghi * max(0, cos_incidence) / max(0.1, math.sin(math.radians(solar_elevation)))

    # Irradiance on tilted surface
    poa_irradiance = max(0, dni * cos_incidence + ghi * 0.1 * (1 + math.cos(math.radians(tilt_angle))) / 2)

    return poa_irradiance

def calculate_module_temperature(ambient_temp, irradiance, noct=45):
    """Calculate module temperature"""
    return ambient_temp + (noct - 20) * irradiance / 800

def calculate_power_output(irradiance, module_temp, module_power, temp_coeff=-0.0028):
    """Calculate power output considering temperature effects"""
    temp_factor = 1 + temp_coeff * (module_temp - 25)
    irradiance_factor = irradiance / 1000
    return module_power * irradiance_factor * temp_factor

def calculate_system_efficiency(ac_power, dc_power):
    """Calculate system efficiency"""
    return (ac_power / dc_power) * 100 if dc_power > 0 else 0

def calculate_performance_ratio(actual_energy, theoretical_energy):
    """Calculate performance ratio"""
    return (actual_energy / theoretical_energy) * 100 if theoretical_energy > 0 else 0

def calculate_capacity_factor(actual_energy, rated_capacity, hours):
    """Calculate capacity factor"""
    return (actual_energy / (rated_capacity * hours)) * 100

def calculate_specific_yield(energy_output, installed_capacity):
    """Calculate specific yield (kWh/kWp)"""
    return energy_output / installed_capacity

def calculate_shading_losses(gcr, solar_elevation):
    """Calculate shading losses based on GCR and solar elevation"""
    if solar_elevation <= 0:
        return 100

    # Simplified shading calculation
    shading_factor = max(0, 1 - (gcr / 100) * (1 / math.tan(math.radians(max(1, solar_elevation)))))
    return (1 - shading_factor) * 100

def calculate_inverter_efficiency(dc_power, rated_power):
    """Calculate inverter efficiency based on loading"""
    loading_ratio = dc_power / rated_power
    if loading_ratio <= 0.1:
        return 0.85
    elif loading_ratio <= 0.2:
        return 0.92
    elif loading_ratio <= 0.5:
        return 0.96
    elif loading_ratio <= 0.75:
        return 0.98
    elif loading_ratio <= 1.0:
        return 0.989
    else:
        return 0.985

# ===============================
# MONTHLY CALCULATIONS
# ===============================

def calculate_monthly_metrics(month_index):
    """Calculate all metrics for a given month"""
    config = PROJECT_CONFIG

    # Days in each month
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # Base values for the month
    monthly_ghi = config["monthly_ghi"][month_index]
    monthly_temp = config["monthly_temp"][month_index]
    days = days_in_month[month_index]

    # Daily averages
    daily_ghi = monthly_ghi / days

    # Calculate average daily solar position (assuming noon)
    avg_day = 15 + (month_index * 30)  # Approximate day of year
    solar_elevation, solar_azimuth = calculate_solar_position(avg_day, config["location"]["latitude"], 12)

    # Site characteristics
    site_metrics = {
        "latitude": config["location"]["latitude"],
        "longitude": config["location"]["longitude"],
        "altitude": config["location"]["altitude"],
        "total_area": config["total_area"],
        "suitable_area": config["suitable_area"],
        "utilization_ratio": (config["suitable_area"] / config["total_area"]) * 100
    }

    # Topography metrics
    topo_metrics = {
        "slope_impact": max(0, 100 - abs(config["tilt_angle"] - 30)),  # Optimal tilt impact
        "terrain_suitability": 85.0,  # Based on slopes < 15%
        "drainage_adequacy": 90.0     # Based on civil works design
    }

    # Horizon profile impact
    horizon_impact = max(0, 100 - (solar_elevation < 10) * 20)  # Simplified horizon blocking

    # Solar resource calculations
    poa_irradiance = calculate_irradiance_on_tilted_surface(
        daily_ghi, config["tilt_angle"], config["azimuth_angle"], 
        solar_elevation, solar_azimuth
    )

    module_temp = calculate_module_temperature(monthly_temp, poa_irradiance)

    solar_metrics = {
        "ghi": monthly_ghi,
        "poa_irradiance": poa_irradiance * days,
        "solar_elevation": solar_elevation,
        "ambient_temp": monthly_temp,
        "module_temp": module_temp,
        "irradiance_ratio": (poa_irradiance / daily_ghi) * 100 if daily_ghi > 0 else 0
    }

    # PV Module performance
    module_power = calculate_power_output(poa_irradiance, module_temp, config["pv_modules"]["peak_power"])
    total_dc_power = (module_power * config["pv_modules"]["quantity"]) / 1000  # kW

    pv_metrics = {
        "module_efficiency": config["pv_modules"]["efficiency"],
        "module_power_output": module_power,
        "total_dc_power": total_dc_power,
        "temperature_losses": ((module_temp - 25) * 0.28),  # % loss per degree
        "bifacial_gain": 5.0  # Simplified bifacial gain
    }

    # Fixed structure impact
    shading_losses = calculate_shading_losses(52.57, solar_elevation)  # GCR from document

    structure_metrics = {
        "shading_losses": shading_losses,
        "structural_efficiency": 95.0,  # Based on design
        "mounting_losses": 2.0  # Standard mounting losses
    }

    # String combiner efficiency
    combiner_efficiency = 99.5  # Typical string combiner efficiency

    # Inverter performance
    inverter_efficiency = calculate_inverter_efficiency(total_dc_power, config["inverters"]["rated_power"])
    total_ac_power = total_dc_power * inverter_efficiency

    inverter_metrics = {
        "efficiency": inverter_efficiency * 100,
        "loading_ratio": (total_dc_power / (config["inverters"]["rated_power"] * config["inverters"]["quantity"])) * 100,
        "total_ac_power": total_ac_power,
        "conversion_losses": (1 - inverter_efficiency) * 100
    }

    # Power transformer efficiency
    transformer_efficiency = 98.5  # Typical transformer efficiency

    # Power station metrics
    station_metrics = {
        "transformer_efficiency": transformer_efficiency,
        "switchgear_losses": 0.5,
        "auxiliary_consumption": 1.0,
        "total_station_efficiency": transformer_efficiency - 1.5
    }

    # Electrical configuration
    string_voltage = 26 * 41.1  # modules per string * Vmpp
    dc_losses = 2.0  # DC wiring losses
    ac_losses = 1.0  # AC wiring losses

    electrical_metrics = {
        "string_voltage": string_voltage,
        "dc_losses": dc_losses,
        "ac_losses": ac_losses,
        "total_electrical_losses": dc_losses + ac_losses,
        "grid_connection_efficiency": 99.0
    }

    # Civil works impact
    civil_metrics = {
        "road_accessibility": 95.0,
        "drainage_effectiveness": 90.0,
        "security_rating": 85.0,
        "maintenance_accessibility": 92.0
    }

    # Overall system performance
    total_energy = total_ac_power * 24 * days / 1000  # MWh
    capacity_factor = calculate_capacity_factor(total_energy, config["rated_power_ac"], 24 * days)
    specific_yield = calculate_specific_yield(total_energy * 1000, config["peak_power_dc"] * 1000)
    performance_ratio = calculate_performance_ratio(total_energy, (monthly_ghi * config["peak_power_dc"] * 1000) / 1000)

    overall_metrics = {
        "total_energy_output": total_energy,
        "capacity_factor": capacity_factor,
        "specific_yield": specific_yield,
        "performance_ratio": performance_ratio,
        "availability": 98.0,
        "overall_efficiency": (total_energy / (monthly_ghi * config["total_area"] * 10)) * 100  # Simplified
    }

    return {
        "site": site_metrics,
        "topography": topo_metrics,
        "horizon": {"impact_factor": horizon_impact},
        "solar_resource": solar_metrics,
        "pv_modules": pv_metrics,
        "fixed_structure": structure_metrics,
        "string_combiner": {"efficiency": combiner_efficiency},
        "inverter": inverter_metrics,
        "power_transformer": {"efficiency": transformer_efficiency},
        "power_station": station_metrics,
        "electrical_config": electrical_metrics,
        "civil_works": civil_metrics,
        "overall": overall_metrics
    }

# ===============================
# STREAMLIT DASHBOARD
# ===============================

def create_dashboard():
    """Create the Streamlit dashboard"""
    st.set_page_config(page_title="Solar PV Plant Analysis Dashboard", layout="wide")

    # Header
    st.title("🌞 Solar PV Plant Analysis Dashboard")
    st.markdown("**CA_PV_ED Project - Highvale, Alberta, Canada**")

    # Project Summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rated Power", f"{PROJECT_CONFIG['rated_power_ac']} MWac")
    with col2:
        st.metric("Peak Power", f"{PROJECT_CONFIG['peak_power_dc']} MWdc")
    with col3:
        st.metric("DC/AC Ratio", f"{PROJECT_CONFIG['dc_ac_ratio']}")
    with col4:
        st.metric("Total Modules", f"{PROJECT_CONFIG['pv_modules']['quantity']:,}")

    # Calculate metrics for all months
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    all_metrics = []

    for i in range(12):
        metrics = calculate_monthly_metrics(i)
        all_metrics.append(metrics)

    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📍 Site Analysis", "☀️ Solar Resource", "⚡ Equipment Performance", "🔧 System Configuration", "📊 Overall Performance"])

    with tab1:
        st.header("Site Characteristics")

        # Site metrics
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Location Details")
            st.write(f"**Latitude:** {PROJECT_CONFIG['location']['latitude']}°")
            st.write(f"**Longitude:** {PROJECT_CONFIG['location']['longitude']}°")
            st.write(f"**Altitude:** {PROJECT_CONFIG['location']['altitude']} m")
            st.write(f"**Total Area:** {PROJECT_CONFIG['total_area']} ha")
            st.write(f"**Suitable Area:** {PROJECT_CONFIG['suitable_area']} ha")

        with col2:
            # Area utilization chart
            utilization_data = [all_metrics[i]["site"]["utilization_ratio"] for i in range(12)]

            st.subheader("Area Utilization Over Time")
            chart_data = {}
            for i, month in enumerate(months):
                chart_data[month] = utilization_data[i]

            st.line_chart(chart_data)

        # Topography analysis
        st.subheader("Topography Analysis")
        col1, col2, col3 = st.columns(3)

        topo_data = {
            "Slope Impact": [all_metrics[i]["topography"]["slope_impact"] for i in range(12)],
            "Terrain Suitability": [all_metrics[i]["topography"]["terrain_suitability"] for i in range(12)],
            "Drainage Adequacy": [all_metrics[i]["topography"]["drainage_adequacy"] for i in range(12)]
        }

        for i, (key, values) in enumerate(topo_data.items()):
            with [col1, col2, col3][i]:
                st.metric(key, f"{values[0]:.1f}%")

    with tab2:
        st.header("Solar Resource Analysis")

        # Solar resource charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Global Horizontal Irradiance")
            ghi_data = {}
            for i, month in enumerate(months):
                ghi_data[month] = all_metrics[i]["solar_resource"]["ghi"]
            st.line_chart(ghi_data)

        with col2:
            st.subheader("Plane of Array Irradiance")
            poa_data = {}
            for i, month in enumerate(months):
                poa_data[month] = all_metrics[i]["solar_resource"]["poa_irradiance"]
            st.line_chart(poa_data)

        # Temperature analysis
        st.subheader("Temperature Analysis")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Ambient Temperature")
            temp_data = {}
            for i, month in enumerate(months):
                temp_data[month] = all_metrics[i]["solar_resource"]["ambient_temp"]
            st.line_chart(temp_data)

        with col2:
            st.subheader("Module Temperature")
            module_temp_data = {}
            for i, month in enumerate(months):
                module_temp_data[month] = all_metrics[i]["solar_resource"]["module_temp"]
            st.line_chart(module_temp_data)

    with tab3:
        st.header("Equipment Performance")

        # PV Modules
        st.subheader("PV Module Performance")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Module Power Output")
            module_power_data = {}
            for i, month in enumerate(months):
                module_power_data[month] = all_metrics[i]["pv_modules"]["module_power_output"]
            st.line_chart(module_power_data)

        with col2:
            st.subheader("Temperature Losses")
            temp_loss_data = {}
            for i, month in enumerate(months):
                temp_loss_data[month] = all_metrics[i]["pv_modules"]["temperature_losses"]
            st.line_chart(temp_loss_data)

        # Inverter Performance
        st.subheader("Inverter Performance")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Inverter Efficiency")
            inv_eff_data = {}
            for i, month in enumerate(months):
                inv_eff_data[month] = all_metrics[i]["inverter"]["efficiency"]
            st.line_chart(inv_eff_data)

        with col2:
            st.subheader("Inverter Loading")
            loading_data = {}
            for i, month in enumerate(months):
                loading_data[month] = all_metrics[i]["inverter"]["loading_ratio"]
            st.line_chart(loading_data)

    with tab4:
        st.header("System Configuration")

        # Electrical Configuration
        st.subheader("Electrical Performance")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("DC Losses")
            dc_loss_data = {}
            for i, month in enumerate(months):
                dc_loss_data[month] = all_metrics[i]["electrical_config"]["dc_losses"]
            st.line_chart(dc_loss_data)

        with col2:
            st.subheader("AC Losses")
            ac_loss_data = {}
            for i, month in enumerate(months):
                ac_loss_data[month] = all_metrics[i]["electrical_config"]["ac_losses"]
            st.line_chart(ac_loss_data)

        # Civil Works Impact
        st.subheader("Civil Works Performance")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Road Accessibility", f"{all_metrics[0]['civil_works']['road_accessibility']:.1f}%")
            st.metric("Drainage Effectiveness", f"{all_metrics[0]['civil_works']['drainage_effectiveness']:.1f}%")

        with col2:
            st.metric("Security Rating", f"{all_metrics[0]['civil_works']['security_rating']:.1f}%")
            st.metric("Maintenance Access", f"{all_metrics[0]['civil_works']['maintenance_accessibility']:.1f}%")

    with tab5:
        st.header("Overall Performance Summary")

        # Key Performance Indicators
        st.subheader("Key Performance Indicators")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Energy Output")
            energy_data = {}
            for i, month in enumerate(months):
                energy_data[month] = all_metrics[i]["overall"]["total_energy_output"]
            st.line_chart(energy_data)

        with col2:
            st.subheader("Capacity Factor")
            cf_data = {}
            for i, month in enumerate(months):
                cf_data[month] = all_metrics[i]["overall"]["capacity_factor"]
            st.line_chart(cf_data)

        # Performance Metrics
        st.subheader("Performance Metrics")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Performance Ratio")
            pr_data = {}
            for i, month in enumerate(months):
                pr_data[month] = all_metrics[i]["overall"]["performance_ratio"]
            st.line_chart(pr_data)

        with col2:
            st.subheader("Specific Yield")
            sy_data = {}
            for i, month in enumerate(months):
                sy_data[month] = all_metrics[i]["overall"]["specific_yield"]
            st.line_chart(sy_data)

        # Annual Summary
        st.subheader("Annual Summary")
        total_annual_energy = sum([all_metrics[i]["overall"]["total_energy_output"] for i in range(12)])
        avg_capacity_factor = sum([all_metrics[i]["overall"]["capacity_factor"] for i in range(12)]) / 12
        avg_performance_ratio = sum([all_metrics[i]["overall"]["performance_ratio"] for i in range(12)]) / 12

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Annual Energy", f"{total_annual_energy:.1f} MWh")
        with col2:
            st.metric("Avg Capacity Factor", f"{avg_capacity_factor:.1f}%")
        with col3:
            st.metric("Avg Performance Ratio", f"{avg_performance_ratio:.1f}%")
        with col4:
            st.metric("System Availability", f"{all_metrics[0]['overall']['availability']:.1f}%")

# Run the dashboard
if __name__ == "__main__":
    create_dashboard()
