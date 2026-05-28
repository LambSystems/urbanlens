from __future__ import annotations

import unittest

from app.schemas import BoundingBox, HotspotCandidate, HotspotStatus, HotspotType, LatLng
from app.scoring.anomaly import ANOMALY_THRESHOLD, passes_anomaly_gate
from app.scoring.ranker import compute_final_rank_score, rank_hotspots


def _hotspot(
    hotspot_id: str,
    anomaly: float,
    severity: float,
    confidence: float,
    recommended_action: str = "inspect surface",
) -> HotspotCandidate:
    return HotspotCandidate(
        hotspot_id=hotspot_id,
        region_id="region_test",
        bbox=BoundingBox(x=0, y=0, w=32, h=32),
        centroid=LatLng(lat=38.627, lng=-90.1994),
        hotspot_type=HotspotType.roof,
        status=HotspotStatus.finalized,
        source_count=1,
        anomaly_score=anomaly,
        severity_score=severity,
        confidence_score=confidence,
        recommended_action=recommended_action,
        why=["test evidence"],
    )


class ScoringTests(unittest.TestCase):
    def test_anomaly_gate_is_threshold_inclusive(self) -> None:
        self.assertFalse(passes_anomaly_gate(ANOMALY_THRESHOLD - 0.001))
        self.assertTrue(passes_anomaly_gate(ANOMALY_THRESHOLD))

    def test_final_rank_score_is_severity_times_confidence(self) -> None:
        self.assertEqual(compute_final_rank_score(0.8, 0.75), 0.6)
        self.assertEqual(compute_final_rank_score(0.33333, 0.77777), 0.2593)

    def test_rank_hotspots_filters_anomaly_failures_and_orders_survivors(self) -> None:
        low_anomaly = _hotspot("hs_low_anomaly", 0.1, 1.0, 1.0)
        medium = _hotspot("hs_medium", 0.7, 0.7, 0.7)
        high = _hotspot("hs_high", 0.7, 0.9, 0.8)

        ranked = rank_hotspots([low_anomaly, medium, high], top_n=3)

        self.assertEqual([item.hotspot_id for item in ranked], ["hs_high", "hs_medium"])
        self.assertEqual(ranked[0].priority_rank, 1)
        self.assertEqual(ranked[0].final_rank_score, 0.72)


if __name__ == "__main__":
    unittest.main()
