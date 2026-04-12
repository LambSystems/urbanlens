"""
Urban Legend — Final Ranking

Ranking formula:
    final_rank_score = severity_score * confidence_score
    (only for hotspots that passed the anomaly gate)

Produces the Top 3 ranked interventions with recommended actions
and explanation bullets.
"""
from __future__ import annotations

from ..schemas import HotspotCandidate, RankedHotspot
from .anomaly import passes_anomaly_gate


# Maps hotspot type to default recommended action
_DEFAULT_ACTIONS: dict[str, str] = {
    "roof": "cool-roof retrofit",
    "road_pavement": "reflective pavement treatment",
    "parking_lot": "shade and pavement mitigation",
    "hvac_mechanical": "hvac inspection",
    "vegetation_loss": "green infrastructure restoration",
    "other": "further investigation",
}


def compute_final_rank_score(severity: float, confidence: float) -> float:
    """final_rank_score = severity_score * confidence_score"""
    return round(severity * confidence, 4)


def rank_hotspots(hotspots: list[HotspotCandidate], top_n: int = 3) -> list[RankedHotspot]:
    """Rank finalized hotspots and return the top N.

    STUB: uses scores already on the hotspot objects.
    Replace with live scoring pipeline outputs.
    """
    survivors = []
    for hs in hotspots:
        if hs.anomaly_score is None or not passes_anomaly_gate(hs.anomaly_score):
            continue
        if hs.severity_score is None or hs.confidence_score is None:
            continue
        score = compute_final_rank_score(hs.severity_score, hs.confidence_score)
        survivors.append((hs, score))

    survivors.sort(key=lambda pair: pair[1], reverse=True)

    ranked = []
    for rank, (hs, score) in enumerate(survivors[:top_n], start=1):
        action = hs.recommended_action or _DEFAULT_ACTIONS.get(hs.hotspot_type.value, "investigate")
        ranked.append(
            RankedHotspot(
                hotspot_id=hs.hotspot_id,
                priority_rank=rank,
                hotspot_type=hs.hotspot_type,
                recommended_action=action,
                anomaly_score=hs.anomaly_score or 0.0,
                severity_score=hs.severity_score or 0.0,
                confidence_score=hs.confidence_score or 0.0,
                final_rank_score=score,
                why=hs.why,
            )
        )
    return ranked
