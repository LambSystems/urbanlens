from __future__ import annotations

from pathlib import Path
import re
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Request

from .example_payloads import EXAMPLE_ANALYSIS_REQUEST
from .agent.planner import answer_region_question
from .orchestrator import DEMO_REGION_PRESETS
from .schemas import (
    AnalysisEvent,
    AnalysisResponse,
    CreateAnalysisRequest,
    DebugAnalysisView,
    HotspotCandidate,
    PlannerQuestionRequest,
    PlannerQuestionResponse,
    ThermalInferenceRequest,
    ThermalInferenceResponse,
)
from .thermal.generator import generate_thermal
from .store import store


router = APIRouter()
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT / "backend" / "data" / "hybrid_thermal"
PREDICT_DIR = DATA_ROOT / "Predict_Thermal"
UPLOAD_DIR = DATA_ROOT / "uploads"


def _safe_stem(value: str | None) -> str:
    raw = value or uuid4().hex
    stem = Path(raw).stem
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem).strip("._-")
    return cleaned[:80] or uuid4().hex


def _resolve_repo_path(path_value: str) -> Path:
    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="image_path must stay inside this repo.") from exc
    if not resolved.exists():
        raise HTTPException(status_code=404, detail="Image file not found.")
    if not resolved.is_file():
        raise HTTPException(status_code=400, detail="image_path must point to a file.")
    return resolved


def _output_path(output_name: str | None, fallback_stem: str) -> Path:
    stem = _safe_stem(output_name or fallback_stem)
    return PREDICT_DIR / f"{stem}.png"


def _extension_from_content_type(content_type: str | None, filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png"}:
        return suffix
    if content_type == "image/jpeg":
        return ".jpg"
    if content_type == "image/png":
        return ".png"
    return ".png"


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


@router.post("/thermal/infer/path", response_model=ThermalInferenceResponse)
def infer_thermal_from_path(payload: ThermalInferenceRequest) -> ThermalInferenceResponse:
    image_path = _resolve_repo_path(payload.image_path)
    output_path = _output_path(payload.output_name, image_path.stem)
    try:
        result = generate_thermal(
            image_path=image_path,
            metadata=payload.metadata,
            output_path=output_path,
            allow_fallback=payload.allow_fallback,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ThermalGen inference failed: {exc}") from exc
    return ThermalInferenceResponse(**result)


@router.post("/thermal/infer/upload", response_model=ThermalInferenceResponse)
async def infer_thermal_from_upload(
    request: Request,
    lat: float | None = Query(default=None),
    lng: float | None = Query(default=None),
    radius_m: int | None = Query(default=None, ge=1, le=5000),
    prompt: str | None = Query(default=None, max_length=500),
    filename: str | None = Query(default=None, max_length=120),
    allow_fallback: bool = Query(default=False),
) -> ThermalInferenceResponse:
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Upload body is empty.")

    content_type = request.headers.get("content-type")
    extension = _extension_from_content_type(content_type, filename)
    upload_stem = f"{_safe_stem(filename or 'map_capture')}_{uuid4().hex[:12]}"
    upload_path = UPLOAD_DIR / f"{upload_stem}{extension}"
    output_path = _output_path(upload_stem, upload_stem)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(body)

    metadata = {
        "source": "frontend_map_capture",
        "content_type": content_type,
        "filename": filename,
        "radius_m": radius_m,
        "prompt": prompt,
    }
    if lat is not None and lng is not None:
        metadata["center"] = {"lat": lat, "lng": lng}

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
