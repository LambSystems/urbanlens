from __future__ import annotations


def compute_severity_score(thermal_intensity: float, area_px: int = 0, material_type: str | None = None) -> float:
    intensity_weight = thermal_intensity * 0.5
    area_weight = min(area_px / 10000.0, 0.3)
    material_boost = 0.0
    if material_type in ("dark_roof", "asphalt"):
        material_boost = 0.1
    elif material_type in ("metal_equipment",):
        material_boost = 0.15
    return round(min(intensity_weight + area_weight + material_boost, 1.0), 4)
