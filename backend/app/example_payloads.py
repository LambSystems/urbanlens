from __future__ import annotations

from .schemas import CreateAnalysisRequest, LatLng

EXAMPLE_ANALYSIS_REQUEST = CreateAnalysisRequest(
    center=LatLng(lat=38.6270, lng=-90.1994),
    radius_m=120,
)
