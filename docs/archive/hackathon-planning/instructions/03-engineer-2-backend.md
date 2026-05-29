# Engineer 2
## Backend, Capture Ingestion, and Agent Orchestrator

Owner:

- FastAPI service
- schemas
- capture ingestion endpoints
- capture storage
- analysis resource endpoints
- agent orchestrator
- tool routing and dispatch
- `LLMProvider` abstraction
- cache/playback bridge
- optional voice briefing endpoint

## Immediate Goal

Make the backend ready for the new capture-based approach without breaking the existing analysis API.

Your win is:

- frontend can send a locality capture
- backend creates an analysis
- the agent can visibly call tools against that capture

## Canonical Priorities

1. Keep `analysis` as the main resource.
2. Support both:
   - `POST /analysis/from-capture`
   - `POST /analysis/from-capture-upload`
3. Store uploaded image plus metadata under `backend/data/captures/{region_id}`.
4. Route the new capture flow into the existing analysis output shape.
5. Keep planner questions as:
   - `POST /analysis/{region_id}/questions`

## Orchestrator Rules

The orchestrator receives:

- user question or default analysis intent
- capture metadata
- stored image path
- prior analysis state

The orchestrator decides whether to call:

- `ThermalGen`
- `Heat Risk Profiler`
- perception helpers
- scoring and ranking tools

The path may vary by question, but the output shape must stay stable.

## LLM Rule

Do not hard-bind the product to Gemini.

Use `LLMProvider` with:

- `AnthropicProvider` as default for reliability
- `GeminiProvider` as optional
- `FeatherlessProvider` as optional and prize-relevant
- `MockProvider` for fallback/testing

Use the LLM mainly for:

- tool-selection reasoning
- explanation wording
- follow-up questions

Keep ranking math deterministic.

## Voice Rule

If time allows, add a backend endpoint for ElevenLabs-generated voice briefings.

Recommended shape:

- `POST /analysis/{region_id}/voice-briefing`

This endpoint should:

- read the final grounded answer
- generate short audio
- return a file URL or bytes response

It must remain optional and downstream of the main analysis flow.

## Required Endpoints

- `POST /analysis`
- `POST /analysis/from-capture`
- `POST /analysis/from-capture-upload`
- `GET /analysis/{region_id}`
- `GET /analysis/{region_id}/events`
- `GET /analysis/{region_id}/hotspots/{hotspot_id}`
- `GET /analysis/{region_id}/debug`
- `POST /analysis/{region_id}/questions`

## Success Condition

The rest of the team can build on a stable analysis contract while you swap internals from stubs to real tools.
