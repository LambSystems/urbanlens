from __future__ import annotations

from ..schemas import HotspotType


_RULE_BASED_CLASSIFICATIONS: dict[HotspotType, dict] = {
    HotspotType.roof: {"object_label": "roof", "object_confidence": 0.88},
    HotspotType.road_pavement: {"object_label": "road", "object_confidence": 0.91},
    HotspotType.hvac_mechanical: {"object_label": "rooftop_hvac", "object_confidence": 0.83},
    HotspotType.parking_lot: {"object_label": "parking_lot", "object_confidence": 0.90},
    HotspotType.vegetation_loss: {"object_label": "vegetation_edge", "object_confidence": 0.72},
    HotspotType.other: {"object_label": "unknown", "object_confidence": 0.45},
}


def classify_object(hotspot_type: HotspotType, image_path: str | None = None) -> dict:
    del image_path
    return _RULE_BASED_CLASSIFICATIONS.get(hotspot_type, {"object_label": "unknown", "object_confidence": 0.40})
