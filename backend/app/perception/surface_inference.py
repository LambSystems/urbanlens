from __future__ import annotations

from ..schemas import HotspotType


def infer_surface(
    hotspot_type: HotspotType,
    visual_features: dict | None = None,
) -> dict:
    features = visual_features or {}
    dark_ratio = float(features.get("dark_ratio", 0.0))
    light_ratio = float(features.get("light_ratio", 0.0))
    green_ratio = float(features.get("green_ratio", 0.0))

    if hotspot_type == HotspotType.vegetation_loss:
        return {"material_type": "vegetation", "material_confidence": round(0.6 + green_ratio * 0.3, 2)}

    if hotspot_type == HotspotType.hvac_mechanical:
        return {"material_type": "metal_equipment", "material_confidence": round(0.68 + light_ratio * 0.2, 2)}

    if hotspot_type == HotspotType.roof:
        material = "dark_roof" if dark_ratio >= light_ratio else "light_roof"
        confidence = 0.74 if material == "dark_roof" else 0.67
        return {"material_type": material, "material_confidence": confidence}

    if hotspot_type in {HotspotType.parking_lot, HotspotType.road_pavement}:
        material = "asphalt" if dark_ratio >= 0.18 else "concrete"
        confidence = 0.83 if material == "asphalt" else 0.72
        return {"material_type": material, "material_confidence": confidence}

    return {"material_type": "unknown", "material_confidence": 0.3}
