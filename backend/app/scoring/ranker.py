from __future__ import annotations

from ..schemas import HotspotCandidate, HotspotStatus, RankedHotspot


def compute_final_rank_score(severity_score: float, confidence_score: float) -> float:
    """Final rank = severity orders, confidence modulates."""
    return round(severity_score * confidence_score, 4)


def rank_hotspots(hotspots: list[HotspotCandidate], top_n: int = 3) -> list[RankedHotspot]:
    """Return the top-N finalized hotspots sorted by final_rank_score descending."""
    eligible = [
        h for h in hotspots
        if h.status == HotspotStatus.finalized
        and h.final_rank_score is not None
        and h.severity_score is not None
        and h.confidence_score is not None
        and h.anomaly_score is not None
        and h.recommended_action is not None
    ]
    eligible.sort(key=lambda h: h.final_rank_score or 0.0, reverse=True)

    ranked: list[RankedHotspot] = []
    for rank, h in enumerate(eligible[:top_n], start=1):
        ranked.append(
            RankedHotspot(
                hotspot_id=h.hotspot_id,
                priority_rank=rank,
                hotspot_type=h.hotspot_type,
                recommended_action=h.recommended_action,  # type: ignore[arg-type]
                anomaly_score=h.anomaly_score,  # type: ignore[arg-type]
                severity_score=h.severity_score,  # type: ignore[arg-type]
                confidence_score=h.confidence_score,  # type: ignore[arg-type]
                final_rank_score=h.final_rank_score,  # type: ignore[arg-type]
                why=h.why,
            )
        )
    return ranked
