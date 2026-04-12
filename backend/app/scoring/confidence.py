from __future__ import annotations


def compute_confidence_score(
    object_confidence: float = 0.5,
    material_confidence: float = 0.5,
    coverage_score: float | None = None,
    metadata_quality_score: float | None = None,
    consistency_score: float | None = None,
) -> float:
    components = [object_confidence * 0.3, material_confidence * 0.2]
    components.append((coverage_score if coverage_score is not None else 0.4) * 0.25)
    components.append((metadata_quality_score if metadata_quality_score is not None else 0.35) * 0.15)
    components.append((consistency_score if consistency_score is not None else 0.5) * 0.1)
    return round(min(max(sum(components), 0.0), 1.0), 4)
