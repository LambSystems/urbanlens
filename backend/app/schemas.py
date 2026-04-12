from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AnalysisStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"


class HotspotStatus(str, Enum):
    candidate = "candidate"
    investigating = "investigating"
    evidence_gathered = "evidence_gathered"
    discarded = "discarded"
    finalized = "finalized"


class TraceStepStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"


class HotspotType(str, Enum):
    roof = "roof"
    road_pavement = "road_pavement"
    parking_lot = "parking_lot"
    hvac_mechanical = "hvac_mechanical"
    vegetation_loss = "vegetation_loss"
    other = "other"


class SurfaceFamily(str, Enum):
    built_surface = "built_surface"
    paved_surface = "paved_surface"
    vegetated_area = "vegetated_area"
    mechanical_feature = "mechanical_feature"
    ambiguous = "ambiguous"


class TraceKind(str, Enum):
    candidate_detected = "candidate_detected"
    generate_thermal_overlay = "generate_thermal_overlay"
    inspect_object = "inspect_object"
    request_thermal_evidence = "request_thermal_evidence"
    analyze_heat_risk = "analyze_heat_risk"
    infer_surface = "infer_surface"
    compare_neighbors = "compare_neighbors"
    check_consistency = "check_consistency"
    score_hotspot = "score_hotspot"
    discard_hotspot = "discard_hotspot"
    finalize_hotspot = "finalize_hotspot"


class LatLng(BaseModel):
    lat: float
    lng: float


class SourceBounds(BaseModel):
    north: float
    south: float
    east: float
    west: float


class SourceType(str, Enum):
    drone = "drone"
    satellite = "satellite"
    derived = "derived"


class SourceRecord(BaseModel):
    source_id: str
    source_type: SourceType
    image_path: str | None = None
    image_url: str | None = None
    lat: float | None = None
    lng: float | None = None
    bounds: SourceBounds | None = None
    timestamp: datetime | None = None
    altitude: float | None = None
    heading: float | None = None
    resolution: float | None = None
    metadata_quality_score: float = 0.0
    geolocation_confidence: float = 0.0


class BoundingBox(BaseModel):
    x: int
    y: int
    w: int
    h: int


# ── Analysis region ───────────────────────────────────────────────────────────

class AnalysisSummary(BaseModel):
    candidate_count: int
    discarded_count: int
    finalized_count: int


class AnalysisRegion(BaseModel):
    region_id: str
    display_name: str | None = None
    center: LatLng
    radius_m: int = Field(default=120, ge=1)
    bounds: SourceBounds | None = None
    area_km2: float | None = None
    available_source_count: int = 0
    coverage_score: float | None = None
    maps_fallback_count: int = 0
    enrichment_confidence_avg: float | None = None
    thermal_image_path: str | None = None
    thermal_image_url: str | None = None
    thermal_image_width: int | None = None
    thermal_image_height: int | None = None
    thermal_preview_path: str | None = None
    thermal_preview_url: str | None = None
    thermal_preview_width: int | None = None
    thermal_preview_height: int | None = None
    thermal_source: str | None = None
    source_image_path: str | None = None
    source_image_url: str | None = None
    source_image_width: int | None = None
    source_image_height: int | None = None
    source_image_file_size_bytes: int | None = None
    aligned_rgb_path: str | None = None
    aligned_rgb_width: int | None = None
    aligned_rgb_height: int | None = None
    source_records: list[SourceRecord] = Field(default_factory=list)
    status: AnalysisStatus
    summary: AnalysisSummary


# ── Trace ─────────────────────────────────────────────────────────────────────

class TraceEvidence(BaseModel):
    object_confidence: float | None = None
    object_label: str | None = None
    material_type: str | None = None
    material_confidence: float | None = None
    source_count: int | None = None
    coverage_score: float | None = None
    neighbor_count: int | None = None
    relative_percentile: float | None = None
    consistency_score: float | None = None
    anomaly_score: float | None = None
    severity_score: float | None = None
    confidence_score: float | None = None


class TraceStep(BaseModel):
    step_id: str
    hotspot_id: str
    kind: TraceKind
    status: TraceStepStatus
    timestamp_ms: int | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)
    evidence: TraceEvidence = Field(default_factory=TraceEvidence)


class AnalysisEvent(BaseModel):
    region_id: str
    hotspot_id: str
    step_id: str
    kind: TraceKind
    status: TraceStepStatus
    timestamp_ms: int | None = None
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)
    scheduled_offset_ms: int


# ── Hotspot ───────────────────────────────────────────────────────────────────

class HotspotCandidate(BaseModel):
    hotspot_id: str
    region_id: str
    bbox: BoundingBox
    centroid: LatLng
    hotspot_type: HotspotType
    surface_family: SurfaceFamily | None = None
    type_confidence: float | None = None
    display_name: str | None = None
    status_label: str | None = None
    sidebar_summary: str | None = None
    evidence_highlights: list[str] = Field(default_factory=list)
    tool_signals: list[str] = Field(default_factory=list)
    status: HotspotStatus
    surface_temperature_c: float | None = None
    ambient_delta_c: float | None = None
    source_count: int = 0
    coverage_score: float | None = None
    anomaly_score: float | None = None
    severity_score: float | None = None
    confidence_score: float | None = None
    final_rank_score: float | None = None
    discard_reason: str | None = None
    recommended_action: str | None = None
    evidence_urls: list[str] = Field(default_factory=list)
    priority_rank: int | None = None
    is_top_ranked: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    why: list[str] = Field(default_factory=list)
    trace: list[TraceStep] = Field(default_factory=list)


class PerceptionEvidence(BaseModel):
    hotspot_id: str
    hotspot_type: HotspotType
    surface_family: SurfaceFamily | None = None
    type_confidence: float | None = None
    object_label: str
    object_confidence: float
    source_count: int = 0
    coverage_score: float | None = None
    material_type: str | None = None
    material_confidence: float | None = None


class ScoringResult(BaseModel):
    hotspot_id: str
    anomaly_score: float
    severity_score: float
    confidence_score: float
    coverage_score: float | None = None
    metadata_quality_score: float | None = None
    final_rank_score: float | None = None
    discard_reason: str | None = None
    why: list[str] = Field(default_factory=list)


class RankedHotspot(BaseModel):
    hotspot_id: str
    priority_rank: int
    hotspot_type: HotspotType
    recommended_action: str
    anomaly_score: float
    severity_score: float
    confidence_score: float
    final_rank_score: float
    why: list[str]


class AnalysisResult(BaseModel):
    region_id: str
    status: AnalysisStatus
    hotspots: list[HotspotCandidate]
    top_hotspots: list[RankedHotspot]
    top_hotspot_id: str | None = None
    discarded_hotspot_ids: list[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    region: AnalysisRegion
    result: AnalysisResult


class CreateAnalysisRequest(BaseModel):
    center: LatLng
    radius_m: int = Field(default=120, ge=1, le=1000)


class CaptureRegion(BaseModel):
    bounds: SourceBounds
    center: LatLng
    area_km2: float | None = Field(default=None, alias="areaKm2")

    model_config = {"populate_by_name": True}


class CaptureMapState(BaseModel):
    zoom: int | None = None
    map_type_id: str | None = Field(default=None, alias="mapTypeId")
    tilt: int | None = None
    heading: float | None = None

    model_config = {"populate_by_name": True}


class CaptureImagePayload(BaseModel):
    mime_type: str = Field(default="image/png", alias="mimeType")
    image_base64: str = Field(min_length=1, alias="imageBase64")

    model_config = {"populate_by_name": True}


# ── Request / response models ─────────────────────────────────────────────────

class CreateAnalysisRequest(BaseModel):
    center: LatLng
    radius_m: int = Field(default=120, ge=1, le=1000)


class CreateAnalysisFromCaptureRequest(BaseModel):
    region: CaptureRegion
    map: CaptureMapState
    viewport: SourceBounds
    image_bounds: SourceBounds | None = Field(default=None, alias="imageBounds")
    capture: CaptureImagePayload

    model_config = {"populate_by_name": True}


class CreateAnalysisFromCaptureMetadataRequest(BaseModel):
    region: CaptureRegion
    map: CaptureMapState
    viewport: SourceBounds
    image_bounds: SourceBounds | None = Field(default=None, alias="imageBounds")

    model_config = {"populate_by_name": True}


class PlannerQuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class PlannerQuestionResponse(BaseModel):
    region_id: str
    hotspot_id: str
    step_id: str
    kind: TraceKind
    status: TraceStepStatus
    timestamp_ms: int | None = None
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)
    scheduled_offset_ms: int


class DebugHotspotView(BaseModel):
    hotspot_id: str
    hotspot_type: HotspotType
    status: HotspotStatus
    perception: PerceptionEvidence
    scoring: ScoringResult
    trace_kinds: list[TraceKind]


class DebugAnalysisView(BaseModel):
    region_id: str
    status: AnalysisStatus
    hotspot_count: int
    ranking_formula: str
    anomaly_threshold: float
    hotspots: list[DebugHotspotView]


class PlannerQuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class PlannerQuestionResponse(BaseModel):
    region_id: str
    question: str
    answer: str
    answer_title: str | None = None
    answer_sections: list[str] = Field(default_factory=list)
    referenced_hotspot_ids: list[str] = Field(default_factory=list)
    planner_mode: str = "analysis_qa"


class VoiceBriefingRequest(BaseModel):
    question: str | None = Field(default=None, max_length=500)
    voice_id: str | None = Field(default=None, max_length=200)


class VoiceBriefingResponse(BaseModel):
    region_id: str
    audio_url: str | None = None
    summary_text: str
    provider: str


class SessionStatus(str, Enum):
    region_loaded = "region_loaded"
    investigating = "investigating"
    answered = "answered"


class ChainOfThoughtStepType(str, Enum):
    reasoning = "reasoning"
    tool_call = "tool_call"
    answer = "answer"


class StepStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    error = "error"


class ChainOfThoughtStep(BaseModel):
    step_id: str
    step_type: ChainOfThoughtStepType
    tool_name: str | None = None
    status: StepStatus = StepStatus.running
    summary: str = ""
    evidence: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


class SessionMessage(BaseModel):
    role: str
    content: str
    message_index: int = 0
    chain_of_thought: list[ChainOfThoughtStep] = Field(default_factory=list)


class Session(BaseModel):
    session_id: str
    center: LatLng
    radius_m: int = 120
    status: SessionStatus = SessionStatus.region_loaded
    messages: list[SessionMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class CreateSessionRequest(BaseModel):
    center: LatLng
    radius_m: int = Field(default=120, ge=1, le=1000)


class UserPromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)


class InvestigationResponse(BaseModel):
    session_id: str
    prompt: str
    chain_of_thought: list[ChainOfThoughtStep]
    answer: str


class ThermalInferenceRequest(BaseModel):
    image_path: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    output_name: str | None = None
    allow_fallback: bool = False


class ThermalInferenceResponse(BaseModel):
    source: str
    source_image_path: str | None = None
    source_image_width: int | None = None
    source_image_height: int | None = None
    source_image_file_size_bytes: int | None = None
    aligned_rgb_path: str | None = None
    aligned_rgb_width: int | None = None
    aligned_rgb_height: int | None = None
    thermal_image_path: str | None = None
    thermal_image_url: str | None = None
    thermal_image_width: int | None = None
    thermal_image_height: int | None = None
    thermal_preview_path: str | None = None
    thermal_preview_url: str | None = None
    thermal_preview_width: int | None = None
    thermal_preview_height: int | None = None
    checkpoint_path: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    model_input: dict[str, Any] = Field(default_factory=dict)
    thermal_data: dict[str, Any] = Field(default_factory=dict)
