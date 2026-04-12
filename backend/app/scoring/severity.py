from __future__ import annotations

_MATERIAL_MULTIPLIER: dict[str, float] = {
    "dark_roof": 1.15,
    "asphalt": 1.10,
    "metal_equipment": 1.05,
    "concrete": 1.00,
    "gravel": 0.95,
    "vegetation": 0.80,
}

_AREA_SCALE_PX = 4000.0  # pixel area at which area factor saturates to ~1.0


def compute_severity_score(
    thermal_intensity: float,
    area_px: int,
    material_type: str,
) -> float:
    """Severity = thermal intensity weighted by material type and surface area."""
    material_mult = _MATERIAL_MULTIPLIER.get(material_type, 1.0)
    area_factor = min(area_px / _AREA_SCALE_PX, 1.0)
    raw = thermal_intensity * 0.65 * material_mult + area_factor * 0.35
    return round(min(max(raw, 0.0), 1.0), 4)
