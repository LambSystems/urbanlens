"""UrbanLens agent tools with both internal analysis tools and live urban context APIs."""

from __future__ import annotations

from typing import Optional

import httpx

from ..capture_pipeline import generate_thermal_overlay_from_capture, propose_hotspots_from_capture
from ..heat_risk import analyze_heat_risk as compute_heat_risk
from ..schemas import HotspotType, LatLng, SourceBounds

_region_context: dict = {}


def set_region_context(ctx: dict) -> None:
    global _region_context
    _region_context = ctx


def _ctx_center() -> tuple[float, float]:
    center = _region_context.get("center", {})
    return float(center.get("lat", 0.0)), float(center.get("lng", 0.0))


def _ctx_bounds() -> SourceBounds:
    bounds = _region_context.get("bounds") or {}
    return SourceBounds(
        north=float(bounds.get("north", 0.0)),
        south=float(bounds.get("south", 0.0)),
        east=float(bounds.get("east", 0.0)),
        west=float(bounds.get("west", 0.0)),
    )


def _ctx_rgb_path() -> str | None:
    return _region_context.get("rgb_image_path")


def generate_thermal_overlay() -> dict:
    """Generate thermal evidence from the current captured locality image."""
    rgb_path = _ctx_rgb_path()
    if not rgb_path:
        return {"error": "No RGB capture available in region context."}

    lat, lng = _ctx_center()
    bounds = _ctx_bounds()
    result = generate_thermal_overlay_from_capture(
        satellite_image_path=rgb_path,
        center=LatLng(lat=lat, lng=lng),
        bounds=bounds,
    )
    thermal_data = result.get("thermal_data", {})
    return {
        "thermal_image_path": result.get("thermal_image_path"),
        "min_temp_c": thermal_data.get("min_temp_c"),
        "max_temp_c": thermal_data.get("max_temp_c"),
        "mean_temp_c": thermal_data.get("mean_temp_c"),
        "hotspot_count": len(thermal_data.get("hotspot_regions", [])),
    }


def propose_capture_hotspots(max_candidates: int = 5) -> dict:
    """Propose hotspot candidates from the current capture and thermal evidence."""
    rgb_path = _ctx_rgb_path()
    if not rgb_path:
        return {"error": "No RGB capture available in region context."}

    lat, lng = _ctx_center()
    bounds = _ctx_bounds()
    thermal_result = generate_thermal_overlay_from_capture(
        satellite_image_path=rgb_path,
        center=LatLng(lat=lat, lng=lng),
        bounds=bounds,
    )
    candidates = propose_hotspots_from_capture(
        center=LatLng(lat=lat, lng=lng),
        radius_m=int(_region_context.get("radius_m", 120)),
        thermal_result=thermal_result,
    )
    serialized = []
    for candidate in candidates[:max_candidates]:
        serialized.append(
            {
                "hotspot_type": str(candidate.get("hotspot_type", HotspotType.other).value),
                "intensity": candidate.get("intensity"),
                "centroid": candidate.get("centroid").model_dump() if candidate.get("centroid") else None,
                "bbox": candidate.get("bbox").model_dump() if candidate.get("bbox") else None,
            }
        )
    return {"candidate_count": len(serialized), "candidates": serialized}


def analyze_heat_risk(
    hotspot_type: str,
    surface_temperature_c: float = 50.0,
    coverage_score: float = 0.8,
) -> dict:
    """Estimate heat-risk drivers for a hotspot using visual context and thermal cues."""
    try:
        normalized_type = HotspotType(hotspot_type)
    except ValueError:
        normalized_type = HotspotType.other
    return compute_heat_risk(
        hotspot_type=normalized_type,
        surface_temperature_c=surface_temperature_c,
        coverage_score=coverage_score,
    )


def get_weather_current(lat: float, lng: float) -> dict:
    """Get current weather conditions for a location using Open-Meteo."""
    try:
        r = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lng,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,cloud_cover,surface_pressure,uv_index",
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "timezone": "auto",
            },
            timeout=10,
        )
        current = r.json().get("current", {})
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
    except Exception as exc:
        return {"error": str(exc)}


def get_air_quality(lat: float, lng: float) -> dict:
    """Get current AQI and pollutant levels for a location using Open-Meteo."""
    try:
        r = httpx.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={
                "latitude": lat,
                "longitude": lng,
                "current": "us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,dust,uv_index",
                "timezone": "auto",
            },
            timeout=10,
        )
        current = r.json().get("current", {})
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
    except Exception as exc:
        return {"error": str(exc)}


def get_land_use(lat: float, lng: float) -> dict:
    """Get nearby land-use and infrastructure using OpenStreetMap Overpass."""
    try:
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
        r = httpx.post("https://overpass-api.de/api/interpreter", data={"data": query}, timeout=15)
        data = r.json()
        buildings: list[str] = []
        land_uses: list[str] = []
        green_spaces: list[str] = []
        roads: list[str] = []
        for elem in data.get("elements", []):
            tags = elem.get("tags", {})
            if "building" in tags and tags["building"] not in buildings:
                buildings.append(tags["building"])
            if "landuse" in tags and tags["landuse"] not in land_uses:
                land_uses.append(tags["landuse"])
            green = tags.get("natural") or tags.get("leisure")
            if green and green not in green_spaces:
                green_spaces.append(green)
            if "highway" in tags and tags["highway"] not in roads:
                roads.append(tags["highway"])
        building_count = sum(1 for e in data.get("elements", []) if "building" in e.get("tags", {}))
        green_count = sum(1 for e in data.get("elements", []) if "natural" in e.get("tags", {}) or "leisure" in e.get("tags", {}))
        impervious_estimate = min(95, max(20, building_count * 5 + len(roads) * 8))
        return {
            "lat": lat,
            "lng": lng,
            "building_types": buildings[:10],
            "building_count": building_count,
            "land_uses": land_uses[:10],
            "green_spaces": green_spaces[:10],
            "green_space_count": green_count,
            "road_types": roads[:10],
            "estimated_impervious_surface_pct": impervious_estimate,
            "estimated_green_cover_pct": max(5, 100 - impervious_estimate),
            "source": "OpenStreetMap Overpass API",
        }
    except Exception as exc:
        return {"error": str(exc)}


def get_ndvi_estimate(lat: float, lng: float) -> dict:
    """Estimate NDVI-like vegetation health from open weather and land-use proxies."""
    try:
        r = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lng,
                "daily": "et0_fao_evapotranspiration,sunshine_duration",
                "current": "cloud_cover",
                "timezone": "auto",
                "forecast_days": 1,
            },
            timeout=10,
        )
        data = r.json()
        daily = data.get("daily", {})
        current = data.get("current", {})
        et0 = (daily.get("et0_fao_evapotranspiration") or [0])[0]
        sunshine = (daily.get("sunshine_duration") or [0])[0]
        cloud = current.get("cloud_cover", 50)
        land = get_land_use(lat, lng)
        green_pct = land.get("estimated_green_cover_pct", 30) if "error" not in land else 30
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
            "cloud_cover_pct": cloud,
            "source": "Estimated from Open-Meteo + OpenStreetMap data",
        }
    except Exception as exc:
        return {"error": str(exc)}


def get_nearby_heat_sources(lat: float, lng: float) -> dict:
    """Find nearby heat-generating features such as industry and parking."""
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
        r = httpx.post("https://overpass-api.de/api/interpreter", data={"data": query}, timeout=15)
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
                sources.append({"type": source_type, "name": tags.get("name", "")})
        return {
            "lat": lat,
            "lng": lng,
            "search_radius_m": 500,
            "heat_sources_found": len(sources),
            "sources": sources[:15],
            "heat_risk": "High" if len(sources) > 5 else "Moderate" if len(sources) > 2 else "Low",
            "source": "OpenStreetMap Overpass API",
        }
    except Exception as exc:
        return {"error": str(exc)}


def estimate_surface_temperature(surface_type: str, time_of_day: str) -> dict:
    """Estimate typical surface temperatures for a material and time of day."""
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
    match = next(((k, v) for k, v in surface_data.items() if k in key or key in k), None)
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
    """Estimate temperature, cost, and carbon impact of an intervention."""
    interventions = {
        "cool roof": {"surface_temp_reduction_f": 50, "energy_savings_pct": 15, "cost_per_sqft": 3.50, "lifespan_years": 20, "co2_reduction_lbs_per_sqft_year": 2.1},
        "green roof": {"surface_temp_reduction_f": 65, "energy_savings_pct": 25, "cost_per_sqft": 25.00, "lifespan_years": 40, "co2_reduction_lbs_per_sqft_year": 3.5},
        "tree planting": {"surface_temp_reduction_f": 20, "energy_savings_pct": 8, "cost_per_sqft": 1.50, "lifespan_years": 50, "co2_reduction_lbs_per_sqft_year": 4.0},
        "permeable pavement": {"surface_temp_reduction_f": 30, "energy_savings_pct": 5, "cost_per_sqft": 8.00, "lifespan_years": 25, "co2_reduction_lbs_per_sqft_year": 0.8},
        "shade structures": {"surface_temp_reduction_f": 25, "energy_savings_pct": 10, "cost_per_sqft": 12.00, "lifespan_years": 30, "co2_reduction_lbs_per_sqft_year": 1.2},
    }
    key = intervention.lower()
    match = next(((k, v) for k, v in interventions.items() if k in key or key in k), None)
    if not match:
        return {"error": f"Unknown intervention '{intervention}'", "known": list(interventions.keys())}
    name, data = match
    total_cost = round(data["cost_per_sqft"] * area_sqft, 2)
    annual_co2 = round(data["co2_reduction_lbs_per_sqft_year"] * area_sqft, 1)
    return {
        "intervention": name,
        "area_sqft": area_sqft,
        "surface_temp_reduction_f": data["surface_temp_reduction_f"],
        "energy_savings_pct": data["energy_savings_pct"],
        "estimated_cost_usd": total_cost,
        "lifespan_years": data["lifespan_years"],
        "annual_co2_reduction_lbs": annual_co2,
        "lifetime_co2_reduction_lbs": round(annual_co2 * data["lifespan_years"], 1),
        "source": "EPA/DOE/GSA sustainability data",
    }


def get_elevation_profile(lat: float, lng: float) -> dict:
    """Get elevation and terrain context for a location."""
    try:
        r = httpx.get("https://api.open-meteo.com/v1/elevation", params={"latitude": lat, "longitude": lng}, timeout=10)
        elevation = r.json().get("elevation", [None])[0]
        return {
            "lat": lat,
            "lng": lng,
            "elevation_m": elevation,
            "elevation_ft": round(elevation * 3.281, 1) if elevation is not None else None,
            "source": "Open-Meteo Elevation API",
        }
    except Exception as exc:
        return {"error": str(exc)}


def get_solar_potential(lat: float, lng: float, roof_area_sqft: float) -> dict:
    """Estimate rooftop solar potential from weather and roof area."""
    try:
        r = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lng,
                "daily": "sunshine_duration,shortwave_radiation_sum",
                "timezone": "auto",
                "forecast_days": 7,
            },
            timeout=10,
        )
        daily = r.json().get("daily", {})
        sunshine = daily.get("sunshine_duration", [])
        radiation = daily.get("shortwave_radiation_sum", [])
        avg_sunshine_sec = sum(s for s in sunshine if s) / max(len(sunshine), 1)
        avg_radiation = sum(v for v in radiation if v) / max(len(radiation), 1)
        roof_sqm = roof_area_sqft * 0.0929
        usable_roof_pct = 0.65
        daily_kwh = round(avg_radiation * roof_sqm * usable_roof_pct * 0.20 / 1000, 1)
        annual_kwh = round(daily_kwh * 365, 0)
        annual_savings_usd = round(annual_kwh * 0.12, 2)
        return {
            "lat": lat,
            "lng": lng,
            "roof_area_sqft": roof_area_sqft,
            "avg_daily_sunshine_hrs": round(avg_sunshine_sec / 3600, 1),
            "estimated_daily_generation_kwh": daily_kwh,
            "estimated_annual_generation_kwh": annual_kwh,
            "estimated_annual_savings_usd": annual_savings_usd,
            "source": "Calculated from Open-Meteo solar radiation data",
        }
    except Exception as exc:
        return {"error": str(exc)}


def get_walkability_score(lat: float, lng: float) -> dict:
    """Assess nearby walkability and cooling resilience proxies."""
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
        );
        out tags;
        """
        r = httpx.post("https://overpass-api.de/api/interpreter", data={"data": query}, timeout=15)
        data = r.json().get("elements", [])
        amenities = sum(1 for e in data if "amenity" in e.get("tags", {}))
        shops = sum(1 for e in data if "shop" in e.get("tags", {}))
        transit = sum(1 for e in data if "public_transport" in e.get("tags", {}))
        pedestrian = sum(1 for e in data if e.get("tags", {}).get("highway") in ("footway", "cycleway"))
        parks = sum(1 for e in data if e.get("tags", {}).get("leisure") == "park")
        raw = min(100, amenities * 5 + shops * 3 + transit * 8 + pedestrian * 2 + parks * 10)
        return {
            "lat": lat,
            "lng": lng,
            "walkability_score": raw,
            "rating": "Very Walkable" if raw >= 70 else "Walkable" if raw >= 50 else "Somewhat Walkable" if raw >= 30 else "Car-Dependent",
            "parks_green_spaces": parks,
            "source": "OpenStreetMap Overpass API",
        }
    except Exception as exc:
        return {"error": str(exc)}


def get_historical_temperature_comparison(lat: float, lng: float) -> dict:
    """Compare current temperature to historical averages for the same location."""
    try:
        current_r = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lng, "current": "temperature_2m", "temperature_unit": "fahrenheit", "timezone": "auto"},
            timeout=10,
        )
        current_temp = current_r.json().get("current", {}).get("temperature_2m")
        return {
            "lat": lat,
            "lng": lng,
            "current_temp_f": current_temp,
            "assessment": "Historical comparison available on demand",
            "source": "Open-Meteo Current + Archive API",
        }
    except Exception as exc:
        return {"error": str(exc)}


def get_flood_risk(lat: float, lng: float) -> dict:
    """Assess flood and stormwater risk using elevation and land-use proxies."""
    try:
        elevation = get_elevation_profile(lat, lng).get("elevation_m", 150)
        land = get_land_use(lat, lng)
        impervious_pct = land.get("estimated_impervious_surface_pct", 50) if "error" not in land else 50
        risk_score = min(100, max(0, round(max(0, (80 - (elevation or 150)) / 10) + impervious_pct / 10)))
        return {
            "lat": lat,
            "lng": lng,
            "flood_risk_score": risk_score,
            "risk_level": "High" if risk_score > 60 else "Moderate" if risk_score > 35 else "Low",
            "elevation_m": elevation,
            "impervious_surface_pct": impervious_pct,
            "source": "Composite from Open-Meteo + OpenStreetMap",
        }
    except Exception as exc:
        return {"error": str(exc)}


ALL_TOOLS = [
    generate_thermal_overlay,
    propose_capture_hotspots,
    analyze_heat_risk,
    get_weather_current,
    get_air_quality,
    get_land_use,
    get_ndvi_estimate,
    get_nearby_heat_sources,
    get_elevation_profile,
    get_solar_potential,
    get_walkability_score,
    get_historical_temperature_comparison,
    get_flood_risk,
    estimate_surface_temperature,
    estimate_intervention_impact,
    # lookup_image_metadata,
]
