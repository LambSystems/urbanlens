"""
Urban Legend — Evidence Normalization

Turns scattered drone imagery and metadata into a shared internal
format ready for the analysis pipeline.

Responsibilities:
  - normalize crops or region evidence
  - attach source metadata
  - expose coverage quality to downstream confidence logic
  - tolerate incomplete metadata
"""
from __future__ import annotations

from ..schemas import SourceRecord


def normalize_sources(sources: list[SourceRecord]) -> dict:
    """Normalize scattered source records into analysis-ready representation.

    Returns a summary dict the pipeline can use without worrying
    about per-source inconsistencies.

    STUB: passthrough with quality summary.
    """
    geolocated = [s for s in sources if s.lat is not None and s.lng is not None]
    avg_geo_confidence = (
        sum(s.geolocation_confidence for s in sources) / len(sources)
        if sources
        else 0.0
    )

    return {
        "total_sources": len(sources),
        "geolocated_sources": len(geolocated),
        "partial_metadata_count": len(sources) - len(geolocated),
        "avg_geolocation_confidence": round(avg_geo_confidence, 2),
        "source_ids": [s.source_id for s in sources],
    }
