from __future__ import annotations

from pathlib import Path


def _synthetic_thermal(center_lat: float, center_lng: float, error: str | None = None) -> dict:
    thermal_data = {
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
    }
    if error:
        thermal_data["fallback_reason"] = error
    return {
        "thermal_image_path": "data/demo/stub_thermal_overlay.png",
        "thermal_data": thermal_data,
        "source": "synthetic_fallback",
    }


def _attach_geo_centroids(result: dict, center_lat: float, center_lng: float) -> dict:
    for region in result.get("thermal_data", {}).get("hotspot_regions", []):
        centroid_px = region.get("centroid_px")
        if not centroid_px:
            continue
        x_norm = float(centroid_px["x"]) / 640.0
        y_norm = float(centroid_px["y"]) / 512.0
        region["centroid"] = {
            "lat": round(center_lat + (0.5 - y_norm) * 0.0014, 6),
            "lng": round(center_lng + (x_norm - 0.5) * 0.0014, 6),
        }
    return result


def generate_thermal(satellite_image_path: str, region_bounds: dict) -> dict:
    """Convert a drone RGB image to thermal evidence.

    Falls back to deterministic demo data when no image/checkpoint is available.
    """
    center_lat = region_bounds.get("lat", 38.6270)
    center_lng = region_bounds.get("lng", -90.1994)
    image_path = Path(satellite_image_path) if satellite_image_path else None

    if image_path and image_path.exists():
        try:
            from .hybrid_thermal.runtime import predict_one

            result = predict_one(image_path)
            result = _attach_geo_centroids(result, center_lat, center_lng)
            result["source"] = "hybrid_thermal"
            return result
        except Exception as exc:
            return _synthetic_thermal(center_lat, center_lng, error=str(exc))

    return _synthetic_thermal(center_lat, center_lng)
