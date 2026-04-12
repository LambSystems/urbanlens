from __future__ import annotations

from ..schemas import LatLng, SourceRecord, SourceType


def retrieve_sources_for_region(center: LatLng, radius_m: int) -> list[SourceRecord]:
    """Return mock source records for a selected analysis region.

    This is intentionally a provider boundary instead of inline orchestrator logic.
    Later, Engineer 3 or data integration work can replace this with real dataset
    retrieval over scattered drone imagery without changing the API contract.
    """

    radius_factor = max(min(radius_m / 120.0, 1.5), 0.75)

    return [
        SourceRecord(
            source_id="drone_img_001",
            source_type=SourceType.drone,
            image_path="data/demo/drone_img_001.png",
            lat=round(center.lat + 0.0004, 6),
            lng=round(center.lng + 0.0003, 6),
            altitude=110.0,
            resolution=round(0.12 * radius_factor, 3),
            metadata_quality_score=0.82,
            geolocation_confidence=0.78,
        ),
        SourceRecord(
            source_id="drone_img_002",
            source_type=SourceType.drone,
            image_path="data/demo/drone_img_002.png",
            lat=None,
            lng=None,
            altitude=95.0,
            resolution=round(0.18 * radius_factor, 3),
            metadata_quality_score=0.48,
            geolocation_confidence=0.35,
        ),
        SourceRecord(
            source_id="derived_thermal_001",
            source_type=SourceType.derived,
            image_path="data/demo/thermal_overlay_001.png",
            lat=round(center.lat + 0.0002, 6),
            lng=round(center.lng - 0.0002, 6),
            metadata_quality_score=0.75,
            geolocation_confidence=0.72,
        ),
    ]


def estimate_region_coverage_score(source_records: list[SourceRecord]) -> float:
    if not source_records:
        return 0.0

    weighted_sum = 0.0
    for source in source_records:
        weighted_sum += (source.metadata_quality_score + source.geolocation_confidence) / 2

    return round(weighted_sum / len(source_records), 2)
