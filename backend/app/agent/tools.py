"""
Urban Legend - Agent Tool Registry

Defines the internal tools the orchestrator can invoke during investigation.
The tool set is intentionally constrained so the UI trace stays legible.
"""
from __future__ import annotations


TOOL_REGISTRY: dict[str, dict] = {
    # Capture and thermal tools
    "generate_thermal_overlay": {
        "description": "Generate a thermal overlay and thermal statistics from a frontend satellite capture",
        "module": "capture_pipeline",
        "function": "generate_thermal_overlay_from_capture",
    },
    "propose_hotspots_from_capture": {
        "description": "Propose hotspot candidates from satellite capture and thermal output",
        "module": "capture_pipeline",
        "function": "propose_hotspots_from_capture",
    },

    # Perception tools
    "inspect_object": {
        "description": "Identify the object type at this hotspot (roof, road, hvac, etc.)",
        "module": "perception.object_classifier",
        "function": "classify_object",
    },
    "infer_surface": {
        "description": "Estimate the surface material (dark roof, asphalt, metal, etc.)",
        "module": "perception.surface_inference",
        "function": "infer_surface",
    },
    "list_hotspot_candidates": {
        "description": "List all hotspot candidates detected in the analysis region",
        "module": "perception.candidate_discovery",
        "function": "propose_candidates",
    },

    # Thermal tools
    "request_thermal_evidence": {
        "description": "Retrieve thermal intensity and heat pattern for a hotspot",
        "module": "thermal.evidence",
        "function": "extract_hotspot_thermal",
    },

    # Context and scoring tools
    "compare_neighbors": {
        "description": "Compare this hotspot against nearby similar structures",
        "module": "scoring.context",
        "function": "compare_neighbors",
    },
    "check_consistency": {
        "description": "Check if the signal is consistent across nearby crops or tiles",
        "module": "scoring.context",
        "function": "check_consistency",
    },
    "score_hotspot": {
        "description": "Compute anomaly, severity, and confidence scores for a hotspot",
        "module": "scoring.ranker",
        "function": "compute_final_rank_score",
    },

    # Terminal actions
    "discard_hotspot": {
        "description": "Discard this hotspot when the evidence does not justify escalation",
        "module": None,
        "function": None,
    },
    "finalize_hotspot": {
        "description": "Finalize this hotspot for ranking and recommendation",
        "module": None,
        "function": None,
    },
}


def get_tool_descriptions_for_prompt() -> str:
    lines = []
    for name, meta in TOOL_REGISTRY.items():
        lines.append(f"- {name}: {meta['description']}")
    return "\n".join(lines)
