"""
Urban Legend — Agent Tool Registry

Defines the tools the agent can invoke during prompt-driven investigation.
Each tool maps to a backend module and is called when the agent (Gemini)
decides it needs that evidence to answer the user's question.

The tool set is intentionally constrained so the chain of thought stays
legible in the UI.
"""
from __future__ import annotations


TOOL_REGISTRY: dict[str, dict] = {
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
        "description": "Check if the signal is consistent across nearby crops/tiles",
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
        "description": "Discard this hotspot — evidence does not justify escalation",
        "module": None,
        "function": None,
    },
    "finalize_hotspot": {
        "description": "Finalize this hotspot for ranking and recommendation",
        "module": None,
        "function": None,
    },

    # Region-level tools
    "get_region_summary": {
        "description": "Get an overview of the region: source count, coverage, thermal stats",
        "module": "sources.retrieval",
        "function": "compute_coverage_score",
    },
    "lookup_location": {
        "description": "Look up location metadata for a coordinate (reverse geocoding)",
        "module": "sources.enrichment",
        "function": "enrich_source_metadata",
    },
}


def get_tool_descriptions_for_prompt() -> str:
    """Format tool registry as text for inclusion in Gemini system prompt."""
    lines = []
    for name, meta in TOOL_REGISTRY.items():
        lines.append(f"- {name}: {meta['description']}")
    return "\n".join(lines)


def get_gemini_function_declarations() -> list[dict]:
    """Format tool registry as Gemini function declarations.

    TODO: Build proper Gemini function calling schema for each tool.
    """
    declarations = []
    for name, meta in TOOL_REGISTRY.items():
        declarations.append({
            "name": name,
            "description": meta["description"],
            "parameters": {
                "type": "object",
                "properties": {},
            },
        })
    return declarations
