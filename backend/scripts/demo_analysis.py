from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas import (
    AnalysisRegion,
    AnalysisResponse,
    AnalysisResult,
    AnalysisStatus,
    AnalysisSummary,
    BoundingBox,
    HotspotCandidate,
    HotspotStatus,
    HotspotType,
    LatLng,
)
from app.scoring.ranker import rank_hotspots


def _hotspot(
    hotspot_id: str,
    hotspot_type: HotspotType,
    label: str,
    anomaly: float,
    severity: float,
    confidence: float,
    action: str | None,
    why: list[str],
) -> HotspotCandidate:
    now = datetime.now(UTC)
    final_score = round(severity * confidence, 4) if action else None
    return HotspotCandidate(
        hotspot_id=hotspot_id,
        region_id="demo_washu",
        bbox=BoundingBox(x=96, y=72, w=88, h=64),
        centroid=LatLng(lat=38.6488, lng=-90.3108),
        hotspot_type=hotspot_type,
        display_name=label,
        status=HotspotStatus.finalized if action else HotspotStatus.discarded,
        status_label="Recommended" if action else "Discarded",
        sidebar_summary=f"{label} reviewed by deterministic demo fixture.",
        evidence_highlights=why,
        tool_signals=["Thermal Evidence", "Heat Risk Profile", "Deterministic Scoring"],
        surface_temperature_c=42.0 + anomaly * 10,
        ambient_delta_c=4.0 + anomaly * 8,
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
    )


def build_demo_analysis() -> AnalysisResponse:
    hotspots = [
        _hotspot(
            "hs_demo_01",
            HotspotType.roof,
            "Large Roof Cluster",
            anomaly=0.84,
            severity=0.78,
            confidence=0.86,
            action="cool-roof retrofit",
            why=[
                "relative thermal signal is elevated",
                "large exposed roof surface",
                "low visible shade around the structure",
            ],
        ),
        _hotspot(
            "hs_demo_02",
            HotspotType.parking_lot,
            "Parking Lot",
            anomaly=0.76,
            severity=0.72,
            confidence=0.74,
            action="shade and pavement mitigation",
            why=[
                "broad paved area retains heat",
                "thermal signal is consistent across the lot",
            ],
        ),
        _hotspot(
            "hs_demo_03",
            HotspotType.road_pavement,
            "Road Segment",
            anomaly=0.18,
            severity=0.52,
            confidence=0.69,
            action=None,
            why=[
                "surface appears consistent with expected road baseline",
                "anomaly score does not pass the gate",
            ],
        ),
    ]

    ranked = rank_hotspots(hotspots, top_n=3)
    rank_lookup = {item.hotspot_id: item.priority_rank for item in ranked}
    for hotspot in hotspots:
        if hotspot.hotspot_id in rank_lookup:
            hotspot.priority_rank = rank_lookup[hotspot.hotspot_id]
            hotspot.is_top_ranked = hotspot.priority_rank == 1

    return AnalysisResponse(
        region=AnalysisRegion(
            region_id="demo_washu",
            display_name="Deterministic Demo Locality",
            center=LatLng(lat=38.6488, lng=-90.3108),
            radius_m=120,
            status=AnalysisStatus.completed,
            summary=AnalysisSummary(
                candidate_count=len(hotspots),
                discarded_count=sum(1 for item in hotspots if item.status == HotspotStatus.discarded),
                finalized_count=sum(1 for item in hotspots if item.status == HotspotStatus.finalized),
            ),
        ),
        result=AnalysisResult(
            region_id="demo_washu",
            status=AnalysisStatus.completed,
            hotspots=hotspots,
            top_hotspots=ranked,
            top_hotspot_id=ranked[0].hotspot_id if ranked else None,
            discarded_hotspot_ids=[item.hotspot_id for item in hotspots if item.status == HotspotStatus.discarded],
        ),
    )


def main() -> None:
    analysis = build_demo_analysis()
    payload = {
        "region_id": analysis.region.region_id,
        "status": analysis.result.status.value,
        "summary": analysis.region.summary.model_dump(),
        "ranking_formula": "final_rank_score = severity_score * confidence_score after anomaly gate",
        "top_hotspots": [item.model_dump(mode="json") for item in analysis.result.top_hotspots],
        "discarded_hotspot_ids": analysis.result.discarded_hotspot_ids,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
