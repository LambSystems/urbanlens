# Shared Contract

Source of truth is [contracts.md](../docs/contracts.md).

Everyone should follow these exact decisions.

## Core Flow

- map click defines an `analysis region`
- system loads data context: satellite imagery, thermal overlay, source records, metadata
- user types a prompt (question or intent)
- agent interprets the prompt and decides what tools to call
- agent investigates with visible chain of thought
- agent returns a structured answer with evidence and recommendations
- user can ask follow-up questions in the same session

## Conversation Model

- `session_id` persists across a region + conversation
- each prompt is a new message in the session
- the agent sees full conversation history for follow-ups
- the region data context is loaded once and reused

## Hotspot Taxonomy

- `roof`
- `road_pavement`
- `parking_lot`
- `hvac_mechanical`
- `vegetation_loss`
- `other`

## Chain of Thought Step Types

- `reasoning` — agent's internal reasoning (text)
- `tool_call` — agent invoked a tool (name + summary)
- `finding` — agent concluded something about a specific item
- `answer` — agent's final response

## Tool Vocabulary

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

## Chain of Thought Rules

- every investigation starts with the agent interpreting the user's prompt
- tool calls must be motivated by the question
- each step has a visible summary
- the chain of thought ends with a structured answer
- streamed to the frontend step by step

## Ranking Heuristic

- anomaly filters
- severity orders
- confidence modulates

Confidence should also reflect source coverage quality.

Gate:

```text
if anomaly_score < anomaly_threshold:
    discard
```

Ranking:

```text
final_rank_score = severity_score * confidence_score
```

## Caching

- cache is allowed
- visible reasoning must remain
- frontend should play back cached chain of thought progressively
- region caches may include pre-resolved drone source sets for known demo regions

## API Surface

- `POST /session`
- `POST /session/{session_id}/prompt`
- `GET /session/{session_id}/chain-of-thought`
- `GET /session/{session_id}/messages`
- `GET /session/{session_id}/hotspots/{hotspot_id}`

Legacy (still supported):

- `POST /analysis`
- `GET /analysis/{region_id}`
- `GET /analysis/{region_id}/hotspots/{hotspot_id}`
- `GET /analysis/{region_id}/events`

## UI Rule

The map is the anchor.

`v0` may be used for:

- sidebar shell
- prompt input
- chain of thought timeline
- ranking cards
- recommendation card
- conversation thread

`v0` may not redefine:

- schemas
- backend logic
- scoring
- chain of thought semantics
- map interaction contract
