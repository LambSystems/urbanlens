from __future__ import annotations

from . import __doc__  # noqa: F401
from ..llm import get_llm_provider
from ..heat_risk import analyze_heat_risk
from ..schemas import AnalysisResponse, PlannerQuestionResponse


def _get_hotspot(analysis: AnalysisResponse, hotspot_id: str):
    for hotspot in analysis.result.hotspots:
        if hotspot.hotspot_id == hotspot_id:
            return hotspot
    return None


def _thermal_phrase(hotspot) -> str:
    if hotspot.surface_temperature_c is None or hotspot.ambient_delta_c is None:
        return "Thermal evidence is available for this hotspot."
    return (
        f"Thermal evidence shows an estimated surface temperature of {hotspot.surface_temperature_c:.1f} C "
        f"with an ambient delta of {hotspot.ambient_delta_c:.1f} C."
    )


def _risk_phrase(hotspot) -> str:
    risk = analyze_heat_risk(
        hotspot_type=hotspot.hotspot_type,
        surface_temperature_c=hotspot.surface_temperature_c,
        coverage_score=hotspot.coverage_score,
    )
    factors = ", ".join(risk["factors"][:3])
    return (
        f"The Heat Risk Profile scored this area at {risk['heat_risk_score']:.2f} "
        f"based on factors like {factors}."
    )


def _coverage_phrase(hotspot) -> str:
    if hotspot.coverage_score is None:
        return "Coverage details are limited."
    return (
        f"Confidence is supported by coverage score {hotspot.coverage_score:.2f} "
        f"across {hotspot.source_count} source views."
    )


def answer_region_question(analysis: AnalysisResponse, question: str) -> PlannerQuestionResponse:
    q = question.strip()
    q_lower = q.lower()

    top_hotspots = analysis.result.top_hotspots
    hotspots = analysis.result.hotspots
    referenced: list[str] = []

    if (
        "fix first" in q_lower
        or "priority" in q_lower
        or "inspect first" in q_lower
        or "first here" in q_lower
        or "what should we inspect" in q_lower
    ):
        if top_hotspots:
            top = top_hotspots[0]
            top_hotspot = _get_hotspot(analysis, top.hotspot_id)
            referenced = [top.hotspot_id]
            answer = (
                f"You should prioritize {top.hotspot_id} first. "
                f"It is a {top.hotspot_type.value.replace('_', ' ')} hotspot with anomaly {top.anomaly_score:.2f}, "
                f"severity {top.severity_score:.2f}, confidence {top.confidence_score:.2f}, "
                f"and the recommended action is {top.recommended_action}. "
                f"{_thermal_phrase(top_hotspot)} "
                f"{_risk_phrase(top_hotspot)}"
            )
        else:
            answer = "There are no finalized hotspots yet, so I cannot recommend a first intervention."
    elif "discard" in q_lower:
        discarded = [hotspot for hotspot in hotspots if hotspot.status.value == "discarded"]
        if discarded:
            hotspot = discarded[0]
            referenced = [hotspot.hotspot_id]
            reason = hotspot.discard_reason or "it did not pass the anomaly or confidence checks"
            answer = (
                f"{hotspot.hotspot_id} was discarded because {reason}. "
                f"{_thermal_phrase(hotspot)} "
                f"{_risk_phrase(hotspot)}"
            )
        else:
            answer = "No hotspots have been discarded in the current analysis."
    elif "why" in q_lower and analysis.result.top_hotspot_id:
        hotspot = _get_hotspot(analysis, analysis.result.top_hotspot_id)
        referenced = [hotspot.hotspot_id]
        answer = (
            f"{hotspot.hotspot_id} ranked first because it stayed strong across both Thermal Evidence and the Heat Risk Profile. "
            f"{_thermal_phrase(hotspot)} "
            f"{_risk_phrase(hotspot)} "
            f"It also kept confidence at {hotspot.confidence_score:.2f}. "
            f"{_coverage_phrase(hotspot)}"
        )
    elif "strongest anomaly" in q_lower or "highest anomaly" in q_lower:
        best = max(hotspots, key=lambda hotspot: hotspot.anomaly_score or -1)
        referenced = [best.hotspot_id]
        answer = (
            f"{best.hotspot_id} has the strongest anomaly at {best.anomaly_score:.2f}. "
            f"It is classified as {best.hotspot_type.value.replace('_', ' ')}. "
            f"{_thermal_phrase(best)} "
            f"{_risk_phrase(best)}"
        )
    elif "roof" in q_lower:
        roof_ranked = [hotspot for hotspot in top_hotspots if hotspot.hotspot_type.value == "roof"]
        if roof_ranked:
            ranked = roof_ranked[0]
            hotspot = _get_hotspot(analysis, ranked.hotspot_id)
            referenced = [ranked.hotspot_id]
            answer = (
                f"For roof-related hotspots, the current recommended action is {ranked.recommended_action} "
                f"for {ranked.hotspot_id}. "
                f"{_thermal_phrase(hotspot)} "
                f"{_risk_phrase(hotspot)}"
            )
        else:
            answer = "There are no finalized roof hotspots in the current analysis."
    else:
        if top_hotspots:
            ids = ", ".join(hotspot.hotspot_id for hotspot in top_hotspots[:3])
            referenced = [hotspot.hotspot_id for hotspot in top_hotspots[:3]]
            answer = (
                f"I can answer questions about ranking, discarded hotspots, anomaly strength, Thermal Evidence, Heat Risk Profile findings, and recommended actions. "
                f"Current top hotspots are {ids}."
            )
        else:
            answer = (
                "I can answer questions about ranking, discarded hotspots, anomaly strength, Thermal Evidence, Heat Risk Profile findings, and recommended actions "
                "once analysis results are available."
            )

    provider = get_llm_provider()
    provider_result = provider.generate_text(
        system_prompt="You are a concise urban heat triage assistant.",
        user_prompt=(
            f"Question: {q}\n"
            f"Draft answer: {answer}\n"
            "Rewrite the draft answer briefly and clearly without changing the facts."
        ),
    )

    final_answer = provider_result.text.strip() or answer

    return PlannerQuestionResponse(
        region_id=analysis.region.region_id,
        question=q,
        answer=final_answer,
        referenced_hotspot_ids=referenced,
    )
