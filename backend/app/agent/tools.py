"""
Urban Legend — Agent Tool Registry

Defines the tools the orchestrator agent can invoke during investigation.
Each tool maps to one TraceKind from the shared contract and calls into
the appropriate backend module (perception, thermal, scoring, sources).

Fixed tool vocabulary:
  - inspect_object       -> perception.object_classifier
  - request_thermal_evidence -> thermal.evidence
  - infer_surface        -> perception.surface_inference
  - compare_neighbors    -> scoring.context
  - check_consistency    -> scoring.context
  - score_hotspot        -> scoring.ranker
  - discard_hotspot      -> terminal
  - finalize_hotspot     -> terminal
"""
from __future__ import annotations


TOOL_REGISTRY: dict[str, dict] = {
    "inspect_object": {
        "description": "Identify the object type at this hotspot (roof, road, hvac, etc.)",
        "module": "perception.object_classifier",
    },
    "request_thermal_evidence": {
        "description": "Retrieve thermal intensity and heat pattern for this hotspot",
        "module": "thermal.evidence",
    },
    "infer_surface": {
        "description": "Estimate the surface material (dark roof, asphalt, metal, etc.)",
        "module": "perception.surface_inference",
    },
    "compare_neighbors": {
        "description": "Compare this hotspot against nearby similar structures",
        "module": "scoring.context",
    },
    "check_consistency": {
        "description": "Check if the signal is consistent across nearby crops/tiles",
        "module": "scoring.context",
    },
    "score_hotspot": {
        "description": "Compute anomaly, severity, and confidence scores",
        "module": "scoring.ranker",
    },
    "discard_hotspot": {
        "description": "Discard this hotspot — evidence does not justify escalation",
        "module": None,
    },
    "finalize_hotspot": {
        "description": "Finalize this hotspot for ranking and recommendation",
        "module": None,
    },
}


def get_tool_descriptions_for_prompt() -> str:
    """Format tool registry as text for inclusion in Gemini system prompt."""
    lines = []
    for name, meta in TOOL_REGISTRY.items():
        lines.append(f"- {name}: {meta['description']}")
    return "\n".join(lines)
