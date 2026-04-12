"""
Urban Legend — Confidence Scoring

Confidence modulates whether a result should be trusted and how
strongly it should be presented. It combines:

  - model/reasoning confidence
  - context consistency
  - source coverage quality
  - metadata completeness and geolocation confidence

Low coverage or weak metadata should penalize confidence.
"""
from __future__ import annotations


def compute_confidence_score(
    object_confidence: float = 0.5,
    material_confidence: float = 0.5,
    coverage_score: float | None = None,
    metadata_quality_score: float | None = None,
    consistency_score: float | None = None,
) -> float:
    """Aggregate confidence from multiple evidence signals.

    STUB: weighted average with coverage penalty.
    """
    components = [object_confidence * 0.3, material_confidence * 0.2]

    if coverage_score is not None:
        components.append(coverage_score * 0.25)
    else:
        components.append(0.1)  # penalty for unknown coverage

    if metadata_quality_score is not None:
        components.append(metadata_quality_score * 0.15)
    else:
        components.append(0.05)

    if consistency_score is not None:
        components.append(consistency_score * 0.1)
    else:
        components.append(0.05)

    return round(min(max(sum(components), 0.0), 1.0), 4)
