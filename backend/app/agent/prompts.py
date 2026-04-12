"""
Urban Legend — Agent System Prompts

System prompts and tool descriptions sent to Gemini for the
prompt-driven investigation loop.

The agent receives the user's question, the region data context,
and conversation history, then decides what tools to call to
investigate and answer.
"""

from .tools import get_tool_descriptions_for_prompt

SYSTEM_PROMPT = """\
You are Urban Legend, an urban heat investigation agent.

You help users understand and act on urban heat data. When a user asks
a question about a geographic region, you investigate by calling tools
to gather evidence, then return an actionable answer.

## Your data context

You have access to a region's data including:
- Satellite imagery with thermal overlay
- Scattered drone source imagery and metadata
- Hotspot candidates detected in the region
- Source coverage and quality metrics

## Your tools

{tools}

## How to investigate

1. Read the user's question and understand what they want to know.
2. Decide what evidence you need to answer their question.
3. Call the appropriate tools to gather that evidence.
4. Reason over what you found. Decide if you need more evidence.
5. When you have enough evidence, produce your answer.

## Rules

- Always start by interpreting what the user is asking.
- Only call tools that help answer the question — do not call tools just because they exist.
- When scoring hotspots: anomaly gates, severity orders, confidence modulates.
- Discard hotspots that fail the anomaly gate or have insufficient evidence.
- When recommending actions, cite the specific evidence from your investigation.
- If source coverage is partial, acknowledge uncertainty in your confidence.
- Be concise. Each tool call should be motivated by missing evidence.
- For follow-up questions, build on your prior investigation — do not restart from scratch.

## Answer format

End your investigation with a clear, direct answer to the user's question.
Include specific evidence, scores, and recommendations where relevant.
""".format(tools=get_tool_descriptions_for_prompt())


def build_investigation_prompt(
    user_prompt: str,
    region_context: dict,
    conversation_history: list[dict] | None = None,
) -> list[dict]:
    """Build the message list for a Gemini investigation call.

    Returns a list of message dicts ready for the Gemini API.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    # Add region context as a system message
    context_summary = _format_region_context(region_context)
    messages.append({
        "role": "system",
        "content": f"## Current region data\n\n{context_summary}",
    })

    # Add conversation history for follow-ups
    if conversation_history:
        for msg in conversation_history:
            messages.append(msg)

    # Add the user's current prompt
    messages.append({
        "role": "user",
        "content": user_prompt,
    })

    return messages


def _format_region_context(region_context: dict) -> str:
    """Format region data context as readable text for the agent."""
    parts = []

    if "center" in region_context:
        c = region_context["center"]
        parts.append(f"Region center: ({c.get('lat', '?')}, {c.get('lng', '?')})")

    if "coverage_score" in region_context:
        parts.append(f"Coverage score: {region_context['coverage_score']}")

    if "source_count" in region_context:
        parts.append(f"Available sources: {region_context['source_count']}")

    if "thermal_data" in region_context:
        td = region_context["thermal_data"]
        parts.append(f"Thermal range: {td.get('min_temp_c', '?')}°C to {td.get('max_temp_c', '?')}°C")
        parts.append(f"Mean temp: {td.get('mean_temp_c', '?')}°C")
        hotspot_count = len(td.get("hotspot_regions", []))
        parts.append(f"Detected thermal hotspot regions: {hotspot_count}")

    if "candidates" in region_context:
        parts.append(f"Hotspot candidates: {len(region_context['candidates'])}")

    return "\n".join(parts) if parts else "No region context loaded."
