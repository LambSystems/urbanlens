"""
Urban Legend — Object Classifier

Identifies the coarse object type a hotspot is attached to.

Taxonomy (fixed for MVP):
  - roof
  - road_pavement
  - parking_lot
  - hvac_mechanical
  - vegetation_loss
  - other

Input: hotspot crop or coordinates + source imagery
Output: object label + confidence
"""
from __future__ import annotations

from ..schemas import HotspotType


# Stub lookup — maps initial type guess to classification output
_STUB_CLASSIFICATIONS: dict[HotspotType, dict] = {
    HotspotType.roof: {
        "object_label": "roof",
        "object_confidence": 0.88,
    },
    HotspotType.road_pavement: {
        "object_label": "road",
        "object_confidence": 0.91,
    },
    HotspotType.hvac_mechanical: {
        "object_label": "rooftop_hvac",
        "object_confidence": 0.83,
    },
    HotspotType.parking_lot: {
        "object_label": "parking_lot",
        "object_confidence": 0.90,
    },
    HotspotType.vegetation_loss: {
        "object_label": "vegetation_edge",
        "object_confidence": 0.72,
    },
    HotspotType.other: {
        "object_label": "unknown",
        "object_confidence": 0.45,
    },
}


def classify_object(hotspot_type: HotspotType, image_path: str | None = None) -> dict:
    """Classify the object at a hotspot location.

    Returns dict with 'object_label' and 'object_confidence'.
    """
    # STUB: return precomputed classification
    # Replace with Gemini vision or dedicated classifier
    return _STUB_CLASSIFICATIONS.get(
        hotspot_type,
        {"object_label": "unknown", "object_confidence": 0.40},
    )
