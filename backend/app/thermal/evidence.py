"""
Urban Legend — Thermal Evidence Extraction

Extracts per-hotspot thermal cues from the thermal data generated
by the satellite-to-thermal model.

This is the tool the agent calls via request_thermal_evidence — it
returns hotspot-specific heat signals for the scoring pipeline.
"""
from __future__ import annotations


def extract_hotspot_thermal(hotspot_centroid: dict, thermal_data: dict) -> dict:
    """Extract thermal evidence for a specific hotspot location.

    Args:
        hotspot_centroid: {"lat": float, "lng": float}
        thermal_data: output from thermal.generator.generate_thermal()

    Returns:
        thermal intensity, relative heat, and surrounding context.
    """
    # STUB: find closest hotspot region from thermal data and return cues
    hotspot_regions = thermal_data.get("hotspot_regions", [])
    mean_temp = thermal_data.get("mean_temp_c", 34.0)
    max_temp = thermal_data.get("max_temp_c", 45.0)

    best_match = None
    best_dist = float("inf")

    for region in hotspot_regions:
        c = region["centroid"]
        dist = abs(c["lat"] - hotspot_centroid["lat"]) + abs(c["lng"] - hotspot_centroid["lng"])
        if dist < best_dist:
            best_dist = dist
            best_match = region

    if best_match is None:
        return {
            "intensity": 0.0,
            "estimated_temp_c": mean_temp,
            "relative_heat": 0.0,
            "area_px": 0,
        }

    estimated_temp = mean_temp + (max_temp - mean_temp) * best_match["intensity"]
    return {
        "intensity": best_match["intensity"],
        "estimated_temp_c": round(estimated_temp, 1),
        "relative_heat": round(best_match["intensity"] - 0.5, 2),
        "area_px": best_match["area_px"],
    }
