from __future__ import annotations

from datetime import UTC, datetime

from .providers.google_maps_enrichment import summarize_enrichment_coverage
from .providers.source_retrieval import estimate_region_coverage_score, retrieve_sources_for_region
from .schemas import (
    AnalysisEvent,
    DebugAnalysisView,
    DebugHotspotView,
    AnalysisResponse,
    AnalysisResult,
    AnalysisStatus,
    AnalysisSummary,
    BoundingBox,
    HotspotCandidate,
    HotspotStatus,
    HotspotType,
    LatLng,
    PerceptionEvidence,
    RankedHotspot,
    ScoringResult,
    TraceEvidence,
    TraceKind,
    TraceStep,
    TraceStepStatus,
    AnalysisRegion,
)


HOTSPOT_LIBRARY: list[dict] = [
    {
        "hotspot_id": "hs_01",
        "hotspot_type": HotspotType.roof,
        "source_count": 3,
        "coverage_score": 0.79,
        "object_label": "roof",
        "object_confidence": 0.88,
        "material_type": "dark_roof",
        "material_confidence": 0.74,
        "bbox": BoundingBox(x=112, y=78, w=64, h=48),
        "centroid_offset": (0.0007, 0.0005),
        "trace": [
            (TraceKind.candidate_detected, "Candidate hotspot detected in analysis region."),
            (TraceKind.inspect_object, "Object inspection suggests a roof structure."),
            (TraceKind.request_thermal_evidence, "Requested thermal evidence for roof heat concentration."),
            (TraceKind.infer_surface, "Surface inference suggests a dark roof membrane."),
            (TraceKind.compare_neighbors, "Hotter than 83% of nearby comparable roofs."),
            (TraceKind.check_consistency, "Signal remains consistent across nearby roof crops."),
            (TraceKind.score_hotspot, "Scored hotspot after anomaly, severity, and confidence checks."),
            (TraceKind.finalize_hotspot, "Hotspot passed anomaly gate and was finalized for ranking."),
        ],
        "anomaly_score": 0.82,
        "severity_score": 0.76,
        "confidence_score": 0.71,
        "recommended_action": "cool-roof retrofit",
        "why": [
            "high relative anomaly vs nearby roofs",
            "large exposed dark surface",
            "high-confidence thermal evidence",
        ],
    },
    {
        "hotspot_id": "hs_02",
        "hotspot_type": HotspotType.road_pavement,
        "source_count": 2,
        "coverage_score": 0.64,
        "object_label": "road",
        "object_confidence": 0.91,
        "material_type": "asphalt",
        "material_confidence": 0.86,
        "bbox": BoundingBox(x=214, y=166, w=86, h=30),
        "centroid_offset": (-0.0003, 0.0008),
        "trace": [
            (TraceKind.candidate_detected, "Candidate hotspot detected in analysis region."),
            (TraceKind.inspect_object, "Object inspection suggests a road or pavement segment."),
            (TraceKind.request_thermal_evidence, "Requested thermal evidence for pavement heat profile."),
            (TraceKind.compare_neighbors, "Heat is consistent with nearby roads and paved surfaces."),
            (TraceKind.score_hotspot, "Scored hotspot and found anomaly too low to escalate."),
            (TraceKind.discard_hotspot, "Discarded because the heat pattern is expected locally."),
        ],
        "anomaly_score": 0.18,
        "severity_score": 0.58,
        "confidence_score": 0.84,
        "discard_reason": "expected road heat profile",
        "why": [
            "heat pattern matches nearby paved surfaces",
            "low structural anomaly despite visible heat",
        ],
    },
    {
        "hotspot_id": "hs_03",
        "hotspot_type": HotspotType.hvac_mechanical,
        "source_count": 2,
        "coverage_score": 0.72,
        "object_label": "rooftop_hvac",
        "object_confidence": 0.83,
        "material_type": "metal_equipment",
        "material_confidence": 0.71,
        "bbox": BoundingBox(x=298, y=104, w=38, h=40),
        "centroid_offset": (0.0004, -0.0004),
        "trace": [
            (TraceKind.candidate_detected, "Candidate hotspot detected in analysis region."),
            (TraceKind.inspect_object, "Object inspection suggests rooftop HVAC equipment."),
            (TraceKind.request_thermal_evidence, "Requested thermal evidence for localized heat release."),
            (TraceKind.infer_surface, "Thermal pattern is concentrated around mechanical equipment."),
            (TraceKind.score_hotspot, "Scored hotspot after evidence gathering."),
            (TraceKind.finalize_hotspot, "Finalized as a high-priority mechanical inspection candidate."),
        ],
        "anomaly_score": 0.67,
        "severity_score": 0.81,
        "confidence_score": 0.79,
        "recommended_action": "hvac inspection",
        "why": [
            "localized mechanical heat concentration",
            "clear hotspot boundary with strong confidence",
        ],
    },
    {
        "hotspot_id": "hs_04",
        "hotspot_type": HotspotType.parking_lot,
        "source_count": 4,
        "coverage_score": 0.83,
        "object_label": "parking_lot",
        "object_confidence": 0.9,
        "material_type": "asphalt",
        "material_confidence": 0.82,
        "bbox": BoundingBox(x=354, y=208, w=92, h=58),
        "centroid_offset": (-0.0006, -0.0007),
        "trace": [
            (TraceKind.candidate_detected, "Candidate hotspot detected in analysis region."),
            (TraceKind.inspect_object, "Object inspection suggests a parking lot surface."),
            (TraceKind.request_thermal_evidence, "Requested thermal evidence for surface heat intensity."),
            (TraceKind.compare_neighbors, "Hotter than nearby paved surfaces with limited shade."),
            (TraceKind.score_hotspot, "Scored hotspot after context comparison."),
            (TraceKind.finalize_hotspot, "Finalized as a mitigation candidate after passing anomaly gate."),
        ],
        "anomaly_score": 0.56,
        "severity_score": 0.73,
        "confidence_score": 0.75,
        "recommended_action": "shade and pavement mitigation",
        "why": [
            "low-shade paved area with meaningful heat buildup",
            "hotter than comparable nearby paved areas",
        ],
    },
]

ANOMALY_THRESHOLD = 0.25
STEP_INTERVAL_MS = 1200
RANKING_FORMULA = "final_rank_score = severity_score * confidence_score after anomaly gate"

DEMO_REGION_PRESETS: list[dict] = [
    {"label": "downtown_core", "lat": 38.6270, "lng": -90.1994, "radius_m": 120},
    {"label": "industrial_corridor", "lat": 38.6155, "lng": -90.2152, "radius_m": 140},
    {"label": "campus_zone", "lat": 38.6483, "lng": -90.3108, "radius_m": 110},
]


def _trace_evidence(seed: dict, kind: TraceKind) -> TraceEvidence:
    evidence = TraceEvidence()
    if kind == TraceKind.inspect_object:
        evidence.object_confidence = max(seed["confidence_score"] - 0.05, 0.5)
        evidence.object_label = seed["object_label"]
        evidence.source_count = seed["source_count"]
        evidence.coverage_score = seed["coverage_score"]
    elif kind == TraceKind.infer_surface:
        evidence.material_type = seed["material_type"]
        evidence.material_confidence = max(seed["confidence_score"] - 0.08, 0.45)
        evidence.source_count = seed["source_count"]
        evidence.coverage_score = seed["coverage_score"]
    elif kind == TraceKind.compare_neighbors:
        evidence.neighbor_count = 12
        evidence.relative_percentile = seed["anomaly_score"]
        evidence.coverage_score = seed["coverage_score"]
    elif kind == TraceKind.check_consistency:
        evidence.consistency_score = min(seed["confidence_score"] + 0.08, 0.99)
        evidence.coverage_score = seed["coverage_score"]
    elif kind == TraceKind.score_hotspot:
        evidence.anomaly_score = seed["anomaly_score"]
        evidence.severity_score = seed["severity_score"]
        evidence.confidence_score = seed["confidence_score"]
        evidence.coverage_score = seed["coverage_score"]
    return evidence


def build_perception_evidence(seed: dict) -> PerceptionEvidence:
    return PerceptionEvidence(
        hotspot_id=seed["hotspot_id"],
        hotspot_type=seed["hotspot_type"],
        object_label=seed["object_label"],
        object_confidence=seed["object_confidence"],
        source_count=seed["source_count"],
        coverage_score=seed["coverage_score"],
        material_type=seed["material_type"],
        material_confidence=seed["material_confidence"],
    )


def build_scoring_result(seed: dict) -> ScoringResult:
    final_rank_score = None
    discard_reason = seed.get("discard_reason")
    if seed["anomaly_score"] >= ANOMALY_THRESHOLD and "recommended_action" in seed:
        final_rank_score = round(seed["severity_score"] * seed["confidence_score"], 4)
    return ScoringResult(
        hotspot_id=seed["hotspot_id"],
        anomaly_score=seed["anomaly_score"],
        severity_score=seed["severity_score"],
        confidence_score=seed["confidence_score"],
        coverage_score=seed["coverage_score"],
        metadata_quality_score=round((seed["coverage_score"] + 0.15), 2),
        final_rank_score=final_rank_score,
        discard_reason=discard_reason,
        why=seed["why"],
    )


def _build_trace(seed: dict) -> tuple[list[TraceStep], list[AnalysisEvent]]:
    now = datetime.now(UTC)
    trace: list[TraceStep] = []
    events: list[AnalysisEvent] = []

    for index, (kind, summary) in enumerate(seed["trace"]):
        started_at = now if index == 0 else None
        completed_at = now if index == 0 else None
        status = TraceStepStatus.completed if index == 0 else TraceStepStatus.pending
        step_id = f"{seed['hotspot_id']}_step_{index + 1:02d}"
        trace.append(
            TraceStep(
                step_id=step_id,
                hotspot_id=seed["hotspot_id"],
                kind=kind,
                status=status,
                started_at=started_at,
                completed_at=completed_at,
                summary=summary,
                evidence=_trace_evidence(seed, kind),
            )
        )
        events.append(
            AnalysisEvent(
                region_id="",
                hotspot_id=seed["hotspot_id"],
                step_id=step_id,
                kind=kind,
                status=status,
                summary=summary,
                scheduled_offset_ms=index * STEP_INTERVAL_MS,
            )
        )
    return trace, events


def build_analysis(center: LatLng, radius_m: int, region_id: str) -> tuple[AnalysisResponse, list[AnalysisEvent]]:
    hotspots: list[HotspotCandidate] = []
    top_ranked: list[RankedHotspot] = []
    all_events: list[AnalysisEvent] = []
    source_records = retrieve_sources_for_region(center, radius_m)
    region_coverage_score = estimate_region_coverage_score(source_records)
    enrichment_summary = summarize_enrichment_coverage(source_records, center)

    for seed in HOTSPOT_LIBRARY:
        trace, events = _build_trace(seed)
        for event in events:
            event.region_id = region_id
        final_rank_score = None
        status = HotspotStatus.investigating

        if seed["anomaly_score"] < ANOMALY_THRESHOLD:
            status = HotspotStatus.discarded
        elif trace[-1].kind == TraceKind.finalize_hotspot:
            status = HotspotStatus.finalized
            final_rank_score = round(seed["severity_score"] * seed["confidence_score"], 4)

        hotspot = HotspotCandidate(
            hotspot_id=seed["hotspot_id"],
            region_id=region_id,
            bbox=seed["bbox"],
            centroid=LatLng(
                lat=round(center.lat + seed["centroid_offset"][0], 6),
                lng=round(center.lng + seed["centroid_offset"][1], 6),
            ),
            hotspot_type=seed["hotspot_type"],
            status=status,
            source_count=seed["source_count"],
            coverage_score=seed["coverage_score"],
            anomaly_score=seed["anomaly_score"],
            severity_score=seed["severity_score"],
            confidence_score=seed["confidence_score"],
            final_rank_score=final_rank_score,
            discard_reason=seed.get("discard_reason"),
            recommended_action=seed.get("recommended_action"),
            why=seed["why"],
            trace=trace,
        )
        hotspots.append(hotspot)
        all_events.extend(events)

        if status == HotspotStatus.finalized and final_rank_score is not None:
            top_ranked.append(
                RankedHotspot(
                    hotspot_id=hotspot.hotspot_id,
                    priority_rank=0,
                    hotspot_type=hotspot.hotspot_type,
                    recommended_action=hotspot.recommended_action or "investigate",
                    anomaly_score=hotspot.anomaly_score or 0.0,
                    severity_score=hotspot.severity_score or 0.0,
                    confidence_score=hotspot.confidence_score or 0.0,
                    final_rank_score=final_rank_score,
                    why=hotspot.why,
                )
            )

    top_ranked.sort(key=lambda item: item.final_rank_score, reverse=True)
    for index, item in enumerate(top_ranked, start=1):
        item.priority_rank = index

    summary = AnalysisSummary(
        candidate_count=len(hotspots),
        discarded_count=sum(1 for hotspot in hotspots if hotspot.status == HotspotStatus.discarded),
        finalized_count=sum(1 for hotspot in hotspots if hotspot.status == HotspotStatus.finalized),
    )

    response = AnalysisResponse(
        region=AnalysisRegion(
            region_id=region_id,
            center=center,
            radius_m=radius_m,
            available_source_count=len(source_records),
            coverage_score=region_coverage_score,
            maps_fallback_count=int(enrichment_summary["maps_fallback_count"]),
            enrichment_confidence_avg=float(enrichment_summary["enrichment_confidence_avg"]),
            source_records=source_records,
            status=AnalysisStatus.running,
            summary=summary,
        ),
        result=AnalysisResult(
            region_id=region_id,
            status=AnalysisStatus.running,
            hotspots=hotspots,
            top_hotspots=top_ranked,
        ),
    )
    return response, all_events


def build_debug_view(analysis: AnalysisResponse) -> DebugAnalysisView:
    hotspots: list[DebugHotspotView] = []
    hotspot_lookup = {seed["hotspot_id"]: seed for seed in HOTSPOT_LIBRARY}

    for hotspot in analysis.result.hotspots:
        seed = hotspot_lookup[hotspot.hotspot_id]
        hotspots.append(
            DebugHotspotView(
                hotspot_id=hotspot.hotspot_id,
                hotspot_type=hotspot.hotspot_type,
                status=hotspot.status,
                perception=build_perception_evidence(seed),
                scoring=build_scoring_result(seed),
                trace_kinds=[step.kind for step in hotspot.trace],
            )
        )

    return DebugAnalysisView(
        region_id=analysis.region.region_id,
        status=analysis.result.status,
        hotspot_count=len(hotspots),
        ranking_formula=RANKING_FORMULA,
        anomaly_threshold=ANOMALY_THRESHOLD,
        hotspots=hotspots,
    )
