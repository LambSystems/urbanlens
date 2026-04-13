from __future__ import annotations

from ..schemas import HotspotCandidate, RankedHotspot
from .anomaly import passes_anomaly_gate


_DEFAULT_ACTIONS: dict[str, str] = {
    "roof": "cool-roof retrofit",
    "road_pavement": "reflective pavement treatment",
    "parking_lot": "shade and pavement mitigation",
    "hvac_mechanical": "hvac inspection",
    "vegetation_loss": "green infrastructure restoration",
    "other": "further investigation",
}


def compute_final_rank_score(severity: float, confidence: float) -> float:
    return round(severity * confidence, 4)


def rank_hotspots(hotspots: list[HotspotCandidate], top_n: int = 3) -> list[RankedHotspot]:
    survivors = []
    for hotspot in hotspots:
        if hotspot.anomaly_score is None or not passes_anomaly_gate(hotspot.anomaly_score):
            continue
        if hotspot.severity_score is None or hotspot.confidence_score is None:
            continue
        score = compute_final_rank_score(hotspot.severity_score, hotspot.confidence_score)
        survivors.append((hotspot, score))
    survivors.sort(key=lambda pair: pair[1], reverse=True)

    ranked: list[RankedHotspot] = []
    for rank, (hotspot, score) in enumerate(survivors[:top_n], start=1):
        action = hotspot.recommended_action or _DEFAULT_ACTIONS.get(hotspot.hotspot_type.value, "investigate")
        ranked.append(
            RankedHotspot(
                hotspot_id=hotspot.hotspot_id,
                priority_rank=rank,
                hotspot_type=hotspot.hotspot_type,
                recommended_action=action,
                anomaly_score=hotspot.anomaly_score or 0.0,
                severity_score=hotspot.severity_score or 0.0,
                confidence_score=hotspot.confidence_score or 0.0,
                final_rank_score=score,
                why=hotspot.why,
            )
        )
    return ranked
