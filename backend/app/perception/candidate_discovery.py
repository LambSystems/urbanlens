from __future__ import annotations

from ..schemas import BoundingBox, HotspotType, LatLng

# Image dimensions the model always outputs (see runtime.py _transform)
_MODEL_W = 640
_MODEL_H = 512


def _type_from_region(region: dict, rank: int) -> HotspotType:
    """Heuristic: assign hotspot type from model region properties."""
    intensity = region.get("intensity", 0.5)
    area_px = region.get("area_px", 0)

    # Tight, very hot cluster -> mechanical equipment
    if intensity >= 0.80 and area_px < 2_000:
        return HotspotType.hvac_mechanical
    # Hot but moderate area -> roof surface
    if intensity >= 0.72:
        return HotspotType.roof
    # Large impervious surface -> parking lot
    if area_px >= 4_000:
        return HotspotType.parking_lot
    # Broad low-medium signal -> road / pavement
    if area_px >= 1_500:
        return HotspotType.road_pavement
    # Diffuse low signal -> vegetation loss
    return HotspotType.vegetation_loss


def _bbox_from_region(region: dict) -> BoundingBox:
    bbox_px = region.get("bbox_px")
    if bbox_px:
        return BoundingBox(
            x=int(bbox_px["x"]),
            y=int(bbox_px["y"]),
            w=max(int(bbox_px["w"]), 8),
            h=max(int(bbox_px["h"]), 8),
        )
    # Fall back: estimate a square box around centroid_px
    cx = region.get("centroid_px", {}).get("x", _MODEL_W / 2)
    cy = region.get("centroid_px", {}).get("y", _MODEL_H / 2)
    side = max(int((region.get("area_px", 1000) ** 0.5)), 16)
    return BoundingBox(
        x=max(0, int(cx - side / 2)),
        y=max(0, int(cy - side / 2)),
        w=side,
        h=side,
    )


def _centroid_from_region(region: dict, region_center: LatLng) -> LatLng:
    centroid = region.get("centroid")
    if centroid and "lat" in centroid and "lng" in centroid:
        return LatLng(lat=centroid["lat"], lng=centroid["lng"])
    # Approximate from model-space pixel position if geo centroid missing.
    point = region.get("peak_px") or region.get("centroid_px", {})
    cx = point.get("x", _MODEL_W / 2)
    cy = point.get("y", _MODEL_H / 2)
    lat = region_center.lat + (0.5 - cy / _MODEL_H) * 0.0014
    lng = region_center.lng + (cx / _MODEL_W - 0.5) * 0.0014
    return LatLng(lat=round(lat, 6), lng=round(lng, 6))


def propose_candidates(thermal_data: dict, region_center: LatLng, radius_m: int) -> list[dict]:
    del radius_m
    regions = thermal_data.get("hotspot_regions", [])

    if regions:
        # Sort brightest thermal regions first so markers land on visible heat peaks.
        ranked = sorted(regions, key=lambda r: r.get("brightness_score", r.get("intensity", 0)), reverse=True)
        return [
            {
                "centroid": _centroid_from_region(r, region_center),
                "bbox": _bbox_from_region(r),
                "hotspot_type": _type_from_region(r, rank),
                "intensity": r.get("intensity", 0.5),
                "brightness_score": r.get("brightness_score", r.get("intensity", 0.5)),
                "peak_intensity": r.get("peak_intensity", r.get("intensity", 0.5)),
                "mean_intensity": r.get("mean_intensity", r.get("intensity", 0.5)),
                "area_px": r.get("area_px", 0),
            }
            for rank, r in enumerate(ranked)
        ]

    return []
