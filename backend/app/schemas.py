from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────────

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


class SourceType(str, Enum):
    drone = "drone"
    satellite = "satellite"
    derived = "derived"


# ── Core geo models ───────────────────────────────────────────────────────────

class LatLng(BaseModel):
    lat: float
    lng: float


class SourceBounds(BaseModel):
    north: float
    south: float
    east: float
    west: float


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
    thermal_preview_path: str | None = None
    thermal_preview_url: str | None = None
    thermal_source: str | None = None
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
    display_name: str | None = None
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


# ── Scoring / debug ───────────────────────────────────────────────────────────

class PerceptionEvidence(BaseModel):
    hotspot_id: str
    hotspot_type: HotspotType
    object_label: str
    object_confidence: float
    source_count: int
    coverage_score: float
    material_type: str
    material_confidence: float


class ScoringResult(BaseModel):
    hotspot_id: str
    anomaly_score: float
    severity_score: float
    confidence_score: float
    coverage_score: float
    metadata_quality_score: float
    final_rank_score: float | None = None
    discard_reason: str | None = None
    why: list[str] = Field(default_factory=list)


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


# ── Ranked hotspot / analysis result ─────────────────────────────────────────

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


# ── Capture models ────────────────────────────────────────────────────────────

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
    capture: CaptureImagePayload


class CreateAnalysisFromCaptureMetadataRequest(BaseModel):
    region: CaptureRegion
    map: CaptureMapState
    viewport: SourceBounds


class PlannerQuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class PlannerQuestionResponse(BaseModel):
    region_id: str
    question: str
    answer: str
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
