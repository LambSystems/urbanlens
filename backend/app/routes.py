from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .example_payloads import EXAMPLE_ANALYSIS_REQUEST
from .orchestrator import DEMO_REGION_PRESETS
from .schemas import (
    AnalysisEvent,
    AnalysisResponse,
    CreateAnalysisRequest,
    DebugAnalysisView,
    HotspotCandidate,
)
from .store import store


router = APIRouter()


@router.post("/analysis", response_model=AnalysisResponse)
def create_analysis(payload: CreateAnalysisRequest) -> AnalysisResponse:
    return store.create_analysis(payload)


@router.get("/analysis/{region_id}", response_model=AnalysisResponse)
def get_analysis(region_id: str) -> AnalysisResponse:
    try:
        return store.get_analysis(region_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Analysis region not found.") from exc


@router.get("/analysis/{region_id}/hotspots/{hotspot_id}", response_model=HotspotCandidate)
def get_hotspot(region_id: str, hotspot_id: str) -> HotspotCandidate:
    try:
        return store.get_hotspot(region_id, hotspot_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Hotspot not found.") from exc


@router.get("/analysis/{region_id}/events", response_model=list[AnalysisEvent])
def get_analysis_events(region_id: str) -> list[AnalysisEvent]:
    try:
        return store.get_events(region_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Analysis region not found.") from exc


@router.get("/analysis/{region_id}/debug", response_model=DebugAnalysisView)
def get_analysis_debug(region_id: str) -> DebugAnalysisView:
    try:
        return store.get_debug_view(region_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Analysis region not found.") from exc


@router.get("/demo/regions")
def get_demo_regions() -> dict[str, list[dict]]:
    return {"regions": DEMO_REGION_PRESETS}


@router.get("/demo/example-analysis-request")
def get_example_analysis_request() -> dict:
    return EXAMPLE_ANALYSIS_REQUEST.model_dump()
