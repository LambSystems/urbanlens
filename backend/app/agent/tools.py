"""
UrbanLens — Agent Tool Registry

Defines the internal tools the orchestrator can invoke during investigation.
Tool set is intentionally constrained so the UI trace stays legible.

Canonical tools per docs/contracts.md:
  generate_thermal_overlay, request_thermal_evidence, analyze_heat_risk,
  inspect_object, infer_surface, compare_findings, score_hotspots,
  discard_hotspot, finalize_recommendation
"""
from __future__ import annotations


TOOL_REGISTRY: dict[str, dict] = {
    # ── ThermalGen tools ─────────────────────────────────────────────────────
    "generate_thermal_overlay": {
        "description": "Generate a thermal overlay and thermal statistics from a frontend satellite capture",
        "module": "capture_pipeline",
        "function": "generate_thermal_overlay_from_capture",
    },
    "request_thermal_evidence": {
        "description": "Retrieve thermal intensity and heat pattern for a specific hotspot",
        "module": "thermal.evidence",
        "function": "extract_hotspot_thermal",
    },
    "analyze_heat_risk": {
        "description": "Estimate heat risk drivers from visible locality cues and hotspot context",
        "module": "heat_risk",
        "function": "analyze_heat_risk",
    },

    # ── Heat Risk Profiler ────────────────────────────────────────────────────
    "analyze_heat_risk": {
        "description": (
            "Analyze visible environmental cues in the captured locality to estimate heat risk. "
            "Identifies likely drivers such as dark roofs, exposed pavement, low shade, or large surface exposure."
        ),
        "module": "tools.heat_risk",
        "function": "analyze_heat_risk",
    },

    # ── Perception helpers ────────────────────────────────────────────────────
    "inspect_object": {
        "description": "Identify the object type at this hotspot (roof, road, hvac, parking lot, etc.)",
        "module": "perception.object_classifier",
        "function": "classify_object",
    },
    "infer_surface": {
        "description": "Estimate the surface material (dark roof membrane, asphalt, metal equipment, etc.)",
        "module": "perception.surface_inference",
        "function": "infer_surface",
    },

    # ── Scoring and comparison ────────────────────────────────────────────────
    "compare_findings": {
        "description": "Reconcile thermal evidence against heat-risk profile and other gathered findings",
        "module": "scoring.context",
        "function": "compare_findings",
    },
    "score_hotspots": {
        "description": "Compute anomaly, severity, and confidence scores and rank hotspot candidates",
        "module": "scoring.ranker",
        "function": "score_and_rank",
    },

    # ── Terminal actions ──────────────────────────────────────────────────────
    "discard_hotspot": {
        "description": "Discard this hotspot when the evidence does not justify escalation",
        "module": None,
        "function": None,
    },
    "finalize_recommendation": {
        "description": "Finalize this hotspot for ranking and produce a grounded recommendation",
        "module": None,
        "function": None,
    },
}


def get_tool_descriptions_for_prompt() -> str:
    """Return a bullet list of tool names and descriptions for LLM prompts."""
    lines = []
    for name, meta in TOOL_REGISTRY.items():
        lines.append(f"- {name}: {meta['description']}")
    return "\n".join(lines)


def get_tool_names() -> list[str]:
    return list(TOOL_REGISTRY.keys())
