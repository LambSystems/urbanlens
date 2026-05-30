from __future__ import annotations

import unittest

from app.demo_data import build_demo_analysis, build_demo_investigation_response, build_demo_planner_response


class DemoModeTests(unittest.TestCase):
    def test_demo_analysis_preserves_ranked_contract(self) -> None:
        analysis, events = build_demo_analysis()

        self.assertEqual(analysis.region.region_id, "demo_washu")
        self.assertEqual(analysis.result.top_hotspot_id, "hs_demo_01")
        self.assertEqual(analysis.result.top_hotspots[0].final_rank_score, 0.6708)
        self.assertGreater(len(events), 0)

    def test_demo_planner_is_deterministic_and_grounded(self) -> None:
        analysis, _events = build_demo_analysis()
        response = build_demo_planner_response(analysis, "what should we fix first?")

        self.assertEqual(response.planner_mode, "demo_mode_analysis_qa")
        self.assertIn("hs_demo_01", response.answer)
        self.assertEqual(response.referenced_hotspot_ids[0], "hs_demo_01")

    def test_demo_session_does_not_require_external_ai(self) -> None:
        response = build_demo_investigation_response("sess_test", "what happened?")

        self.assertEqual(response.session_id, "sess_test")
        self.assertIn("No live LLM", response.answer)
        self.assertEqual(response.chain_of_thought[-1].evidence["external_ai_called"], False)


if __name__ == "__main__":
    unittest.main()
