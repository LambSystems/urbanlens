"""
Urban Legend — Source Retrieval

Finds drone images and metadata intersecting a selected analysis region.
Sources may be scattered, partial, or inconsistent in coverage.

For the hackathon MVP, this is a curated mapping for known demo regions.
The contract already models scattered inputs so the real implementation
can slot in later.
"""
from __future__ import annotations

from ..schemas import LatLng, SourceRecord, SourceType


# STUB: curated source sets for demo regions
_DEMO_SOURCES: list[dict] = [
    {
        "source_id": "drone_img_001",
        "source_type": SourceType.drone,
        "image_path": "data/demo/drone_img_001.png",
        "lat_offset": 0.0004,
        "lng_offset": 0.0003,
        "altitude": 110.0,
        "resolution": 0.12,
        "metadata_quality_score": 0.82,
        "geolocation_confidence": 0.78,
    },
    {
        "source_id": "drone_img_002",
        "source_type": SourceType.drone,
        "image_path": "data/demo/drone_img_002.png",
        "lat_offset": None,
        "lng_offset": None,
        "altitude": 95.0,
        "resolution": 0.18,
        "metadata_quality_score": 0.48,
        "geolocation_confidence": 0.35,
    },
    {
        "source_id": "drone_img_003",
        "source_type": SourceType.drone,
        "image_path": "data/demo/drone_img_003.png",
        "lat_offset": -0.0005,
        "lng_offset": 0.0006,
        "altitude": 105.0,
        "resolution": 0.14,
        "metadata_quality_score": 0.76,
        "geolocation_confidence": 0.71,
    },
    {
        "source_id": "derived_thermal_001",
        "source_type": SourceType.derived,
        "image_path": "data/demo/thermal_overlay_001.png",
        "lat_offset": 0.0002,
        "lng_offset": -0.0002,
        "altitude": None,
        "resolution": None,
        "metadata_quality_score": 0.75,
        "geolocation_confidence": 0.72,
    },
]


def retrieve_sources(center: LatLng, radius_m: int) -> list[SourceRecord]:
    """Find available source imagery intersecting the analysis region.

    STUB: returns curated demo sources relative to the center point.
    Replace with real spatial lookup over a source index.
    """
    records = []
    for src in _DEMO_SOURCES:
        lat = round(center.lat + src["lat_offset"], 6) if src["lat_offset"] else None
        lng = round(center.lng + src["lng_offset"], 6) if src["lng_offset"] else None
        records.append(
            SourceRecord(
                source_id=src["source_id"],
                source_type=src["source_type"],
                image_path=src["image_path"],
                lat=lat,
                lng=lng,
                altitude=src["altitude"],
                resolution=src["resolution"],
                metadata_quality_score=src["metadata_quality_score"],
                geolocation_confidence=src["geolocation_confidence"],
            )
        )
    return records


def compute_coverage_score(sources: list[SourceRecord]) -> float:
    """Estimate overall coverage quality from available sources."""
    if not sources:
        return 0.0
    avg_quality = sum(s.metadata_quality_score for s in sources) / len(sources)
    count_bonus = min(len(sources) / 6.0, 0.2)
    return round(min(avg_quality + count_bonus, 1.0), 2)
