"""
Urban Legend — Google Maps Metadata Enrichment (Fallback)

When source records have incomplete metadata, Google Maps can
fill gaps as a fallback. This is NOT a replacement for evidence.

Allowed:
  - reverse geocoding
  - viewport/bounds support
  - approximate place or area labeling
  - contextual metadata enrichment

Not allowed:
  - treating Google Maps as primary thermal evidence
  - replacing missing drone evidence with fake data

Fallback order:
  1. source record metadata
  2. dataset-level metadata
  3. Google Maps enrichment
  4. confidence penalty if uncertainty remains
"""
from __future__ import annotations

from ..schemas import SourceRecord


def enrich_source_metadata(source: SourceRecord) -> SourceRecord:
    """Attempt to fill missing metadata fields via Google Maps APIs.

    STUB: returns source unchanged. Wire to Google Maps Geocoding
    or Places API when ready.
    """
    # TODO: Call Google Maps reverse geocoding for sources missing lat/lng
    # TODO: Call Places API for area labeling when bounds are missing
    return source
