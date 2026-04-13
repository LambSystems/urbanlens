from __future__ import annotations


def compare_neighbors(hotspot_intensity: float, hotspot_type: str, region_stats: dict | None = None) -> dict:
    del hotspot_type, region_stats
    return {
        "neighbor_count": 12,
        "relative_percentile": round(min(hotspot_intensity + 0.1, 0.99), 2),
        "coverage_score": 0.79,
    }


def check_consistency(hotspot_id: str, source_count: int = 0, coverage_score: float | None = None) -> dict:
    del hotspot_id
    if source_count >= 3 and (coverage_score or 0) > 0.6:
        score = 0.85
    elif source_count >= 2:
        score = 0.65
    else:
        score = 0.40
    return {"consistency_score": score, "source_count": source_count}
