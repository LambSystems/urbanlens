"""Urban Legend — Agent tools for urban sustainability analysis."""

import json
from typing import Optional

from ..config import TRAIN_TEST_SPLIT_PATH

# Region context set by the loop before running the agent
_region_context: dict = {}


def set_region_context(ctx: dict) -> None:
    global _region_context
    _region_context = ctx


# ---------------------------------------------------------------------------
# Data access tools
# ---------------------------------------------------------------------------

def lookup_image_metadata(image_id: str) -> dict:
    """Look up metadata about the drone imagery — image pair info, source drone details.

    Args:
        image_id: Image index (e.g. '475') or filename. Use 'summary' for dataset overview.
    """
    if not TRAIN_TEST_SPLIT_PATH.exists():
        return {"error": "Image metadata file not found"}

    with open(TRAIN_TEST_SPLIT_PATH) as f:
        data = json.load(f)

    if image_id == "summary":
        return {
            "total_image_pairs": len(data),
            "description": "Dataset of DJI drone image pairs — thermal (_T) and visual (_V) captured on 2024-08-04.",
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


def lookup_location_info(query: str) -> dict:
    """Look up information about the location — address, building types, land use,
    zoning, and neighborhood context.

    Args:
        query: What to look up (e.g. 'the building on the northwest corner' or 'general').
    """
    center = _region_context.get("center", {})
    return {
        "coordinates": center,
        "city": "St. Louis",
        "state": "Missouri",
        "area_description": "Urban downtown area with commercial buildings, office towers, parking structures, and surface roads. Typical Midwestern urban heat island characteristics.",
        "building_types": ["commercial office", "parking garage", "retail", "mixed-use residential"],
        "land_use": "commercial/mixed-use urban core",
        "zoning": "Central Business District (CBD)",
        "climate_zone": "IECC Zone 4A — mixed-humid",
        "avg_summer_high_f": 89,
        "urban_tree_canopy_pct": 18,
        "impervious_surface_pct": 78,
        "note": "Curated demo data. Wire to Google Maps Places API for live lookups.",
    }


# ---------------------------------------------------------------------------
# Analysis tools
# ---------------------------------------------------------------------------

def get_climate_data(location: str) -> dict:
    """Get local climate context — temperature ranges, precipitation, heating/cooling
    degree days, and climate-related sustainability factors.

    Args:
        location: City or coordinates (e.g. 'St. Louis, MO').
    """
    return {
        "location": location or "St. Louis, MO",
        "climate_zone": "4A — Mixed-Humid",
        "avg_annual_temp_f": 57,
        "avg_summer_high_f": 89,
        "avg_winter_low_f": 24,
        "cooling_degree_days": 1764,
        "heating_degree_days": 4484,
        "annual_precipitation_in": 42,
        "heat_wave_days_per_year": 12,
        "urban_heat_island_intensity_f": 5.2,
        "sustainability_notes": [
            "High cooling demand makes roof reflectivity impactful",
            "Mixed-humid climate supports green infrastructure",
            "Summer heat waves intensify urban heat island effects",
            "Both heating and cooling matter — insulation is dual-benefit",
        ],
    }


def estimate_surface_temperature(surface_type: str, time_of_day: str) -> dict:
    """Estimate typical surface temperatures for different materials under sun exposure.
    Use this to contextualize thermal observations with known material properties.

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
            "surface_temp_reduction_f": 50,
            "energy_savings_pct": 15,
            "cost_per_sqft": 3.50,
            "lifespan_years": 20,
            "co2_reduction_lbs_per_sqft_year": 2.1,
            "description": "Reflective roof coating or membrane that reduces heat absorption by up to 80%.",
        },
        "green roof": {
            "surface_temp_reduction_f": 65,
            "energy_savings_pct": 25,
            "cost_per_sqft": 25.00,
            "lifespan_years": 40,
            "co2_reduction_lbs_per_sqft_year": 3.5,
            "description": "Vegetated roof system that provides insulation, stormwater management, and habitat.",
        },
        "tree planting": {
            "surface_temp_reduction_f": 20,
            "energy_savings_pct": 8,
            "cost_per_sqft": 1.50,
            "lifespan_years": 50,
            "co2_reduction_lbs_per_sqft_year": 4.0,
            "description": "Strategic tree planting for shade and evapotranspiration cooling.",
        },
        "permeable pavement": {
            "surface_temp_reduction_f": 30,
            "energy_savings_pct": 5,
            "cost_per_sqft": 8.00,
            "lifespan_years": 25,
            "co2_reduction_lbs_per_sqft_year": 0.8,
            "description": "Porous pavement that reduces runoff and surface temperatures through evaporation.",
        },
        "shade structures": {
            "surface_temp_reduction_f": 25,
            "energy_savings_pct": 10,
            "cost_per_sqft": 12.00,
            "lifespan_years": 30,
            "co2_reduction_lbs_per_sqft_year": 1.2,
            "description": "Canopies, pergolas, or solar shade structures over parking and pedestrian areas.",
        },
        "reflective pavement": {
            "surface_temp_reduction_f": 35,
            "energy_savings_pct": 3,
            "cost_per_sqft": 2.00,
            "lifespan_years": 15,
            "co2_reduction_lbs_per_sqft_year": 0.5,
            "description": "Light-colored or reflective coating applied to existing pavement surfaces.",
        },
    }

    key = intervention.lower()
    match = None
    for k, v in interventions.items():
        if k in key or key in k:
            match = (k, v)
            break

    if not match:
        return {"error": f"Unknown intervention '{intervention}'", "known_interventions": list(interventions.keys())}

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
        "roi_notes": f"At {data['energy_savings_pct']}% energy savings over {data['lifespan_years']} years, typical payback period is 3-7 years for commercial buildings.",
        "source": "EPA/DOE/GSA sustainability intervention data",
    }


def compare_surfaces(surface_a: str, surface_b: str) -> dict:
    """Compare the thermal and sustainability properties of two surface types.
    Use this to explain why one area is hotter than another in the thermal image.

    Args:
        surface_a: First surface type (e.g. 'dark asphalt').
        surface_b: Second surface type (e.g. 'concrete').
    """
    data_a = estimate_surface_temperature(surface_a, "afternoon")
    data_b = estimate_surface_temperature(surface_b, "afternoon")

    if "error" in data_a or "error" in data_b:
        errors = []
        if "error" in data_a:
            errors.append(data_a["error"])
        if "error" in data_b:
            errors.append(data_b["error"])
        return {"error": "; ".join(errors)}

    temp_diff = data_a["peak_surface_temp_f"] - data_b["peak_surface_temp_f"]

    return {
        "surface_a": data_a["surface_type"],
        "surface_b": data_b["surface_type"],
        "surface_a_peak_temp_f": data_a["peak_surface_temp_f"],
        "surface_b_peak_temp_f": data_b["peak_surface_temp_f"],
        "temperature_difference_f": abs(temp_diff),
        "hotter_surface": data_a["surface_type"] if temp_diff > 0 else data_b["surface_type"],
        "surface_a_albedo": data_a["albedo"],
        "surface_b_albedo": data_b["albedo"],
        "explanation": f"{data_a['surface_type']} reaches {data_a['peak_surface_temp_f']}°F peak vs {data_b['surface_type']} at {data_b['peak_surface_temp_f']}°F.",
    }


def calculate_area_metrics(length_ft: float, width_ft: float, surface_type: str) -> dict:
    """Calculate area-based sustainability metrics — energy waste estimate, potential
    savings from intervention, and CO2 impact.

    Args:
        length_ft: Estimated length in feet.
        width_ft: Estimated width in feet.
        surface_type: Current surface material (e.g. 'dark roof', 'asphalt').
    """
    area_sqft = length_ft * width_ft
    area_sqm = area_sqft * 0.0929

    surface_data = estimate_surface_temperature(surface_type, "afternoon")
    peak_temp = surface_data.get("peak_surface_temp_f", 140)
    albedo = surface_data.get("albedo", 0.1)

    solar_btu_per_sqft_day = 2000
    absorbed_btu = solar_btu_per_sqft_day * (1 - albedo) * area_sqft
    absorbed_kwh = round(absorbed_btu / 3412, 1)

    cool_roof_albedo = 0.65
    cool_absorbed_btu = solar_btu_per_sqft_day * (1 - cool_roof_albedo) * area_sqft
    savings_btu = absorbed_btu - cool_absorbed_btu
    savings_kwh = round(savings_btu / 3412, 1)

    return {
        "area_sqft": round(area_sqft, 1),
        "area_sqm": round(area_sqm, 1),
        "current_surface": surface_type,
        "current_albedo": albedo,
        "peak_surface_temp_f": peak_temp,
        "daily_heat_absorbed_kwh": absorbed_kwh,
        "daily_savings_with_cool_roof_kwh": savings_kwh,
        "annual_savings_estimate_kwh": round(savings_kwh * 120, 1),
        "annual_savings_estimate_usd": round(savings_kwh * 120 * 0.12, 2),
    }


ALL_TOOLS = [
    lookup_image_metadata,
    lookup_location_info,
    get_climate_data,
    estimate_surface_temperature,
    estimate_intervention_impact,
    compare_surfaces,
    calculate_area_metrics,
]
