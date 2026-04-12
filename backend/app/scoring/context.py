"""
Urban Legend — Context Comparison

Answers:
  - Is this hotspot unusually hot relative to nearby structures?
  - Is the signal consistent across nearby crops/tiles?
  - Is source coverage sufficient to trust the finding?

This is one of the strongest differentiators — it turns detection
into triage by adding local context awareness.
"""
from __future__ import annotations


def compare_neighbors(
    hotspot_intensity: float,
    hotspot_type: str,
    region_stats: dict | None = None,
) -> dict:
    """Compare a hotspot against nearby similar structures.

    Returns:
        neighbor_count: how many comparable structures found
        relative_percentile: where this hotspot ranks (0-1)
        coverage_score: how much of the area has source coverage
    """
    # STUB: synthetic neighbor comparison
    # Replace with real spatial comparison over source imagery
    return {
        "neighbor_count": 12,
        "relative_percentile": round(min(hotspot_intensity + 0.1, 0.99), 2),
        "coverage_score": 0.79,
    }


def check_consistency(
    hotspot_id: str,
    source_count: int = 0,
    coverage_score: float | None = None,
) -> dict:
    """Check signal consistency across nearby crops or tiles.

    Returns:
        consistency_score: 0-1, how consistent the signal is
        source_count: number of sources covering this area
    """
    # STUB: simple heuristic based on source availability
    if source_count >= 3 and (coverage_score or 0) > 0.6:
        score = 0.85
    elif source_count >= 2:
        score = 0.65
    else:
        score = 0.40

    return {
        "consistency_score": score,
        "source_count": source_count,
    }
