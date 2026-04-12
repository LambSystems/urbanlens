from __future__ import annotations

from . import __doc__  # noqa: F401
from ..schemas import AnalysisResponse, PlannerQuestionResponse


def answer_region_question(analysis: AnalysisResponse, question: str) -> PlannerQuestionResponse:
    q = question.strip()
    q_lower = q.lower()

    top_hotspots = analysis.result.top_hotspots
    hotspots = analysis.result.hotspots
    referenced: list[str] = []

    if "fix first" in q_lower or "priority" in q_lower:
        if top_hotspots:
            top = top_hotspots[0]
            referenced = [top.hotspot_id]
            answer = (
                f"You should prioritize {top.hotspot_id} first. "
                f"It is a {top.hotspot_type.value} hotspot with anomaly {top.anomaly_score:.2f}, "
                f"severity {top.severity_score:.2f}, confidence {top.confidence_score:.2f}, "
                f"and the recommended action is {top.recommended_action}."
            )
        else:
            answer = "There are no finalized hotspots yet, so I cannot recommend a first intervention."
    elif "discard" in q_lower:
        discarded = [hotspot for hotspot in hotspots if hotspot.status.value == "discarded"]
        if discarded:
            hotspot = discarded[0]
            referenced = [hotspot.hotspot_id]
            reason = hotspot.discard_reason or "it did not pass the anomaly or confidence checks"
            answer = f"{hotspot.hotspot_id} was discarded because {reason}."
        else:
            answer = "No hotspots have been discarded in the current analysis."
    elif "strongest anomaly" in q_lower or "highest anomaly" in q_lower:
        best = max(hotspots, key=lambda hotspot: hotspot.anomaly_score or -1)
        referenced = [best.hotspot_id]
        answer = (
            f"{best.hotspot_id} has the strongest anomaly at {best.anomaly_score:.2f}. "
            f"It is classified as {best.hotspot_type.value}."
        )
    elif "roof" in q_lower:
        roof_ranked = [hotspot for hotspot in top_hotspots if hotspot.hotspot_type.value == "roof"]
        if roof_ranked:
            hotspot = roof_ranked[0]
            referenced = [hotspot.hotspot_id]
            answer = (
                f"For roof-related hotspots, the current recommended action is {hotspot.recommended_action} "
                f"for {hotspot.hotspot_id}."
            )
        else:
            answer = "There are no finalized roof hotspots in the current analysis."
    else:
        if top_hotspots:
            ids = ", ".join(hotspot.hotspot_id for hotspot in top_hotspots[:3])
            referenced = [hotspot.hotspot_id for hotspot in top_hotspots[:3]]
            answer = (
                f"I can answer questions about ranking, discarded hotspots, anomaly strength, and recommended actions. "
                f"Current top hotspots are {ids}."
            )
        else:
            answer = (
                "I can answer questions about ranking, discarded hotspots, anomaly strength, and recommended actions "
                "once analysis results are available."
            )

    return PlannerQuestionResponse(
        region_id=analysis.region.region_id,
        question=q,
        answer=answer,
        referenced_hotspot_ids=referenced,
    )
