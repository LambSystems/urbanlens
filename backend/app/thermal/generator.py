from __future__ import annotations


def generate_thermal(satellite_image_path: str, region_bounds: dict) -> dict:
    center_lat = region_bounds.get("lat", 38.6270)
    center_lng = region_bounds.get("lng", -90.1994)
    return {
        "thermal_image_path": satellite_image_path,
        "thermal_data": {
            "min_temp_c": 28.3,
            "max_temp_c": 47.1,
            "mean_temp_c": 34.6,
            "hotspot_regions": [
                {"centroid": {"lat": center_lat + 0.0007, "lng": center_lng + 0.0005}, "intensity": 0.87, "area_px": 2816},
                {"centroid": {"lat": center_lat - 0.0003, "lng": center_lng + 0.0008}, "intensity": 0.52, "area_px": 2580},
                {"centroid": {"lat": center_lat + 0.0004, "lng": center_lng - 0.0004}, "intensity": 0.74, "area_px": 1520},
                {"centroid": {"lat": center_lat - 0.0006, "lng": center_lng - 0.0007}, "intensity": 0.61, "area_px": 5336},
            ],
        },
    }
