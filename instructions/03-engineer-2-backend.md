# Engineer 2
## Backend and Agent Orchestrator

Owner:

- FastAPI service
- schemas
- session management
- agent orchestrator (Gemini integration)
- chain of thought streaming
- tool routing and dispatch
- cache/playback bridge
- API endpoints
- region-level source retrieval and normalization
- fallback metadata enrichment path

## Immediate Goal

Expose the final-shaped API before the internals are real.

Your first win is not "AI works".

Your first win is:

- frontend can render the whole product from your API, including chain of thought

## First Hour

1. Create session-based endpoints:
   - `POST /session` — create session for a region, load data context
   - `POST /session/{session_id}/prompt` — accept user prompt, trigger investigation
   - `GET /session/{session_id}/chain-of-thought` — stream/poll chain of thought steps
   - `GET /session/{session_id}/messages` — conversation history
2. Create models for:
   - `Session`
   - `UserPrompt`
   - `ChainOfThoughtStep`
   - `InvestigationResponse`
   - `HotspotCandidate` (existing)
3. Return a fully mocked but contract-valid chain of thought for any prompt.
4. Wire Gemini for the agent loop:
   - accept user prompt + region data context
   - Gemini interprets the prompt and picks tools
   - dispatch tool calls to perception, thermal, scoring modules
   - record each step as a ChainOfThoughtStep
   - stream steps to frontend
   - produce final answer
5. Support session state for follow-up questions.
6. Keep legacy `/analysis` endpoints working.

## Agent Orchestrator Rules

The agent receives:

- user prompt
- region data context (thermal data, source records, metadata)
- conversation history (for follow-ups)

The agent:

- interprets the prompt
- decides what tools to call
- executes tools via the tool registry (`agent/tools.py`)
- records chain of thought
- produces a structured answer

Tool vocabulary:

- `inspect_object`
- `request_thermal_evidence`
- `infer_surface`
- `compare_neighbors`
- `check_consistency`
- `score_hotspot`
- `discard_hotspot`
- `finalize_hotspot`
- `list_hotspot_candidates`
- `get_region_summary`
- `lookup_location`

The investigation path is driven by the user's question, not by a fixed pipeline.

## Caching Rule

Cache is allowed, but the user must still experience a visible chain of thought.

That means:

- backend may serve cached investigation results
- frontend still reveals steps progressively
- chain of thought streaming must expose step progression cleanly

## Handoffs

From Engineer 3 you need:

- hotspot evidence payloads (tools return real data)

From Engineer 4 you need:

- scoring payloads or pure functions (tools return real scores)

To Engineer 1 you provide:

- stable API
- stable field names
- chain of thought streaming

## Success Condition

By hour 2, Engineer 1 should be using your real API and rendering chain of thought — even if tool internals are still mostly mocked.
