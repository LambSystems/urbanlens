from __future__ import annotations


def compute_confidence_score(
    object_confidence: float,
    material_confidence: float,
    coverage_score: float,
    metadata_quality_score: float,
    consistency_score: float,
) -> float:
    """Confidence modulates rank — how trustworthy the evidence is."""
    raw = (
        object_confidence * 0.25
        + material_confidence * 0.20
        + coverage_score * 0.20
        + metadata_quality_score * 0.15
        + consistency_score * 0.20
    )
    return round(min(max(raw, 0.0), 1.0), 4)
