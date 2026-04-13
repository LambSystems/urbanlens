from __future__ import annotations

from ..schemas import LatLng, SourceRecord


def retrieve_sources_for_region(center: LatLng, radius_m: int) -> list[SourceRecord]:
    """Return additional source records for a selected analysis region.

    The capture workflow inserts the uploaded map snippet as the concrete
    source record, so this provider does not create synthetic source records.
    """
    del center, radius_m
    return []


def estimate_region_coverage_score(source_records: list[SourceRecord]) -> float:
    if not source_records:
        return 0.0

    weighted_sum = 0.0
    for source in source_records:
        weighted_sum += (source.metadata_quality_score + source.geolocation_confidence) / 2

    return round(weighted_sum / len(source_records), 2)
