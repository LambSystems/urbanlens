from __future__ import annotations

from pathlib import Path
from typing import Any


def _center_from_metadata(metadata: dict[str, Any]) -> tuple[float, float]:
    center = metadata.get("center")
    if isinstance(center, dict):
        return float(center.get("lat", 38.6270)), float(center.get("lng", -90.1994))
    return float(metadata.get("lat", 38.6270)), float(metadata.get("lng", -90.1994))


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
        "source_image_path": None,
        "thermal_image_path": "data/demo/stub_thermal_overlay.png",
        "thermal_image_url": None,
        "thermal_preview_path": None,
        "thermal_preview_url": None,
        "metadata": {},
        "model_input": {
            "uses_rgb": False,
            "uses_alphaearth": False,
            "uses_metadata": False,
        },
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


def generate_thermal(
    image_path: str | Path,
    metadata: dict[str, Any] | None = None,
    output_path: str | Path | None = None,
    allow_fallback: bool = True,
) -> dict:
    """Convert an RGB image file to thermal evidence.

    The current fast path uses RGB only. Location/context metadata is carried
    through for downstream agents, but it is not fed into the checkpoint.
    """
    metadata = metadata or {}
    center_lat, center_lng = _center_from_metadata(metadata)
    image_path = Path(image_path) if image_path else None

    if image_path and image_path.exists():
        try:
            from .hybrid_thermal.runtime import predict_one

            result = predict_one(image_path, output_path=output_path, metadata=metadata)
            result = _attach_geo_centroids(result, center_lat, center_lng)
            result["source"] = "hybrid_thermal"
            return result
        except Exception as exc:
            if not allow_fallback:
                raise
            return _synthetic_thermal(center_lat, center_lng, error=str(exc))

    if not allow_fallback:
        raise FileNotFoundError(f"RGB image not found: {image_path}")

    return _synthetic_thermal(center_lat, center_lng)
