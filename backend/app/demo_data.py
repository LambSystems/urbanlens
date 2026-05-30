from __future__ import annotations

from datetime import UTC, datetime

from .schemas import (
    AnalysisEvent,
    AnalysisRegion,
    AnalysisResponse,
    AnalysisResult,
    AnalysisStatus,
    AnalysisSummary,
    BoundingBox,
    ChainOfThoughtStep,
    ChainOfThoughtStepType,
    HotspotCandidate,
    HotspotStatus,
    HotspotType,
    InvestigationResponse,
    LatLng,
    PlannerQuestionResponse,
    StepStatus,
    SurfaceFamily,
    ThermalInferenceResponse,
    TraceEvidence,
    TraceKind,
    TraceStep,
    TraceStepStatus,
)
from .scoring.ranker import rank_hotspots


DEMO_REGION_ID = "demo_washu"
DEMO_CENTER = LatLng(lat=38.6488, lng=-90.3108)


def _trace_step(
    hotspot_id: str,
    kind: TraceKind,
    summary: str,
    offset_ms: int,
    evidence: TraceEvidence | None = None,
) -> TraceStep:
    now = datetime.now(UTC)
    return TraceStep(
        step_id=f"{hotspot_id}_{kind.value}",
        hotspot_id=hotspot_id,
        kind=kind,
        status=TraceStepStatus.completed,
        timestamp_ms=offset_ms,
        started_at=now,
        completed_at=now,
        summary=summary,
        evidence=evidence or TraceEvidence(),
    )


def _event(region_id: str, step: TraceStep, offset_ms: int) -> AnalysisEvent:
    return AnalysisEvent(
        region_id=region_id,
        hotspot_id=step.hotspot_id,
        step_id=step.step_id,
        kind=step.kind,
        status=TraceStepStatus.completed,
        timestamp_ms=offset_ms,
        summary=step.summary,
        details=step.details,
        scheduled_offset_ms=offset_ms,
    )


def _hotspot(
    *,
    region_id: str,
    hotspot_id: str,
    hotspot_type: HotspotType,
    surface_family: SurfaceFamily,
    label: str,
    bbox: BoundingBox,
    centroid: LatLng,
    anomaly: float,
    severity: float,
    confidence: float,
    action: str | None,
    why: list[str],
    offset_start_ms: int,
) -> tuple[HotspotCandidate, list[AnalysisEvent]]:
    now = datetime.now(UTC)
    final_score = round(severity * confidence, 4) if action else None
    status = HotspotStatus.finalized if action else HotspotStatus.discarded
    trace = [
        _trace_step(
            hotspot_id,
            TraceKind.candidate_detected,
            f"Detected {label.lower()} as a candidate heat feature.",
            offset_start_ms,
            TraceEvidence(object_label=label, object_confidence=confidence),
        ),
        _trace_step(
            hotspot_id,
            TraceKind.request_thermal_evidence,
            "Loaded deterministic demo thermal evidence for the selected satellite crop.",
            offset_start_ms + 900,
            TraceEvidence(source_count=1, coverage_score=0.82),
        ),
        _trace_step(
            hotspot_id,
            TraceKind.analyze_heat_risk,
            "Compared relative thermal intensity against nearby surfaces.",
            offset_start_ms + 1800,
            TraceEvidence(anomaly_score=anomaly, severity_score=severity, confidence_score=confidence),
        ),
        _trace_step(
            hotspot_id,
            TraceKind.score_hotspot,
            "Applied the deterministic anomaly gate and rank score formula.",
            offset_start_ms + 2700,
            TraceEvidence(anomaly_score=anomaly, severity_score=severity, confidence_score=confidence),
        ),
        _trace_step(
            hotspot_id,
            TraceKind.finalize_hotspot if action else TraceKind.discard_hotspot,
            "Finalized as a ranked intervention candidate." if action else "Discarded below the demo priority threshold.",
            offset_start_ms + 3600,
        ),
    ]
    events = [_event(region_id, step, offset_start_ms + index * 900) for index, step in enumerate(trace)]

    hotspot = HotspotCandidate(
        hotspot_id=hotspot_id,
        region_id=region_id,
        bbox=bbox,
        centroid=centroid,
        hotspot_type=hotspot_type,
        surface_family=surface_family,
        type_confidence=confidence,
        display_name=label,
        status=status,
        status_label="Recommended" if action else "Discarded",
        sidebar_summary=f"{label} reviewed by the deterministic hosted demo fixture.",
        evidence_highlights=why,
        tool_signals=["Thermal Evidence", "Surface Classification", "Deterministic Scoring"],
        surface_temperature_c=round(37.0 + anomaly * 10, 1),
        ambient_delta_c=round(3.0 + anomaly * 7, 1),
        source_count=1,
        coverage_score=0.82,
        anomaly_score=anomaly,
        severity_score=severity,
        confidence_score=confidence,
        final_rank_score=final_score,
        recommended_action=action,
        discard_reason=None if action else "below demo priority threshold",
        created_at=now,
        updated_at=now,
        why=why,
        trace=trace,
    )
    return hotspot, events


def build_demo_analysis(region_id: str = DEMO_REGION_ID) -> tuple[AnalysisResponse, list[AnalysisEvent]]:
    hotspot_specs = [
        {
            "hotspot_id": "hs_demo_01",
            "hotspot_type": HotspotType.roof,
            "surface_family": SurfaceFamily.built_surface,
            "label": "Large Roof Cluster",
            "bbox": BoundingBox(x=96, y=72, w=88, h=64),
            "centroid": LatLng(lat=38.6488, lng=-90.3108),
            "anomaly": 0.84,
            "severity": 0.78,
            "confidence": 0.86,
            "action": "cool-roof retrofit",
            "why": [
                "relative thermal signal is elevated",
                "large exposed roof surface",
                "low visible shade around the structure",
            ],
        },
        {
            "hotspot_id": "hs_demo_02",
            "hotspot_type": HotspotType.parking_lot,
            "surface_family": SurfaceFamily.paved_surface,
            "label": "Parking Lot",
            "bbox": BoundingBox(x=214, y=146, w=96, h=72),
            "centroid": LatLng(lat=38.6491, lng=-90.3097),
            "anomaly": 0.76,
            "severity": 0.72,
            "confidence": 0.74,
            "action": "shade and pavement mitigation",
            "why": [
                "broad paved area retains heat",
                "thermal signal is consistent across the lot",
            ],
        },
        {
            "hotspot_id": "hs_demo_03",
            "hotspot_type": HotspotType.road_pavement,
            "surface_family": SurfaceFamily.paved_surface,
            "label": "Road Segment",
            "bbox": BoundingBox(x=42, y=198, w=120, h=34),
            "centroid": LatLng(lat=38.6484, lng=-90.3113),
            "anomaly": 0.18,
            "severity": 0.52,
            "confidence": 0.69,
            "action": None,
            "why": [
                "surface appears consistent with expected road baseline",
                "anomaly score does not pass the gate",
            ],
        },
    ]

    hotspots: list[HotspotCandidate] = []
    events: list[AnalysisEvent] = []
    for index, spec in enumerate(hotspot_specs):
        hotspot, hotspot_events = _hotspot(region_id=region_id, offset_start_ms=index * 4800, **spec)
        hotspots.append(hotspot)
        events.extend(hotspot_events)

    ranked = rank_hotspots(hotspots, top_n=3)
    rank_lookup = {item.hotspot_id: item.priority_rank for item in ranked}
    score_lookup = {item.hotspot_id: item.final_rank_score for item in ranked}
    for hotspot in hotspots:
        if hotspot.hotspot_id in rank_lookup:
            hotspot.priority_rank = rank_lookup[hotspot.hotspot_id]
            hotspot.is_top_ranked = hotspot.priority_rank == 1
            hotspot.final_rank_score = score_lookup[hotspot.hotspot_id]

    response = AnalysisResponse(
        region=AnalysisRegion(
            region_id=region_id,
            display_name="Deterministic Demo Locality",
            center=DEMO_CENTER,
            radius_m=120,
            available_source_count=1,
            coverage_score=0.82,
            thermal_source="demo_mode_fixture",
            status=AnalysisStatus.completed,
            summary=AnalysisSummary(
                candidate_count=len(hotspots),
                discarded_count=sum(1 for item in hotspots if item.status == HotspotStatus.discarded),
                finalized_count=sum(1 for item in hotspots if item.status == HotspotStatus.finalized),
            ),
        ),
        result=AnalysisResult(
            region_id=region_id,
            status=AnalysisStatus.completed,
            hotspots=hotspots,
            top_hotspots=ranked,
            top_hotspot_id=ranked[0].hotspot_id if ranked else None,
            discarded_hotspot_ids=[item.hotspot_id for item in hotspots if item.status == HotspotStatus.discarded],
        ),
    )
    return response, events


def build_demo_planner_response(analysis: AnalysisResponse, question: str) -> PlannerQuestionResponse:
    top_hotspots = analysis.result.top_hotspots
    top = top_hotspots[0] if top_hotspots else None
    second = top_hotspots[1] if len(top_hotspots) > 1 else None
    referenced = [item.hotspot_id for item in top_hotspots[:2]]

    if top is None:
        answer = "Demo mode did not find ranked hotspots for this region."
        sections = ["No ranked intervention candidates are available in the deterministic fixture."]
    else:
        answer = (
            f"In demo mode, prioritize {top.hotspot_id}: {top.hotspot_type.value.replace('_', ' ')}. "
            f"It ranks first because severity ({top.severity_score:.2f}) and confidence "
            f"({top.confidence_score:.2f}) produce the highest final score ({top.final_rank_score:.4f})."
        )
        sections = [
            f"Top priority: {top.recommended_action} for {top.hotspot_id}.",
            "Ranking is deterministic: candidates below the anomaly gate are discarded, then final_rank_score = severity_score * confidence_score.",
        ]
        if second:
            sections.append(f"Secondary candidate: {second.recommended_action} for {second.hotspot_id}.")

    return PlannerQuestionResponse(
        region_id=analysis.region.region_id,
        question=question,
        answer=answer,
        answer_title="Deterministic Demo Answer",
        answer_sections=sections,
        referenced_hotspot_ids=referenced,
        planner_mode="demo_mode_analysis_qa",
    )


def build_demo_thermal_inference() -> ThermalInferenceResponse:
    return ThermalInferenceResponse(
        source="demo_mode_fixture",
        metadata={"demo_mode": True, "note": "ThermalGen inference is bypassed for hosted portfolio demos."},
        model_input={"bypassed": True},
        thermal_data={
            "hotspot_regions": [
                {"hotspot_id": "hs_demo_01", "anomaly_score": 0.84},
                {"hotspot_id": "hs_demo_02", "anomaly_score": 0.76},
            ]
        },
    )


def build_demo_investigation_response(session_id: str, prompt: str) -> InvestigationResponse:
    steps = [
        ChainOfThoughtStep(
            step_id="demo_session_step_01",
            step_type=ChainOfThoughtStepType.tool_call,
            tool_name="load_stored_analysis",
            status=StepStatus.completed,
            summary="Loaded the deterministic hosted demo analysis artifact.",
            evidence={"region_id": DEMO_REGION_ID, "demo_mode": True},
        ),
        ChainOfThoughtStep(
            step_id="demo_session_step_02",
            step_type=ChainOfThoughtStepType.tool_call,
            tool_name="rank_hotspots",
            status=StepStatus.completed,
            summary="Applied the deterministic anomaly gate and severity-confidence ranking.",
            evidence={"formula": "final_rank_score = severity_score * confidence_score"},
        ),
        ChainOfThoughtStep(
            step_id="demo_session_step_03",
            step_type=ChainOfThoughtStepType.answer,
            status=StepStatus.completed,
            summary="Returned a grounded demo answer without calling an external LLM.",
            evidence={"external_ai_called": False},
        ),
    ]
    answer = (
        "Demo mode is active, so this response is generated from a fixed UrbanLens analysis fixture. "
        "The top intervention is the large roof cluster because it has the highest deterministic rank score. "
        "No live LLM or ThermalGen call was made."
    )
    return InvestigationResponse(session_id=session_id, prompt=prompt, chain_of_thought=steps, answer=answer)
