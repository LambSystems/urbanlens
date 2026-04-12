"""
Urban Legend — Agent Decision Loop

The prompt-driven investigation core. Receives the user's question,
the region data context, and conversation history, then runs a
Gemini-powered loop that:

  1. Interprets the user's prompt
  2. Decides what tool to call next
  3. Executes that tool (perception, thermal, scoring, etc.)
  4. Records the chain of thought step
  5. Decides if more evidence is needed
  6. Produces a final answer when investigation is complete

Every reasoning step and tool call is recorded as a ChainOfThoughtStep
and streamed to the frontend.
"""
from __future__ import annotations


async def investigate(
    prompt: str,
    region_context: dict,
    conversation_history: list[dict] | None = None,
) -> dict:
    """Run a prompt-driven investigation over the region data.

    Args:
        prompt: the user's question (e.g., "What should I fix first?")
        region_context: loaded data context for the region
            - thermal_data
            - source_records
            - hotspot_candidates
            - region metadata
        conversation_history: prior prompts + answers for follow-ups

    Returns:
        InvestigationResponse dict with:
            - chain_of_thought: list of ChainOfThoughtStep dicts
            - answer: the agent's final response text
            - hotspots: updated hotspot states
            - top_hotspots: ranked recommendations (if applicable)
    """
    # TODO: Implement Gemini-driven investigation loop
    #
    # Pseudocode:
    #   1. Build system prompt with region context and tool descriptions
    #   2. Send user prompt + conversation history to Gemini
    #   3. Parse Gemini's response — either a tool call or final answer
    #   4. If tool call:
    #      a. Dispatch to the appropriate module via tools.py registry
    #      b. Record the ChainOfThoughtStep
    #      c. Feed the tool result back to Gemini
    #      d. Loop
    #   5. If final answer:
    #      a. Record the answer step
    #      b. Return the full investigation response
    #
    # For now, the mocked orchestrator.py handles the legacy path.
    # This function will be wired once Gemini integration is ready.

    raise NotImplementedError("Wire Gemini agent loop here")
