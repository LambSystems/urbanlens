from __future__ import annotations

from datetime import datetime
from enum import Enum

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


class TraceKind(str, Enum):
    candidate_detected = "candidate_detected"
    inspect_object = "inspect_object"
    request_thermal_evidence = "request_thermal_evidence"
    infer_surface = "infer_surface"
    compare_neighbors = "compare_neighbors"
    check_consistency = "check_consistency"
    score_hotspot = "score_hotspot"
    discard_hotspot = "discard_hotspot"
    finalize_hotspot = "finalize_hotspot"


class LatLng(BaseModel):
    lat: float
    lng: float


class BoundingBox(BaseModel):
    x: int
    y: int
    w: int
    h: int


class AnalysisSummary(BaseModel):
    candidate_count: int
    discarded_count: int
    finalized_count: int


class AnalysisRegion(BaseModel):
    region_id: str
    center: LatLng
    radius_m: int = Field(default=120, ge=1)
    status: AnalysisStatus
    summary: AnalysisSummary


class TraceEvidence(BaseModel):
    object_confidence: float | None = None
    material_confidence: float | None = None
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
    started_at: datetime | None = None
    completed_at: datetime | None = None
    summary: str
    evidence: TraceEvidence = Field(default_factory=TraceEvidence)


class HotspotCandidate(BaseModel):
    hotspot_id: str
    region_id: str
    bbox: BoundingBox
    centroid: LatLng
    hotspot_type: HotspotType
    status: HotspotStatus
    anomaly_score: float | None = None
    severity_score: float | None = None
    confidence_score: float | None = None
    final_rank_score: float | None = None
    discard_reason: str | None = None
    recommended_action: str | None = None
    why: list[str] = Field(default_factory=list)
    trace: list[TraceStep] = Field(default_factory=list)


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


class AnalysisResponse(BaseModel):
    region: AnalysisRegion
    result: AnalysisResult


class CreateAnalysisRequest(BaseModel):
    center: LatLng
    radius_m: int = Field(default=120, ge=1, le=1000)


class AnalysisEvent(BaseModel):
    region_id: str
    hotspot_id: str
    step_id: str
    kind: TraceKind
    status: TraceStepStatus
    summary: str
    scheduled_offset_ms: int
