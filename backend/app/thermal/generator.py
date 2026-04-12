"""
Urban Legend — Thermal Image Generator (Stub)

Converts satellite imagery to thermal representation.
Returns both:
  - a thermal image (for UI display overlay)
  - extracted thermal data (for the analysis pipeline)

This stub returns synthetic thermal data. Replace with the actual
satellite-to-thermal model when integrated.
"""
from __future__ import annotations


def generate_thermal(satellite_image_path: str, region_bounds: dict) -> dict:
    """Convert satellite image to thermal representation.

    Args:
        satellite_image_path: path to the satellite/drone RGB image
        region_bounds: dict with lat, lng, radius_m

    Returns:
        thermal_image_path: path to generated thermal image (for UI)
        thermal_data: extracted thermal statistics and hotspot regions
    """
    center_lat = region_bounds.get("lat", 38.6270)
    center_lng = region_bounds.get("lng", -90.1994)

    # STUB: synthetic thermal output
    return {
        "thermal_image_path": "data/demo/stub_thermal_overlay.png",
        "thermal_data": {
            "min_temp_c": 28.3,
            "max_temp_c": 47.1,
            "mean_temp_c": 34.6,
            "hotspot_regions": [
                {
                    "centroid": {"lat": center_lat + 0.0007, "lng": center_lng + 0.0005},
                    "intensity": 0.87,
                    "area_px": 2816,
                },
                {
                    "centroid": {"lat": center_lat - 0.0003, "lng": center_lng + 0.0008},
                    "intensity": 0.52,
                    "area_px": 2580,
                },
                {
                    "centroid": {"lat": center_lat + 0.0004, "lng": center_lng - 0.0004},
                    "intensity": 0.74,
                    "area_px": 1520,
                },
                {
                    "centroid": {"lat": center_lat - 0.0006, "lng": center_lng - 0.0007},
                    "intensity": 0.61,
                    "area_px": 5336,
                },
            ],
        },
    }
