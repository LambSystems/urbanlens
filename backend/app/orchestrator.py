from __future__ import annotations

from datetime import UTC, datetime
from math import cos, pi

from .providers.google_maps_enrichment import summarize_enrichment_coverage
from .providers.source_retrieval import estimate_region_coverage_score, retrieve_sources_for_region
from .heat_risk import analyze_heat_risk
from .perception.object_classifier import classify_object
from .perception.surface_inference import infer_surface
from .scoring.anomaly import ANOMALY_THRESHOLD, compute_anomaly_score, passes_anomaly_gate
from .scoring.confidence import compute_confidence_score
from .scoring.ranker import compute_final_rank_score, rank_hotspots
from .scoring.severity import compute_severity_score
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


# Candidate-to-seed helpers used when real model output is available.

_TYPE_SEVERITY_WEIGHT: dict[HotspotType, float] = {
    HotspotType.roof:            0.80,
    HotspotType.parking_lot:     0.75,
    HotspotType.hvac_mechanical: 0.90,
    HotspotType.road_pavement:   0.60,
    HotspotType.vegetation_loss: 0.65,
    HotspotType.other:           0.55,
}

_TYPE_RECOMMENDED_ACTION: dict[HotspotType, str] = {
    HotspotType.roof:            "cool-roof retrofit",
    HotspotType.parking_lot:     "shade and pavement mitigation",
    HotspotType.hvac_mechanical: "hvac inspection",
    HotspotType.road_pavement:   "cool-pavement treatment",
    HotspotType.vegetation_loss: "vegetation restoration",
    HotspotType.other:           "site review",
}

_TYPE_TRACE_STEPS: dict[HotspotType, list[tuple[TraceKind, str]]] = {
    HotspotType.roof: [
        (TraceKind.candidate_detected,       "Candidate hotspot detected from thermal model output."),
        (TraceKind.generate_thermal_overlay, "Thermal overlay generated from captured locality imagery."),
        (TraceKind.inspect_object,           "Object inspection suggests a roof surface."),
        (TraceKind.request_thermal_evidence, "Thermal evidence requested for roof heat concentration."),
        (TraceKind.analyze_heat_risk,        "Heat risk profile highlights exposed roof with limited shade."),
        (TraceKind.infer_surface,            "Surface inference suggests a dark roof membrane."),
        (TraceKind.compare_neighbors,        "Surface is hotter than comparable nearby rooftop areas."),
        (TraceKind.score_hotspot,            "Scored after anomaly, severity, and confidence analysis."),
        (TraceKind.finalize_hotspot,         "Passed anomaly gate - finalized for priority ranking."),
    ],
    HotspotType.parking_lot: [
        (TraceKind.candidate_detected,       "Candidate hotspot detected from thermal model output."),
        (TraceKind.generate_thermal_overlay, "Thermal overlay generated from captured locality imagery."),
        (TraceKind.inspect_object,           "Object inspection suggests a parking lot surface."),
        (TraceKind.request_thermal_evidence, "Thermal evidence requested for surface heat intensity."),
        (TraceKind.analyze_heat_risk,        "Heat risk profile highlights high paved exposure with limited shade."),
        (TraceKind.compare_neighbors,        "Hotter than nearby paved surfaces with limited shade."),
        (TraceKind.score_hotspot,            "Scored after context comparison."),
        (TraceKind.finalize_hotspot,         "Finalized as a mitigation candidate after passing anomaly gate."),
    ],
    HotspotType.hvac_mechanical: [
        (TraceKind.candidate_detected,       "Candidate hotspot detected from thermal model output."),
        (TraceKind.generate_thermal_overlay, "Thermal overlay generated from captured locality imagery."),
        (TraceKind.inspect_object,           "Object inspection suggests rooftop HVAC equipment."),
        (TraceKind.request_thermal_evidence, "Thermal evidence requested for localized heat release."),
        (TraceKind.analyze_heat_risk,        "Heat risk profile highlights concentrated rooftop equipment exposure."),
        (TraceKind.infer_surface,            "Thermal pattern is concentrated around mechanical equipment."),
        (TraceKind.score_hotspot,            "Scored after evidence gathering."),
        (TraceKind.finalize_hotspot,         "Finalized as a high-priority mechanical inspection candidate."),
    ],
    HotspotType.road_pavement: [
        (TraceKind.candidate_detected,       "Candidate hotspot detected from thermal model output."),
        (TraceKind.generate_thermal_overlay, "Thermal overlay generated from captured locality imagery."),
        (TraceKind.inspect_object,           "Object inspection suggests a road or pavement segment."),
        (TraceKind.request_thermal_evidence, "Thermal evidence requested for pavement heat profile."),
        (TraceKind.analyze_heat_risk,        "Heat risk profile suggests expected paved-surface heat."),
        (TraceKind.compare_neighbors,        "Heat is consistent with nearby roads and paved surfaces."),
        (TraceKind.score_hotspot,            "Scored hotspot - anomaly below threshold for escalation."),
        (TraceKind.discard_hotspot,          "Discarded - heat pattern matches expected road baseline."),
    ],
    HotspotType.vegetation_loss: [
        (TraceKind.candidate_detected,       "Candidate hotspot detected from thermal model output."),
        (TraceKind.generate_thermal_overlay, "Thermal overlay generated from captured locality imagery."),
        (TraceKind.inspect_object,           "Object inspection suggests reduced vegetation coverage."),
        (TraceKind.request_thermal_evidence, "Thermal evidence requested for surface heat from vegetation loss."),
        (TraceKind.analyze_heat_risk,        "Heat risk profile highlights reduced canopy and evapotranspiration."),
        (TraceKind.score_hotspot,            "Scored hotspot after heat risk analysis."),
        (TraceKind.finalize_hotspot,         "Finalized - vegetation loss area contributing to urban heat island."),
    ],
    HotspotType.other: [
        (TraceKind.candidate_detected,       "Candidate hotspot detected from thermal model output."),
        (TraceKind.generate_thermal_overlay, "Thermal overlay generated from captured locality imagery."),
        (TraceKind.request_thermal_evidence, "Thermal evidence requested for brightness and boundary analysis."),
        (TraceKind.score_hotspot,            "Scored hotspot using thermal brightness, area, and confidence."),
        (TraceKind.finalize_hotspot,         "Finalized for site review because surface type is unclassified."),
    ],
}


def _why_for_candidate(htype: HotspotType, intensity: float, surface_temp: float) -> list[str]:
    reasons = [f"thermal model detected elevated surface temperature ({surface_temp:.1f} C)"]
    if intensity >= 0.75:
        reasons.append("high relative thermal intensity vs surrounding area")
    elif intensity >= 0.55:
        reasons.append("moderate thermal intensity with clear hotspot boundary")
    if htype == HotspotType.other:
        reasons.append("surface type is unclassified; ThermalGen localizes heat but does not identify objects")
    else:
        label = HOTSPOT_LABELS[htype]
        reasons.append(f"{label.lower()} surface type identified from supporting RGB crop inspection")
    return reasons


def _display_name_for_seed(seed: dict) -> str:
    htype = seed["hotspot_type"]
    return HOTSPOT_LABELS.get(htype, HOTSPOT_LABELS[HotspotType.other])


def _candidate_to_seed(
    candidate: dict,
    hotspot_id: str,
    thermal_min: float,
    thermal_max: float,
    thermal_mean: float,
    image_path: str | None = None,
) -> dict:
    intensity: float = candidate.get("intensity", 0.5)
    bbox: BoundingBox = candidate["bbox"]
    area_px = bbox.w * bbox.h
    fallback_type: HotspotType = candidate["hotspot_type"]

    classification = classify_object(
        image_path=image_path,
        bbox=bbox,
        intensity=intensity,
        fallback_type=fallback_type,
    )
    htype: HotspotType = classification["hotspot_type"]
    surface_family = classification["surface_family"]
    type_confidence = classification["type_confidence"]
    surface = infer_surface(htype, classification.get("visual_features"))

    surface_temp = round(thermal_min + intensity * (thermal_max - thermal_min), 1)
    ambient_delta = round(max(surface_temp - thermal_mean, 0.5), 1)
    coverage_score = round(min(0.50 + intensity * 0.45, 0.95), 2)

    object_label = classification["object_label"]
    material_type = surface["material_type"]
    object_confidence = round(float(classification["object_confidence"]), 2)
    material_confidence = round(float(surface["material_confidence"]), 2)
    anomaly_score = round(min(intensity * 1.05, 0.95), 2)
    # Weight severity by both intensity and area so large hot surfaces rank higher
    area_weight = min(area_px / 5000, 1.0)
    severity_score = round((intensity * 0.7 + area_weight * 0.3) * _TYPE_SEVERITY_WEIGHT.get(htype, 0.7), 2)
    confidence_score = round(min(0.60 + intensity * 0.30, 0.90), 2)

    trace_steps = _TYPE_TRACE_STEPS.get(htype, _TYPE_TRACE_STEPS[HotspotType.other])
    is_road_baseline = htype == HotspotType.road_pavement and intensity < 0.55

    seed: dict = {
        "hotspot_id": hotspot_id,
        "hotspot_type": htype,
        "surface_family": surface_family,
        "type_confidence": type_confidence,
        "surface_temperature_c": surface_temp,
        "ambient_delta_c": ambient_delta,
        "source_count": 1,
        "coverage_score": coverage_score,
        "object_label": object_label,
        "object_confidence": object_confidence,
        "material_type": material_type,
        "material_confidence": material_confidence,
        "classification_method": classification.get("classification_method", "thermal_only"),
        "evidence_urls": [],
        "bbox": bbox,
        "centroid": candidate["centroid"],  # real LatLng from model
        "anomaly_score": anomaly_score,
        "severity_score": severity_score,
        "confidence_score": confidence_score,
        "trace": trace_steps,
        "why": _why_for_candidate(htype, intensity, surface_temp),
    }
    llm_reasoning = classification.get("llm_reasoning")
    if llm_reasoning:
        seed["why"].append(llm_reasoning)
    if not is_road_baseline:
        seed["recommended_action"] = _TYPE_RECOMMENDED_ACTION.get(htype, "site review")
    else:
        seed["discard_reason"] = "expected road heat baseline"

    return seed


def _build_hotspot_from_seed_with_centroid(
    seed: dict,
    region_id: str,
    now: object,
) -> tuple[HotspotCandidate, list[AnalysisEvent]]:
    """Build a HotspotCandidate using seed["centroid"] directly (not offset from center)."""
    trace, events = _build_trace(seed)
    for event in events:
        event.region_id = region_id
    scoring = build_scoring_result(seed)
    status = HotspotStatus.investigating

    if not passes_anomaly_gate(scoring.anomaly_score):
        status = HotspotStatus.discarded
    elif trace[-1].kind == TraceKind.finalize_hotspot:
        status = HotspotStatus.finalized

    hotspot = HotspotCandidate(
        hotspot_id=seed["hotspot_id"],
        region_id=region_id,
        bbox=seed["bbox"],
        centroid=seed["centroid"],
        hotspot_type=seed["hotspot_type"],
        surface_family=seed.get("surface_family"),
        type_confidence=seed.get("type_confidence"),
        display_name=_display_name_for_seed(seed),
        status_label=HOTSPOT_STATUS_LABELS[status],
        sidebar_summary=_sidebar_summary_for_seed(seed, status),
        evidence_highlights=seed["why"],
        tool_signals=_tool_signals_for_seed(seed),
        status=status,
        surface_temperature_c=seed["surface_temperature_c"],
        ambient_delta_c=seed["ambient_delta_c"],
        source_count=seed["source_count"],
        coverage_score=seed["coverage_score"],
        anomaly_score=scoring.anomaly_score,
        severity_score=scoring.severity_score,
        confidence_score=scoring.confidence_score,
        final_rank_score=scoring.final_rank_score,
        discard_reason=scoring.discard_reason,
        recommended_action=seed.get("recommended_action"),
        evidence_urls=seed.get("evidence_urls", []),
        created_at=now,
        updated_at=now,
        why=scoring.why,
        trace=trace,
    )
    return hotspot, events


def build_analysis_from_candidates(
    candidates: list[dict],
    thermal_data: dict,
    center: LatLng,
    radius_m: int,
    region_id: str,
    image_path: str | None = None,
) -> tuple[AnalysisResponse, list[AnalysisEvent]]:
    """Build an AnalysisResponse using real hotspot candidates from the thermal model."""
    now = datetime.now(UTC)
    source_records = retrieve_sources_for_region(center, radius_m)
    region_coverage_score = estimate_region_coverage_score(source_records)
    enrichment_summary = summarize_enrichment_coverage(source_records, center)
    bounds = _region_bounds(center, radius_m)
    area_km2 = _area_km2(bounds)

    t_min = float(thermal_data.get("min_temp_c", 28.0))
    t_max = float(thermal_data.get("max_temp_c", 48.0))
    t_mean = float(thermal_data.get("mean_temp_c", 35.0))

    hotspots: list[HotspotCandidate] = []
    all_events: list[AnalysisEvent] = []

    for i, candidate in enumerate(candidates):
        hotspot_id = f"hs_cap_{i + 1:02d}"
        seed = _candidate_to_seed(candidate, hotspot_id, t_min, t_max, t_mean, image_path=image_path)
        hotspot, events = _build_hotspot_from_seed_with_centroid(seed, region_id, now)
        hotspots.append(hotspot)
        all_events.extend(events)

    top_ranked = rank_hotspots(hotspots, top_n=3)
    top_rank_lookup = {r.hotspot_id: r.priority_rank for r in top_ranked}
    for hotspot in hotspots:
        if hotspot.hotspot_id in top_rank_lookup:
            hotspot.priority_rank = top_rank_lookup[hotspot.hotspot_id]
            hotspot.is_top_ranked = True

    summary = AnalysisSummary(
        candidate_count=len(hotspots),
        discarded_count=sum(1 for h in hotspots if h.status == HotspotStatus.discarded),
        finalized_count=sum(1 for h in hotspots if h.status == HotspotStatus.finalized),
    )

    response = AnalysisResponse(
        region=AnalysisRegion(
            region_id=region_id,
            display_name=_region_display_name(center),
            center=center,
            radius_m=radius_m,
            bounds=bounds,
            area_km2=area_km2,
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
            top_hotspot_id=top_ranked[0].hotspot_id if top_ranked else None,
            discarded_hotspot_ids=[h.hotspot_id for h in hotspots if h.status == HotspotStatus.discarded],
        ),
    )
    return response, all_events


STEP_INTERVAL_MS = 1200
RANKING_FORMULA = "final_rank_score = severity_score * confidence_score after anomaly gate"


HOTSPOT_LABELS: dict[HotspotType, str] = {
    HotspotType.roof: "Building Roof",
    HotspotType.road_pavement: "Road Surface",
    HotspotType.parking_lot: "Parking Lot",
    HotspotType.hvac_mechanical: "HVAC / Mechanical",
    HotspotType.vegetation_loss: "Vegetation Loss",
    HotspotType.other: "Thermal Hotspot",
}

HOTSPOT_STATUS_LABELS: dict[HotspotStatus, str] = {
    HotspotStatus.candidate: "Candidate",
    HotspotStatus.investigating: "Investigating",
    HotspotStatus.evidence_gathered: "Evidence Gathered",
    HotspotStatus.discarded: "Discarded",
    HotspotStatus.finalized: "Recommended",
}


def _region_bounds(center: LatLng, radius_m: int) -> dict[str, float]:
    lat_delta = radius_m / 111_000
    lng_delta = radius_m / (111_000 * max(cos(center.lat * pi / 180), 0.1))
    return {
        "north": round(center.lat + lat_delta, 6),
        "south": round(center.lat - lat_delta, 6),
        "east": round(center.lng + lng_delta, 6),
        "west": round(center.lng - lng_delta, 6),
    }


def _area_km2(bounds: dict[str, float]) -> float:
    lat_diff = bounds["north"] - bounds["south"]
    lng_diff = bounds["east"] - bounds["west"]
    lat_km = lat_diff * 111
    lng_km = lng_diff * 111 * cos(((bounds["north"] + bounds["south"]) / 2) * pi / 180)
    return round(lat_km * lng_km, 3)


def _region_display_name(center: LatLng) -> str:
    return f"Selected Locality ({center.lat:.4f}, {center.lng:.4f})"


def _tool_signals_for_seed(seed: dict) -> list[str]:
    signals: list[str] = []
    trace_kinds = [kind for kind, _ in seed["trace"]]
    if TraceKind.generate_thermal_overlay in trace_kinds or TraceKind.request_thermal_evidence in trace_kinds:
        signals.append("Thermal Evidence")
    if TraceKind.analyze_heat_risk in trace_kinds:
        signals.append("Heat Risk Profile")
    if TraceKind.inspect_object in trace_kinds:
        signals.append("Object Inspection")
    if TraceKind.compare_neighbors in trace_kinds:
        signals.append("Neighbor Comparison")
    return signals


def _sidebar_summary_for_seed(seed: dict, status: HotspotStatus) -> str:
    label = _display_name_for_seed(seed)
    if status == HotspotStatus.discarded:
        reason = seed.get("discard_reason") or "did not pass anomaly or confidence checks"
        return f"{label} was reviewed and discarded because {reason}."
    if status == HotspotStatus.finalized:
        action = seed.get("recommended_action") or "follow-up inspection"
        return f"{label} was recommended after thermal and environmental investigation. Suggested next step: {action}."
    return f"{label} is still being investigated with tool-based evidence gathering."


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
    elif kind == TraceKind.analyze_heat_risk:
        risk = analyze_heat_risk(
            hotspot_type=seed["hotspot_type"],
            surface_temperature_c=seed["surface_temperature_c"],
            coverage_score=seed["coverage_score"],
        )
        evidence.coverage_score = seed["coverage_score"]
        evidence.confidence_score = risk["heat_risk_score"]
    elif kind == TraceKind.check_consistency:
        evidence.consistency_score = min(seed["confidence_score"] + 0.08, 0.99)
        evidence.coverage_score = seed["coverage_score"]
    elif kind == TraceKind.score_hotspot:
        evidence.anomaly_score = seed["anomaly_score"]
        evidence.severity_score = seed["severity_score"]
        evidence.confidence_score = seed["confidence_score"]
        evidence.coverage_score = seed["coverage_score"]
    return evidence


def _trace_details(seed: dict, kind: TraceKind, evidence: TraceEvidence) -> dict:
    details = evidence.model_dump(exclude_none=True)
    if kind == TraceKind.request_thermal_evidence:
        details["surface_temperature_c"] = seed["surface_temperature_c"]
        details["ambient_delta_c"] = seed["ambient_delta_c"]
    if kind == TraceKind.analyze_heat_risk:
        risk = analyze_heat_risk(
            hotspot_type=seed["hotspot_type"],
            surface_temperature_c=seed["surface_temperature_c"],
            coverage_score=seed["coverage_score"],
        )
        details["heat_risk_score"] = risk["heat_risk_score"]
        details["factors"] = risk["factors"]
        details["summary"] = risk["summary"]
    if kind == TraceKind.discard_hotspot and seed.get("discard_reason"):
        details["reason"] = seed["discard_reason"]
    if kind == TraceKind.finalize_hotspot and seed.get("recommended_action"):
        details["recommended_action"] = seed["recommended_action"]
    return details


def build_scoring_result(seed: dict) -> ScoringResult:
    anomaly_score = compute_anomaly_score(
        thermal_intensity=seed["anomaly_score"],
        relative_percentile=seed["anomaly_score"],
        consistency_score=min(seed["coverage_score"] + 0.1, 1.0),
    )
    severity_score = compute_severity_score(
        thermal_intensity=seed["severity_score"],
        area_px=seed["bbox"].w * seed["bbox"].h,
        material_type=seed["material_type"],
    )
    confidence_score = compute_confidence_score(
        object_confidence=seed["object_confidence"],
        material_confidence=seed["material_confidence"],
        coverage_score=seed["coverage_score"],
        metadata_quality_score=round(seed["coverage_score"] + 0.15, 2),
        consistency_score=min(seed["coverage_score"] + 0.1, 1.0),
    )
    final_rank_score = None
    discard_reason = seed.get("discard_reason")
    if passes_anomaly_gate(anomaly_score) and "recommended_action" in seed:
        final_rank_score = compute_final_rank_score(severity_score, confidence_score)
    return ScoringResult(
        hotspot_id=seed["hotspot_id"],
        anomaly_score=anomaly_score,
        severity_score=severity_score,
        confidence_score=confidence_score,
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
        evidence = _trace_evidence(seed, kind)
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
                timestamp_ms=index * STEP_INTERVAL_MS,
                started_at=started_at,
                completed_at=completed_at,
                summary=summary,
                details=_trace_details(seed, kind, evidence),
                evidence=evidence,
            )
        )
        events.append(
            AnalysisEvent(
                region_id="",
                hotspot_id=seed["hotspot_id"],
                step_id=step_id,
                kind=kind,
                status=status,
                timestamp_ms=index * STEP_INTERVAL_MS,
                summary=summary,
                details=_trace_details(seed, kind, evidence),
                scheduled_offset_ms=index * STEP_INTERVAL_MS,
            )
        )
    return trace, events



def build_debug_view(analysis: AnalysisResponse) -> DebugAnalysisView:
    hotspots: list[DebugHotspotView] = []

    for hotspot in analysis.result.hotspots:
        hotspots.append(
            DebugHotspotView(
                hotspot_id=hotspot.hotspot_id,
                hotspot_type=hotspot.hotspot_type,
                status=hotspot.status,
                perception=PerceptionEvidence(
                    hotspot_id=hotspot.hotspot_id,
                    hotspot_type=hotspot.hotspot_type,
                    object_label=hotspot.display_name or hotspot.hotspot_type.value,
                    object_confidence=hotspot.confidence_score or 0.0,
                    source_count=hotspot.source_count,
                    coverage_score=hotspot.coverage_score,
                ),
                scoring=ScoringResult(
                    hotspot_id=hotspot.hotspot_id,
                    anomaly_score=hotspot.anomaly_score or 0.0,
                    severity_score=hotspot.severity_score or 0.0,
                    confidence_score=hotspot.confidence_score or 0.0,
                    coverage_score=hotspot.coverage_score,
                    final_rank_score=hotspot.final_rank_score,
                    discard_reason=hotspot.discard_reason,
                    why=hotspot.why,
                ),
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
