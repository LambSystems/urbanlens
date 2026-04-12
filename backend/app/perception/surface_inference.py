"""
Urban Legend — Surface / Material Inference

Estimates coarse material class for a hotspot, relevant to
intervention logic (e.g., dark roof -> cool-roof retrofit candidate).

Material classes:
  - dark_roof
  - reflective_roof
  - asphalt
  - concrete
  - metal_equipment
  - vegetation
  - unknown

Input: hotspot crop or object label + imagery
Output: material_type + material_confidence
"""
from __future__ import annotations

from ..schemas import HotspotType


_STUB_MATERIALS: dict[HotspotType, dict] = {
    HotspotType.roof: {
        "material_type": "dark_roof",
        "material_confidence": 0.74,
    },
    HotspotType.road_pavement: {
        "material_type": "asphalt",
        "material_confidence": 0.86,
    },
    HotspotType.hvac_mechanical: {
        "material_type": "metal_equipment",
        "material_confidence": 0.71,
    },
    HotspotType.parking_lot: {
        "material_type": "asphalt",
        "material_confidence": 0.82,
    },
    HotspotType.vegetation_loss: {
        "material_type": "vegetation",
        "material_confidence": 0.65,
    },
    HotspotType.other: {
        "material_type": "unknown",
        "material_confidence": 0.30,
    },
}


def infer_surface(hotspot_type: HotspotType, image_path: str | None = None) -> dict:
    """Infer the surface material of a hotspot.

    Returns dict with 'material_type' and 'material_confidence'.
    """
    # STUB: return precomputed material inference
    # Replace with Gemini vision or heuristic pipeline
    return _STUB_MATERIALS.get(
        hotspot_type,
        {"material_type": "unknown", "material_confidence": 0.25},
    )
