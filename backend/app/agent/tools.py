"""Urban Legend — Agent tools with real API calls for urban sustainability analysis."""

import json
import httpx
from typing import Optional

from ..config import TRAIN_TEST_SPLIT_PATH

_region_context: dict = {}


def set_region_context(ctx: dict) -> None:
    global _region_context
    _region_context = ctx


# ---------------------------------------------------------------------------
# Real API tools — no keys needed
# ---------------------------------------------------------------------------

def get_weather_current(lat: float, lng: float) -> dict:
    """Get current weather conditions for a location including temperature,
    humidity, wind, and cloud cover. Uses Open-Meteo API (no key needed).

    Args:
        lat: Latitude of the location.
        lng: Longitude of the location.
    """
    try:
        r = httpx.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat,
            "longitude": lng,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,cloud_cover,surface_pressure,uv_index",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "timezone": "auto",
        }, timeout=10)
        data = r.json()
        current = data.get("current", {})
        return {
            "lat": lat,
            "lng": lng,
            "temperature_f": current.get("temperature_2m"),
            "feels_like_f": current.get("apparent_temperature"),
            "humidity_pct": current.get("relative_humidity_2m"),
            "wind_speed_mph": current.get("wind_speed_10m"),
            "cloud_cover_pct": current.get("cloud_cover"),
            "uv_index": current.get("uv_index"),
            "surface_pressure_hpa": current.get("surface_pressure"),
            "time": current.get("time"),
            "source": "Open-Meteo API",
        }
    except Exception as e:
        return {"error": str(e)}


def get_air_quality(lat: float, lng: float) -> dict:
    """Get current air quality index and pollutant levels for a location.
    Includes PM2.5, PM10, ozone, NO2, and overall AQI. Uses Open-Meteo API.

    Args:
        lat: Latitude of the location.
        lng: Longitude of the location.
    """
    try:
        r = httpx.get("https://air-quality-api.open-meteo.com/v1/air-quality", params={
            "latitude": lat,
            "longitude": lng,
            "current": "us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,dust,uv_index",
            "timezone": "auto",
        }, timeout=10)
        data = r.json()
        current = data.get("current", {})

        aqi = current.get("us_aqi", 0)
        if aqi <= 50:
            category = "Good"
        elif aqi <= 100:
            category = "Moderate"
        elif aqi <= 150:
            category = "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            category = "Unhealthy"
        else:
            category = "Very Unhealthy"

        return {
            "lat": lat,
            "lng": lng,
            "us_aqi": aqi,
            "aqi_category": category,
            "pm2_5_ugm3": current.get("pm2_5"),
            "pm10_ugm3": current.get("pm10"),
            "ozone_ugm3": current.get("ozone"),
            "no2_ugm3": current.get("nitrogen_dioxide"),
            "co_ugm3": current.get("carbon_monoxide"),
            "dust_ugm3": current.get("dust"),
            "uv_index": current.get("uv_index"),
            "time": current.get("time"),
            "source": "Open-Meteo Air Quality API",
        }
    except Exception as e:
        return {"error": str(e)}


def get_land_use(lat: float, lng: float) -> dict:
    """Get land use and nearby infrastructure information from OpenStreetMap.
    Returns building types, road types, green spaces, and urban features
    within 200m of the location.

    Args:
        lat: Latitude of the location.
        lng: Longitude of the location.
    """
    try:
        # Query OpenStreetMap Overpass API for features within 200m
        query = f"""
        [out:json][timeout:10];
        (
          way["building"](around:200,{lat},{lng});
          way["landuse"](around:200,{lat},{lng});
          way["natural"](around:200,{lat},{lng});
          way["leisure"](around:200,{lat},{lng});
          way["highway"](around:300,{lat},{lng});
        );
        out tags;
        """
        r = httpx.post("https://overpass-api.de/api/interpreter",
                       data={"data": query}, timeout=15)
        data = r.json()

        buildings = []
        land_uses = []
        green_spaces = []
        roads = []

        for elem in data.get("elements", []):
            tags = elem.get("tags", {})
            if "building" in tags:
                btype = tags.get("building", "yes")
                if btype not in buildings:
                    buildings.append(btype)
            if "landuse" in tags:
                lu = tags["landuse"]
                if lu not in land_uses:
                    land_uses.append(lu)
            if "natural" in tags or "leisure" in tags:
                gs = tags.get("natural") or tags.get("leisure", "")
                if gs and gs not in green_spaces:
                    green_spaces.append(gs)
            if "highway" in tags:
                road = tags["highway"]
                if road not in roads:
                    roads.append(road)

        total_features = len(data.get("elements", []))
        building_count = sum(1 for e in data.get("elements", []) if "building" in e.get("tags", {}))
        green_count = sum(1 for e in data.get("elements", [])
                         if "natural" in e.get("tags", {}) or "leisure" in e.get("tags", {}))

        impervious_estimate = min(95, max(20, building_count * 5 + len(roads) * 8))
        green_estimate = max(5, 100 - impervious_estimate)

        return {
            "lat": lat,
            "lng": lng,
            "total_features_found": total_features,
            "building_types": buildings[:10],
            "building_count": building_count,
            "land_uses": land_uses[:10],
            "green_spaces": green_spaces[:10],
            "green_space_count": green_count,
            "road_types": roads[:10],
            "estimated_impervious_surface_pct": impervious_estimate,
            "estimated_green_cover_pct": green_estimate,
            "source": "OpenStreetMap Overpass API",
        }
    except Exception as e:
        return {"error": str(e)}


def get_ndvi_estimate(lat: float, lng: float) -> dict:
    """Estimate vegetation health (NDVI proxy) for a location using
    satellite-derived land cover data. Higher values = more/healthier vegetation.

    Args:
        lat: Latitude of the location.
        lng: Longitude of the location.
    """
    try:
        # Use Open-Meteo's soil/vegetation data as a proxy
        r = httpx.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat,
            "longitude": lng,
            "daily": "et0_fao_evapotranspiration,sunshine_duration",
            "current": "cloud_cover",
            "timezone": "auto",
            "forecast_days": 1,
        }, timeout=10)
        data = r.json()
        daily = data.get("daily", {})
        current = data.get("current", {})

        et0 = (daily.get("et0_fao_evapotranspiration") or [0])[0]
        sunshine = (daily.get("sunshine_duration") or [0])[0]
        cloud = current.get("cloud_cover", 50)

        # Also check land use for green space estimate
        land = get_land_use(lat, lng)
        green_pct = land.get("estimated_green_cover_pct", 30) if "error" not in land else 30

        # Estimate NDVI from green cover and evapotranspiration
        ndvi_estimate = round(min(0.9, max(0.05, green_pct / 100 * 0.7 + et0 / 10 * 0.1)), 2)

        if ndvi_estimate > 0.6:
            health = "Dense healthy vegetation"
        elif ndvi_estimate > 0.4:
            health = "Moderate vegetation"
        elif ndvi_estimate > 0.2:
            health = "Sparse vegetation / mixed urban"
        else:
            health = "Minimal vegetation / heavy urban"

        return {
            "lat": lat,
            "lng": lng,
            "ndvi_estimate": ndvi_estimate,
            "vegetation_health": health,
            "green_cover_pct": green_pct,
            "evapotranspiration_mm": et0,
            "sunshine_hours": round(sunshine / 3600, 1) if sunshine else None,
            "interpretation": f"NDVI of {ndvi_estimate} indicates {health.lower()}. "
                            f"Green cover is approximately {green_pct}% of the area.",
            "source": "Estimated from Open-Meteo + OpenStreetMap data",
        }
    except Exception as e:
        return {"error": str(e)}


def get_nearby_heat_sources(lat: float, lng: float) -> dict:
    """Find nearby urban heat sources — industrial facilities, large parking lots,
    power infrastructure, HVAC systems, and other heat-generating features
    within 500m of the location.

    Args:
        lat: Latitude of the location.
        lng: Longitude of the location.
    """
    try:
        query = f"""
        [out:json][timeout:10];
        (
          node["power"](around:500,{lat},{lng});
          way["power"](around:500,{lat},{lng});
          node["man_made"="chimney"](around:500,{lat},{lng});
          way["landuse"="industrial"](around:500,{lat},{lng});
          way["amenity"="parking"](around:300,{lat},{lng});
          way["building"="industrial"](around:500,{lat},{lng});
          way["building"="warehouse"](around:500,{lat},{lng});
          node["amenity"="fuel"](around:500,{lat},{lng});
        );
        out tags center;
        """
        r = httpx.post("https://overpass-api.de/api/interpreter",
                       data={"data": query}, timeout=15)
        data = r.json()

        sources = []
        for elem in data.get("elements", []):
            tags = elem.get("tags", {})
            source_type = None
            if "power" in tags:
                source_type = f"Power infrastructure: {tags['power']}"
            elif tags.get("man_made") == "chimney":
                source_type = "Industrial chimney"
            elif tags.get("landuse") == "industrial":
                source_type = f"Industrial area: {tags.get('name', 'unnamed')}"
            elif tags.get("amenity") == "parking":
                source_type = f"Parking area: {tags.get('name', 'surface lot')}"
            elif tags.get("building") in ("industrial", "warehouse"):
                source_type = f"{tags['building'].title()} building: {tags.get('name', 'unnamed')}"
            elif tags.get("amenity") == "fuel":
                source_type = f"Gas station: {tags.get('name', 'unnamed')}"

            if source_type and source_type not in [s["type"] for s in sources]:
                sources.append({
                    "type": source_type,
                    "name": tags.get("name", ""),
                })

        return {
            "lat": lat,
            "lng": lng,
            "search_radius_m": 500,
            "heat_sources_found": len(sources),
            "sources": sources[:15],
            "heat_risk": "High" if len(sources) > 5 else "Moderate" if len(sources) > 2 else "Low",
            "note": "Large parking lots, industrial buildings, and power infrastructure are major contributors to localized heat.",
            "source": "OpenStreetMap Overpass API",
        }
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Analysis / calculation tools (local, no API)
# ---------------------------------------------------------------------------

def estimate_surface_temperature(surface_type: str, time_of_day: str) -> dict:
    """Estimate typical surface temperatures for different materials under sun exposure.

    Args:
        surface_type: Material type (e.g. 'dark asphalt', 'concrete', 'dark roof', 'green roof', 'metal').
        time_of_day: When the measurement would occur ('morning', 'afternoon', 'evening').
    """
    surface_data = {
        "dark asphalt": {"peak_f": 150, "ambient_delta_f": 60, "albedo": 0.05},
        "concrete": {"peak_f": 120, "ambient_delta_f": 30, "albedo": 0.35},
        "dark roof": {"peak_f": 160, "ambient_delta_f": 70, "albedo": 0.05},
        "light roof": {"peak_f": 110, "ambient_delta_f": 20, "albedo": 0.60},
        "green roof": {"peak_f": 95, "ambient_delta_f": 5, "albedo": 0.25},
        "cool roof": {"peak_f": 100, "ambient_delta_f": 10, "albedo": 0.65},
        "metal": {"peak_f": 140, "ambient_delta_f": 50, "albedo": 0.10},
        "grass": {"peak_f": 85, "ambient_delta_f": -5, "albedo": 0.25},
        "tree canopy": {"peak_f": 80, "ambient_delta_f": -10, "albedo": 0.20},
        "water": {"peak_f": 78, "ambient_delta_f": -12, "albedo": 0.06},
    }

    key = surface_type.lower()
    match = None
    for k, v in surface_data.items():
        if k in key or key in k:
            match = (k, v)
            break

    if not match:
        return {"error": f"Unknown surface type '{surface_type}'", "known_types": list(surface_data.keys())}

    name, data = match
    time_multiplier = {"morning": 0.6, "afternoon": 1.0, "evening": 0.4}.get(time_of_day, 1.0)
    adjusted_peak = round(data["peak_f"] * time_multiplier + (1 - time_multiplier) * 75)

    return {
        "surface_type": name,
        "time_of_day": time_of_day,
        "estimated_surface_temp_f": adjusted_peak,
        "peak_surface_temp_f": data["peak_f"],
        "temp_above_ambient_f": data["ambient_delta_f"],
        "albedo": data["albedo"],
        "source": "EPA/DOE surface temperature research",
    }


def estimate_intervention_impact(intervention: str, area_sqft: float) -> dict:
    """Estimate the impact of a sustainability intervention — temperature reduction,
    energy savings, CO2 reduction, and approximate cost.

    Args:
        intervention: Type of intervention (e.g. 'cool roof', 'green roof', 'tree planting', 'permeable pavement', 'shade structures').
        area_sqft: Approximate area in square feet to apply the intervention.
    """
    interventions = {
        "cool roof": {
            "surface_temp_reduction_f": 50, "energy_savings_pct": 15,
            "cost_per_sqft": 3.50, "lifespan_years": 20,
            "co2_reduction_lbs_per_sqft_year": 2.1,
            "description": "Reflective roof coating or membrane reducing heat absorption by up to 80%.",
        },
        "green roof": {
            "surface_temp_reduction_f": 65, "energy_savings_pct": 25,
            "cost_per_sqft": 25.00, "lifespan_years": 40,
            "co2_reduction_lbs_per_sqft_year": 3.5,
            "description": "Vegetated roof system providing insulation, stormwater management, and habitat.",
        },
        "tree planting": {
            "surface_temp_reduction_f": 20, "energy_savings_pct": 8,
            "cost_per_sqft": 1.50, "lifespan_years": 50,
            "co2_reduction_lbs_per_sqft_year": 4.0,
            "description": "Strategic tree planting for shade and evapotranspiration cooling.",
        },
        "permeable pavement": {
            "surface_temp_reduction_f": 30, "energy_savings_pct": 5,
            "cost_per_sqft": 8.00, "lifespan_years": 25,
            "co2_reduction_lbs_per_sqft_year": 0.8,
            "description": "Porous pavement reducing runoff and surface temperatures.",
        },
        "shade structures": {
            "surface_temp_reduction_f": 25, "energy_savings_pct": 10,
            "cost_per_sqft": 12.00, "lifespan_years": 30,
            "co2_reduction_lbs_per_sqft_year": 1.2,
            "description": "Canopies or solar shade structures over parking and pedestrian areas.",
        },
    }

    key = intervention.lower()
    match = None
    for k, v in interventions.items():
        if k in key or key in k:
            match = (k, v)
            break

    if not match:
        return {"error": f"Unknown intervention '{intervention}'", "known": list(interventions.keys())}

    name, data = match
    total_cost = round(data["cost_per_sqft"] * area_sqft, 2)
    annual_co2 = round(data["co2_reduction_lbs_per_sqft_year"] * area_sqft, 1)
    lifetime_co2 = round(annual_co2 * data["lifespan_years"], 1)

    return {
        "intervention": name,
        "area_sqft": area_sqft,
        "description": data["description"],
        "surface_temp_reduction_f": data["surface_temp_reduction_f"],
        "energy_savings_pct": data["energy_savings_pct"],
        "estimated_cost_usd": total_cost,
        "cost_per_sqft_usd": data["cost_per_sqft"],
        "lifespan_years": data["lifespan_years"],
        "annual_co2_reduction_lbs": annual_co2,
        "lifetime_co2_reduction_lbs": lifetime_co2,
        "source": "EPA/DOE/GSA sustainability data",
    }


def lookup_image_metadata(image_id: str) -> dict:
    """Look up metadata about the drone imagery — image pair info, source drone details.

    Args:
        image_id: Image index (e.g. '475') or 'summary' for dataset overview.
    """
    if not TRAIN_TEST_SPLIT_PATH.exists():
        return {"error": "Image metadata file not found"}

    with open(TRAIN_TEST_SPLIT_PATH) as f:
        data = json.load(f)

    if image_id == "summary":
        return {
            "total_image_pairs": len(data),
            "description": "DJI drone image pairs — thermal (_T) and visual (_V) captured 2024-08-04.",
            "sample_entries": {k: data[k] for k in list(data.keys())[:3]},
        }

    key = image_id if image_id.endswith(".JPG") else f"{image_id}.JPG"
    pair = data.get(key)
    if pair is None:
        return {"error": f"No metadata found for '{image_id}'"}

    thermal_file, visual_file = pair
    parts = thermal_file.split("_")
    capture_date = parts[1][:8] if len(parts) >= 2 else "unknown"
    capture_time = parts[1][8:] if len(parts) >= 2 else "unknown"

    return {
        "image_id": key,
        "thermal_file": thermal_file,
        "visual_file": visual_file,
        "drone": "DJI",
        "capture_date": f"{capture_date[:4]}-{capture_date[4:6]}-{capture_date[6:8]}",
        "capture_time": f"{capture_time[:2]}:{capture_time[2:4]}:{capture_time[4:6]}",
    }


# ---------------------------------------------------------------------------
# New: Advanced exploration tools
# ---------------------------------------------------------------------------

def get_elevation_profile(lat: float, lng: float) -> dict:
    """Get elevation and terrain data for a location. Elevation affects drainage,
    wind patterns, and heat pooling in urban valleys.

    Args:
        lat: Latitude of the location.
        lng: Longitude of the location.
    """
    try:
        r = httpx.get("https://api.open-meteo.com/v1/elevation", params={
            "latitude": lat,
            "longitude": lng,
        }, timeout=10)
        data = r.json()
        elevation = data.get("elevation", [None])[0]

        if elevation is not None:
            if elevation < 50:
                flood_note = "Low elevation — higher flood risk from stormwater"
            elif elevation < 200:
                flood_note = "Moderate elevation — standard drainage patterns"
            else:
                flood_note = "Higher elevation — generally better drainage"

            if elevation < 100:
                heat_note = "Low-lying areas tend to trap heat, especially in urban canyons"
            else:
                heat_note = "Elevation provides some natural ventilation advantage"
        else:
            flood_note = "Elevation data unavailable"
            heat_note = "Unable to assess"

        return {
            "lat": lat,
            "lng": lng,
            "elevation_m": elevation,
            "elevation_ft": round(elevation * 3.281, 1) if elevation else None,
            "flood_risk_note": flood_note,
            "heat_trapping_note": heat_note,
            "source": "Open-Meteo Elevation API",
        }
    except Exception as e:
        return {"error": str(e)}


def get_solar_potential(lat: float, lng: float, roof_area_sqft: float) -> dict:
    """Estimate solar energy potential for a rooftop — daily sunshine, estimated
    annual generation, and cost savings. Useful for recommending solar installations.

    Args:
        lat: Latitude of the location.
        lng: Longitude of the location.
        roof_area_sqft: Approximate usable roof area in square feet.
    """
    try:
        r = httpx.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat,
            "longitude": lng,
            "daily": "sunshine_duration,shortwave_radiation_sum",
            "timezone": "auto",
            "forecast_days": 7,
        }, timeout=10)
        data = r.json()
        daily = data.get("daily", {})

        sunshine_hours_list = daily.get("sunshine_duration", [])
        radiation_list = daily.get("shortwave_radiation_sum", [])

        avg_sunshine_sec = sum(s for s in sunshine_hours_list if s) / max(len(sunshine_hours_list), 1)
        avg_sunshine_hrs = round(avg_sunshine_sec / 3600, 1)
        avg_radiation = sum(r for r in radiation_list if r) / max(len(radiation_list), 1)

        # Solar calculations
        panel_efficiency = 0.20
        sqft_to_sqm = 0.0929
        roof_sqm = roof_area_sqft * sqft_to_sqm
        usable_roof_pct = 0.65  # Not all roof is usable

        # kWh per day estimate
        daily_kwh = round(avg_radiation * roof_sqm * usable_roof_pct * panel_efficiency / 1000, 1)
        annual_kwh = round(daily_kwh * 365, 0)
        annual_savings_usd = round(annual_kwh * 0.12, 2)

        # System cost estimate
        watts_per_sqft = 15
        system_kw = round(roof_area_sqft * usable_roof_pct * watts_per_sqft / 1000, 1)
        system_cost = round(system_kw * 2800, 0)  # $2.80/watt installed avg
        payback_years = round(system_cost / max(annual_savings_usd, 1), 1)

        return {
            "lat": lat,
            "lng": lng,
            "roof_area_sqft": roof_area_sqft,
            "avg_daily_sunshine_hrs": avg_sunshine_hrs,
            "avg_daily_radiation_wh_m2": round(avg_radiation, 1),
            "estimated_system_kw": system_kw,
            "estimated_daily_generation_kwh": daily_kwh,
            "estimated_annual_generation_kwh": annual_kwh,
            "estimated_annual_savings_usd": annual_savings_usd,
            "estimated_system_cost_usd": system_cost,
            "payback_years": payback_years,
            "co2_offset_lbs_year": round(annual_kwh * 0.92, 0),  # EPA grid factor
            "source": "Calculated from Open-Meteo solar radiation data + NREL averages",
        }
    except Exception as e:
        return {"error": str(e)}


def get_walkability_score(lat: float, lng: float) -> dict:
    """Assess walkability and livability by counting nearby amenities, transit stops,
    green spaces, and pedestrian infrastructure within 500m.

    Args:
        lat: Latitude of the location.
        lng: Longitude of the location.
    """
    try:
        query = f"""
        [out:json][timeout:10];
        (
          node["amenity"~"cafe|restaurant|school|library|hospital|pharmacy|bank"](around:500,{lat},{lng});
          node["shop"](around:500,{lat},{lng});
          node["public_transport"](around:500,{lat},{lng});
          way["highway"="footway"](around:300,{lat},{lng});
          way["highway"="cycleway"](around:500,{lat},{lng});
          way["leisure"="park"](around:500,{lat},{lng});
          node["amenity"="drinking_water"](around:500,{lat},{lng});
          node["amenity"="bench"](around:300,{lat},{lng});
        );
        out tags;
        """
        r = httpx.post("https://overpass-api.de/api/interpreter",
                       data={"data": query}, timeout=15)
        data = r.json()

        amenities = 0
        shops = 0
        transit = 0
        pedestrian_infra = 0
        parks = 0
        comfort = 0

        for elem in data.get("elements", []):
            tags = elem.get("tags", {})
            if "amenity" in tags and tags["amenity"] not in ("bench", "drinking_water"):
                amenities += 1
            if "shop" in tags:
                shops += 1
            if "public_transport" in tags:
                transit += 1
            if tags.get("highway") in ("footway", "cycleway"):
                pedestrian_infra += 1
            if tags.get("leisure") == "park":
                parks += 1
            if tags.get("amenity") in ("bench", "drinking_water"):
                comfort += 1

        # Score 0-100
        raw = min(100, amenities * 5 + shops * 3 + transit * 8 + pedestrian_infra * 2 + parks * 10 + comfort * 2)

        if raw >= 70:
            rating = "Very Walkable"
        elif raw >= 50:
            rating = "Walkable"
        elif raw >= 30:
            rating = "Somewhat Walkable"
        else:
            rating = "Car-Dependent"

        return {
            "lat": lat,
            "lng": lng,
            "walkability_score": raw,
            "rating": rating,
            "nearby_amenities": amenities,
            "nearby_shops": shops,
            "transit_stops": transit,
            "pedestrian_paths": pedestrian_infra,
            "parks_green_spaces": parks,
            "comfort_features": comfort,
            "heat_resilience_note": f"{'Good' if parks > 0 and comfort > 2 else 'Poor'} — "
                                   f"{'parks and shade available' if parks > 0 else 'lacks green respite areas'}, "
                                   f"{'has benches/water' if comfort > 2 else 'needs cooling stations'}",
            "source": "OpenStreetMap Overpass API",
        }
    except Exception as e:
        return {"error": str(e)}


def get_historical_temperature_comparison(lat: float, lng: float) -> dict:
    """Compare current temperature to historical averages for this location.
    Shows whether today is hotter than normal — useful for detecting heat anomalies.

    Args:
        lat: Latitude of the location.
        lng: Longitude of the location.
    """
    try:
        # Get current conditions
        current_r = httpx.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat, "longitude": lng,
            "current": "temperature_2m",
            "temperature_unit": "fahrenheit",
            "timezone": "auto",
        }, timeout=10)
        current_data = current_r.json()
        current_temp = current_data.get("current", {}).get("temperature_2m")

        # Get historical averages (last 10 years, same day of year)
        import datetime
        today = datetime.date.today()
        historical_temps = []

        for years_back in range(1, 6):
            hist_date = today.replace(year=today.year - years_back)
            try:
                hist_r = httpx.get("https://archive-api.open-meteo.com/v1/archive", params={
                    "latitude": lat, "longitude": lng,
                    "start_date": hist_date.isoformat(),
                    "end_date": hist_date.isoformat(),
                    "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean",
                    "temperature_unit": "fahrenheit",
                    "timezone": "auto",
                }, timeout=10)
                hist_data = hist_r.json()
                daily = hist_data.get("daily", {})
                mean = (daily.get("temperature_2m_mean") or [None])[0]
                if mean:
                    historical_temps.append(mean)
            except Exception:
                pass

        hist_avg = round(sum(historical_temps) / len(historical_temps), 1) if historical_temps else None
        delta = round(current_temp - hist_avg, 1) if current_temp and hist_avg else None

        if delta is not None:
            if delta > 10:
                assessment = "Significantly hotter than historical average — potential heat event"
            elif delta > 5:
                assessment = "Notably warmer than usual"
            elif delta > 0:
                assessment = "Slightly above historical average"
            elif delta > -5:
                assessment = "Near or slightly below historical average"
            else:
                assessment = "Cooler than historical average"
        else:
            assessment = "Unable to compare"

        return {
            "lat": lat,
            "lng": lng,
            "current_temp_f": current_temp,
            "historical_avg_f": hist_avg,
            "delta_f": delta,
            "years_compared": len(historical_temps),
            "assessment": assessment,
            "source": "Open-Meteo Current + Archive API",
        }
    except Exception as e:
        return {"error": str(e)}


def get_flood_risk(lat: float, lng: float) -> dict:
    """Assess flood and stormwater risk based on elevation, impervious surfaces,
    and proximity to water features.

    Args:
        lat: Latitude of the location.
        lng: Longitude of the location.
    """
    try:
        # Get elevation
        elev_data = get_elevation_profile(lat, lng)
        elevation = elev_data.get("elevation_m", 150)

        # Check for nearby water bodies
        query = f"""
        [out:json][timeout:10];
        (
          way["natural"="water"](around:500,{lat},{lng});
          way["waterway"](around:500,{lat},{lng});
          way["natural"="wetland"](around:500,{lat},{lng});
        );
        out tags;
        """
        r = httpx.post("https://overpass-api.de/api/interpreter",
                       data={"data": query}, timeout=15)
        water_data = r.json()
        water_features = len(water_data.get("elements", []))

        # Get land use for impervious estimate
        land = get_land_use(lat, lng)
        impervious_pct = land.get("estimated_impervious_surface_pct", 50) if "error" not in land else 50

        # Get recent precipitation
        precip_r = httpx.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat, "longitude": lng,
            "daily": "precipitation_sum",
            "timezone": "auto",
            "forecast_days": 3,
            "past_days": 3,
        }, timeout=10)
        precip_data = precip_r.json()
        precip_list = precip_data.get("daily", {}).get("precipitation_sum", [])
        recent_precip = sum(p for p in precip_list if p)

        # Risk scoring
        risk_score = 0
        risk_score += max(0, (80 - (elevation or 150)) / 10)  # Lower = riskier
        risk_score += impervious_pct / 10  # More impervious = riskier
        risk_score += water_features * 3  # Near water = riskier
        risk_score += recent_precip / 5  # Recent rain = riskier
        risk_score = min(100, max(0, round(risk_score)))

        if risk_score > 60:
            risk_level = "High"
        elif risk_score > 35:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        return {
            "lat": lat,
            "lng": lng,
            "flood_risk_score": risk_score,
            "risk_level": risk_level,
            "elevation_m": elevation,
            "impervious_surface_pct": impervious_pct,
            "nearby_water_features": water_features,
            "recent_precipitation_mm": round(recent_precip, 1),
            "factors": [
                f"Elevation: {elevation}m ({'low risk' if elevation and elevation > 100 else 'contributing factor'})",
                f"Impervious surfaces: {impervious_pct}% ({'high runoff risk' if impervious_pct > 60 else 'moderate'})",
                f"Water features nearby: {water_features} ({'increases risk' if water_features > 0 else 'none found'})",
                f"Recent precipitation: {round(recent_precip, 1)}mm ({'saturated ground' if recent_precip > 20 else 'dry conditions'})",
            ],
            "source": "Composite from Open-Meteo + OpenStreetMap",
        }
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Tool list for the agent
# ---------------------------------------------------------------------------

ALL_TOOLS = [
    # Real-time environmental data (live API calls)
    get_weather_current,
    get_air_quality,
    get_land_use,
    get_ndvi_estimate,
    # Advanced exploration (live API calls)
    get_elevation_profile,
    get_solar_potential,
    get_walkability_score,
    get_historical_temperature_comparison,
    get_flood_risk,
    # Analysis / calculation (local)
    estimate_surface_temperature,
    estimate_intervention_impact,
    # Data access
    lookup_image_metadata,
]
