from __future__ import annotations

import json
import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from pydantic import ValidationError

from .agent.planner import answer_region_question
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
    ThermalInferenceRequest,
    ThermalInferenceResponse,
    VoiceBriefingRequest,
    VoiceBriefingResponse,
)
from .store import store
from .thermal.generator import generate_thermal
from .voice_briefing import create_voice_briefing

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT / "backend" / "data" / "hybrid_thermal"
PREDICT_DIR = DATA_ROOT / "Predict_Thermal"
UPLOAD_DIR = DATA_ROOT / "uploads"


def _safe_stem(value: str | None) -> str:
    raw = value or uuid4().hex
    stem = Path(raw).stem
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem).strip("._-")
    return cleaned[:80] or uuid4().hex


def _extension_from_content_type(content_type: str | None, filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png"}:
        return suffix
    if content_type == "image/jpeg":
        return ".jpg"
    return ".png"


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


@router.post("/thermal/infer/upload", response_model=ThermalInferenceResponse)
async def infer_thermal_from_upload(
    request: Request,
    lat: float | None = Query(default=None),
    lng: float | None = Query(default=None),
    radius_m: int | None = Query(default=None, ge=1, le=5000),
    filename: str | None = Query(default=None, max_length=120),
    allow_fallback: bool = Query(default=True),
) -> ThermalInferenceResponse:
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Upload body is empty.")

    content_type = request.headers.get("content-type")
    extension = _extension_from_content_type(content_type, filename)
    upload_stem = f"{_safe_stem(filename or 'map_capture')}_{uuid4().hex[:12]}"
    upload_path = UPLOAD_DIR / f"{upload_stem}{extension}"
    output_path = PREDICT_DIR / f"{upload_stem}.png"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(body)

    metadata: dict = {"source": "frontend_map_capture", "content_type": content_type}
    if lat is not None and lng is not None:
        metadata["center"] = {"lat": lat, "lng": lng}
    if radius_m is not None:
        metadata["radius_m"] = radius_m

    try:
        result = generate_thermal(
            image_path=upload_path,
            metadata=metadata,
            output_path=output_path,
            allow_fallback=allow_fallback,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ThermalGen inference failed: {exc}") from exc
    return ThermalInferenceResponse(**result)


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
