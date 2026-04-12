from __future__ import annotations

from .schemas import HotspotType


def analyze_heat_risk(
    hotspot_type: HotspotType,
    surface_temperature_c: float | None,
    coverage_score: float | None,
) -> dict:
    base_score_map = {
        HotspotType.roof: 0.82,
        HotspotType.parking_lot: 0.74,
        HotspotType.hvac_mechanical: 0.69,
        HotspotType.road_pavement: 0.43,
        HotspotType.vegetation_loss: 0.61,
        HotspotType.other: 0.5,
    }
    factors_map = {
        HotspotType.roof: ["large exposed roof area", "dark surface cues", "low nearby shade"],
        HotspotType.parking_lot: ["large paved surface", "limited shade", "high sun exposure"],
        HotspotType.hvac_mechanical: ["concentrated rooftop equipment", "localized heat release"],
        HotspotType.road_pavement: ["expected paved-surface heat", "open sun exposure"],
        HotspotType.vegetation_loss: ["missing canopy cover", "exposed ground surface"],
        HotspotType.other: ["visible surface exposure"],
    }

    base_score = base_score_map.get(hotspot_type, 0.5)
    if surface_temperature_c is not None and surface_temperature_c >= 56:
        base_score += 0.05
    if coverage_score is not None and coverage_score < 0.65:
        base_score -= 0.04

    return {
        "heat_risk_score": round(min(max(base_score, 0.0), 0.99), 2),
        "factors": factors_map.get(hotspot_type, ["visible surface exposure"]),
        "summary": (
            "Visible environmental cues suggest elevated retained heat risk"
            if hotspot_type != HotspotType.road_pavement
            else "Visible cues suggest mostly expected paved-surface heat"
        ),
    }
