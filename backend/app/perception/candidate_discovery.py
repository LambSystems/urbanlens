"""
Urban Legend — Candidate Discovery

Proposes 3-5 hotspot candidates inside an analysis region from
thermal data and imagery features.

Techniques (pick fastest for hackathon):
  - intensity thresholding
  - clustering
  - contour extraction
  - lightweight hotspot scoring

Input: thermal data for the region + source imagery
Output: list of candidate hotspot locations with bounding boxes
"""
from __future__ import annotations

from ..schemas import BoundingBox, HotspotType, LatLng


def propose_candidates(
    thermal_data: dict,
    region_center: LatLng,
    radius_m: int,
) -> list[dict]:
    """Propose hotspot candidates from thermal and imagery data.

    Returns list of dicts with:
      - centroid (LatLng)
      - bbox (BoundingBox)
      - hotspot_type (initial guess)
      - intensity (raw thermal signal)
    """
    # STUB: return synthetic candidates matching the demo region
    # Replace with real detection once thermal model is integrated
    return [
        {
            "centroid": LatLng(lat=region_center.lat + 0.0007, lng=region_center.lng + 0.0005),
            "bbox": BoundingBox(x=112, y=78, w=64, h=48),
            "hotspot_type": HotspotType.roof,
            "intensity": 0.87,
        },
        {
            "centroid": LatLng(lat=region_center.lat - 0.0003, lng=region_center.lng + 0.0008),
            "bbox": BoundingBox(x=214, y=166, w=86, h=30),
            "hotspot_type": HotspotType.road_pavement,
            "intensity": 0.52,
        },
        {
            "centroid": LatLng(lat=region_center.lat + 0.0004, lng=region_center.lng - 0.0004),
            "bbox": BoundingBox(x=298, y=104, w=38, h=40),
            "hotspot_type": HotspotType.hvac_mechanical,
            "intensity": 0.74,
        },
        {
            "centroid": LatLng(lat=region_center.lat - 0.0006, lng=region_center.lng - 0.0007),
            "bbox": BoundingBox(x=354, y=208, w=92, h=58),
            "hotspot_type": HotspotType.parking_lot,
            "intensity": 0.61,
        },
    ]
