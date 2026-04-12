from __future__ import annotations

from . import __doc__  # noqa: F401
from ..llm import get_llm_provider
from ..heat_risk import analyze_heat_risk
from ..schemas import AnalysisResponse, HotspotCandidate, PlannerQuestionResponse


def _get_hotspot(analysis: AnalysisResponse, hotspot_id: str) -> HotspotCandidate | None:
    for hotspot in analysis.result.hotspots:
        if hotspot.hotspot_id == hotspot_id:
            return hotspot
    return None


def _label(hotspot: HotspotCandidate) -> str:
    """Human-readable hotspot label — prefer display_name over raw ID."""
    return hotspot.display_name or hotspot.hotspot_type.value.replace("_", " ").title()


def _thermal_phrase(hotspot: HotspotCandidate | None) -> str:
    if hotspot is None or hotspot.surface_temperature_c is None or hotspot.ambient_delta_c is None:
        return "Thermal evidence is available for this hotspot."
    return (
        f"Thermal evidence shows an estimated surface temperature of {hotspot.surface_temperature_c:.1f}°C "
        f"with an ambient delta of +{hotspot.ambient_delta_c:.1f}°C."
    )


def _risk_phrase(hotspot: HotspotCandidate | None) -> str:
    if hotspot is None:
        return ""
    risk = analyze_heat_risk(
        hotspot_type=hotspot.hotspot_type,
        surface_temperature_c=hotspot.surface_temperature_c,
        coverage_score=hotspot.coverage_score,
    )
    factors = ", ".join(risk["factors"][:3])
    return (
        f"The Heat Risk Profile scored this area at {risk['heat_risk_score']:.2f} "
        f"based on: {factors}."
    )


def _coverage_phrase(hotspot: HotspotCandidate) -> str:
    if hotspot.coverage_score is None:
        return "Coverage details are limited."
    return (
        f"Confidence is supported by a coverage score of {hotspot.coverage_score:.2f} "
        f"across {hotspot.source_count} source views."
    )


def _build_analysis_context(analysis: AnalysisResponse) -> str:
    """
    Build a rich plain-text summary of the full analysis for LLM context.
    This is what lets the LLM answer any locality question grounded in real data.
    """
    lines: list[str] = [
        f"Region: {analysis.region.display_name or 'Selected locality'}",
        f"Analysis status: {analysis.result.status.value}",
        f"Hotspots found: {len(analysis.result.hotspots)} "
        f"({analysis.region.summary.finalized_count} finalized, "
        f"{analysis.region.summary.discarded_count} discarded)",
        "",
        "Hotspot findings:",
    ]
    for h in analysis.result.hotspots:
        status = h.status.value
        label = _label(h)
        line = f"  - {label} [{h.hotspot_id}]: status={status}"
        if h.anomaly_score is not None:
            line += f", anomaly={h.anomaly_score:.2f}"
        if h.severity_score is not None:
            line += f", severity={h.severity_score:.2f}"
        if h.confidence_score is not None:
            line += f", confidence={h.confidence_score:.2f}"
        if h.surface_temperature_c is not None:
            line += f", surface_temp={h.surface_temperature_c:.1f}°C"
        if h.ambient_delta_c is not None:
            line += f", delta=+{h.ambient_delta_c:.1f}°C"
        if h.recommended_action:
            line += f", recommended_action={h.recommended_action}"
        if h.discard_reason:
            line += f", discard_reason={h.discard_reason}"
        lines.append(line)
        if h.why:
            lines.append(f"    Evidence: {'; '.join(h.why)}")
        if h.sidebar_summary:
            lines.append(f"    Summary: {h.sidebar_summary}")

    if analysis.result.top_hotspots:
        lines.append("")
        lines.append("Priority ranking (top hotspots):")
        for r in analysis.result.top_hotspots:
            label = _label(_get_hotspot(analysis, r.hotspot_id) or r)  # type: ignore[arg-type]
            lines.append(
                f"  #{r.priority_rank} {label} [{r.hotspot_id}]: "
                f"action={r.recommended_action}, "
                f"final_rank_score={r.final_rank_score:.3f}"
            )

    return "\n".join(lines)


def answer_region_question(analysis: AnalysisResponse, question: str) -> PlannerQuestionResponse:
    q = question.strip()
    q_lower = q.lower()

    top_hotspots = analysis.result.top_hotspots
    hotspots = analysis.result.hotspots
    referenced: list[str] = []
    answer_title = "Agent Analysis"
    answer_sections: list[str] = []
    draft_answer = ""

    # ── Structured fast-path patterns ─────────────────────────────────────────
    # These populate answer_sections for the structured UI even when LLM refines
    # the prose answer.  All other questions fall through to the LLM free-form path.

    if any(kw in q_lower for kw in ("fix first", "priority", "inspect first", "first here", "what should we inspect")):
        if top_hotspots:
            top = top_hotspots[0]
            top_hotspot = _get_hotspot(analysis, top.hotspot_id)
            referenced = [top.hotspot_id]
            answer_title = "Top Inspection Priority"
            answer_sections = [
                f"{_label(top_hotspot)} is the highest-priority hotspot.",  # type: ignore[arg-type]
                _thermal_phrase(top_hotspot),
                _risk_phrase(top_hotspot),
                f"Recommended action: {top.recommended_action}",
            ]
            draft_answer = (
                f"Prioritize {_label(top_hotspot)} first. "  # type: ignore[arg-type]
                f"Anomaly {top.anomaly_score:.2f}, severity {top.severity_score:.2f}, "
                f"confidence {top.confidence_score:.2f}. "
                f"Recommended action: {top.recommended_action}. "
                f"{_thermal_phrase(top_hotspot)} {_risk_phrase(top_hotspot)}"
            )
        else:
            draft_answer = "There are no finalized hotspots yet to recommend."

    elif "discard" in q_lower:
        discarded = [h for h in hotspots if h.status.value == "discarded"]
        if discarded:
            h = discarded[0]
            referenced = [h.hotspot_id]
            reason = h.discard_reason or "it did not pass the anomaly gate"
            answer_title = "Discard Explanation"
            answer_sections = [
                f"{_label(h)} was discarded.",
                f"Reason: {reason}",
                _thermal_phrase(h),
                _risk_phrase(h),
            ]
            draft_answer = (
                f"{_label(h)} was discarded because {reason}. "
                f"{_thermal_phrase(h)} {_risk_phrase(h)}"
            )
        else:
            draft_answer = "No hotspots have been discarded in the current analysis."

    elif "why" in q_lower and analysis.result.top_hotspot_id:
        h = _get_hotspot(analysis, analysis.result.top_hotspot_id)
        if h:
            referenced = [h.hotspot_id]
            answer_title = "Why This Ranked First"
            answer_sections = [
                f"{_label(h)} ranked first.",
                _thermal_phrase(h),
                _risk_phrase(h),
                _coverage_phrase(h),
            ]
            draft_answer = (
                f"{_label(h)} ranked first because it scored strongly across both "
                f"Thermal Evidence and Heat Risk Profile. "
                f"{_thermal_phrase(h)} {_risk_phrase(h)} "
                f"Confidence: {h.confidence_score:.2f}. {_coverage_phrase(h)}"
            )

    elif any(kw in q_lower for kw in ("strongest anomaly", "highest anomaly")):
        if hotspots:
            best = max(hotspots, key=lambda h: h.anomaly_score or -1)
            referenced = [best.hotspot_id]
            answer_title = "Strongest Anomaly"
            answer_sections = [
                f"{_label(best)} has the highest anomaly score ({best.anomaly_score:.2f}).",
                _thermal_phrase(best),
                _risk_phrase(best),
            ]
            draft_answer = (
                f"{_label(best)} has the strongest anomaly at {best.anomaly_score:.2f}. "
                f"{_thermal_phrase(best)} {_risk_phrase(best)}"
            )

    # ── Free-form LLM path for everything else ────────────────────────────────
    # The LLM receives the full analysis context and answers the question directly.
    # This handles any locality question the user asks.

    context = _build_analysis_context(analysis)
    provider = get_llm_provider()

    if draft_answer:
        # Structured match — LLM polishes the draft, keeps the facts
        provider_result = provider.generate_text(
            system_prompt=(
                "You are a precise urban heat triage assistant. "
                "Refine the draft answer to be clear and natural. "
                "Do not add facts that are not in the draft. Return only the answer."
            ),
            user_prompt=(
                f"Analysis context:\n{context}\n\n"
                f"Question: {q}\n"
                f"Draft: {draft_answer}\n\n"
                "Return the refined answer only."
            ),
        )
        final_answer = provider_result.text.strip() or draft_answer
    else:
        # Unrecognised question — LLM answers freely from full analysis context
        referenced = [h.hotspot_id for h in top_hotspots[:3]]
        provider_result = provider.generate_text(
            system_prompt=(
                "You are an expert urban heat triage agent analyzing a real locality. "
                "Answer the user's question using ONLY the analysis data provided. "
                "Be specific: cite hotspot types, surface temperatures, recommended actions, and risk factors. "
                "For location or intervention questions (tree planting, shade, cooling), "
                "reason from hotspot types and heat evidence — e.g. parking lots and bare roofs "
                "benefit most from shade trees and cool-surface interventions. "
                "Keep the answer to 3-5 sentences. Do not say you cannot answer."
            ),
            user_prompt=(
                f"Analysis context:\n{context}\n\n"
                f"Question: {q}\n\n"
                "Answer based on the analysis data above. Be concrete and actionable."
            ),
        )
        final_answer = provider_result.text.strip()

        if not final_answer:
            # LLM unavailable — build a reasonable answer from context
            if top_hotspots:
                top = top_hotspots[0]
                top_h = _get_hotspot(analysis, top.hotspot_id)
                final_answer = (
                    f"Based on this analysis, the most impactful area to address is the "
                    f"{_label(top_h)} ({_thermal_phrase(top_h)}). "  # type: ignore[arg-type]
                    f"{_risk_phrase(top_h)} "  # type: ignore[arg-type]
                    f"Recommended action: {top.recommended_action}."
                )
                answer_sections = [final_answer]
            else:
                final_answer = "Analysis is still in progress. Please ask once the investigation completes."

        answer_title = "Agent Response"
        # Build answer_sections from the LLM response paragraphs for cleaner UI display
        if not answer_sections:
            answer_sections = [s.strip() for s in final_answer.split(". ") if s.strip()]

    return PlannerQuestionResponse(
        region_id=analysis.region.region_id,
        question=q,
        answer=final_answer,
        answer_title=answer_title,
        answer_sections=answer_sections,
        referenced_hotspot_ids=referenced,
    )
