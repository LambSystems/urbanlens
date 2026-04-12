from __future__ import annotations

from pydantic import BaseModel

from ..schemas import LatLng, SourceRecord


class GoogleMapsEnrichment(BaseModel):
    source_id: str
    place_label: str | None = None
    inferred_bounds_hint: str | None = None
    inferred_lat: float | None = None
    inferred_lng: float | None = None
    enrichment_confidence: float = 0.0
    notes: list[str] = []


def enrich_source_metadata(
    source: SourceRecord,
    region_center: LatLng,
) -> GoogleMapsEnrichment:
    """Return fallback metadata enrichment derived from Google Maps context.

    This is intentionally conservative. It should help explain missing metadata
    and slightly improve operability, but it must not replace the drone evidence
    itself or fabricate thermal truth.
    """

    if source.lat is not None and source.lng is not None:
        return GoogleMapsEnrichment(
            source_id=source.source_id,
            place_label="existing_geolocation",
            inferred_bounds_hint="not_needed",
            inferred_lat=source.lat,
            inferred_lng=source.lng,
            enrichment_confidence=0.95,
            notes=["Source already has geolocation metadata."],
        )

    return GoogleMapsEnrichment(
        source_id=source.source_id,
        place_label="region_context_fallback",
        inferred_bounds_hint="approximate_region_center",
        inferred_lat=region_center.lat,
        inferred_lng=region_center.lng,
        enrichment_confidence=0.42,
        notes=[
            "Source metadata is incomplete.",
            "Using region-level Google Maps context as an approximate fallback.",
            "This enrichment should reduce uncertainty, not replace source evidence.",
        ],
    )


def summarize_enrichment_coverage(
    sources: list[SourceRecord],
    region_center: LatLng,
) -> dict[str, float | int]:
    if not sources:
        return {
            "enriched_source_count": 0,
            "native_geolocation_count": 0,
            "maps_fallback_count": 0,
            "enrichment_confidence_avg": 0.0,
        }

    enrichments = [enrich_source_metadata(source, region_center) for source in sources]
    native_geolocation_count = sum(
        1 for source in sources if source.lat is not None and source.lng is not None
    )
    maps_fallback_count = len(sources) - native_geolocation_count
    enrichment_confidence_avg = round(
        sum(item.enrichment_confidence for item in enrichments) / len(enrichments),
        2,
    )

    return {
        "enriched_source_count": len(sources),
        "native_geolocation_count": native_geolocation_count,
        "maps_fallback_count": maps_fallback_count,
        "enrichment_confidence_avg": enrichment_confidence_avg,
    }
