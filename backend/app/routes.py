from __future__ import annotations

import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from .agent.planner import answer_region_question
from .example_payloads import EXAMPLE_ANALYSIS_REQUEST
from .orchestrator import DEMO_REGION_PRESETS
from .schemas import (
    AnalysisEvent,
    AnalysisResponse,
    CreateAnalysisFromCaptureMetadataRequest,
    CreateAnalysisFromCaptureRequest,
    CreateAnalysisRequest,
    DebugAnalysisView,
    HotspotCandidate,
    PlannerQuestionRequest,
    PlannerQuestionResponse,
    VoiceBriefingRequest,
    VoiceBriefingResponse,
)
from .store import store
from .voice_briefing import create_voice_briefing


router = APIRouter()


@router.post("/analysis", response_model=AnalysisResponse)
def create_analysis(payload: CreateAnalysisRequest) -> AnalysisResponse:
    return store.create_analysis(payload)


@router.post("/analysis/from-capture", response_model=AnalysisResponse)
def create_analysis_from_capture(payload: CreateAnalysisFromCaptureRequest) -> AnalysisResponse:
    return store.create_analysis_from_capture(payload)


@router.post("/analysis/from-capture-upload", response_model=AnalysisResponse)
async def create_analysis_from_capture_upload(
    metadata: str = Form(...),
    image: UploadFile = File(...),
) -> AnalysisResponse:
    try:
        parsed = CreateAnalysisFromCaptureMetadataRequest.model_validate(json.loads(metadata))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(status_code=400, detail="Invalid capture metadata.") from exc

    image_bytes = await image.read()
    suffix = ".png"
    if image.filename and "." in image.filename:
        suffix = f".{image.filename.rsplit('.', 1)[1].lower()}"
    return store.create_analysis_from_capture_upload(parsed, image_bytes, image_suffix=suffix)


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


@router.post("/analysis/{region_id}/questions", response_model=PlannerQuestionResponse)
def ask_region_question(region_id: str, payload: PlannerQuestionRequest) -> PlannerQuestionResponse:
    try:
        analysis = store.get_analysis(region_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Analysis region not found.") from exc
    return answer_region_question(analysis, payload.question)
@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analysis/{region_id}/voice-briefing", response_model=VoiceBriefingResponse)
def create_region_voice_briefing(region_id: str, payload: VoiceBriefingRequest) -> VoiceBriefingResponse:
    try:
        analysis = store.get_analysis(region_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Analysis region not found.") from exc
    return create_voice_briefing(analysis, question=payload.question)
