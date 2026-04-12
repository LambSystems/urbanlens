"""
Urban Legend — Agent Decision Loop

The orchestrator's agentic core. For each hotspot candidate, the agent
decides what tool to call next until the hotspot is either discarded
or finalized.

Uses Gemini to reason over available evidence and pick the next action
from the fixed trace vocabulary:
  candidate_detected -> inspect_object -> [evidence tools] -> score -> discard/finalize

Replaces the mocked trace sequences in orchestrator.py once live.
"""
from __future__ import annotations

from ..schemas import HotspotCandidate, TraceStep


async def run_investigation(hotspot: HotspotCandidate, region_context: dict) -> list[TraceStep]:
    """Run the agentic investigation loop for a single hotspot.

    The agent iterates:
      1. Look at current evidence state
      2. Ask Gemini what tool to call next
      3. Execute that tool (perception, thermal, scoring, etc.)
      4. Record the trace step
      5. Repeat until a terminal action (discard/finalize)

    Returns the full trace of steps the agent chose.
    """
    # TODO: Implement Gemini-driven decision loop
    # For now, the mocked orchestrator.py handles this path
    raise NotImplementedError("Wire Gemini agent loop here")
