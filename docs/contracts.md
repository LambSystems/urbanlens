# Urban Legend Contracts
## Prompt-Driven Investigation, Chain of Thought, and Backend/Frontend Schema

This document defines the operating contract for the MVP so all engineers can work in parallel without drift.

It is the source of truth for:

- analysis region behavior
- source retrieval and evidence normalization behavior
- source record requirements and fallback enrichment
- user prompt and conversation model
- chain of thought design
- hotspot taxonomy
- tool vocabulary
- ranking and discard heuristics
- caching behavior
- backend/frontend data contracts
- the UI boundaries where `v0` can be used safely

---

## 1. Analysis Region

The user does not analyze a single structure directly.

A click on the map defines an `analysis region` centered around that click. The system loads the data context for that region, then the user asks a question about it.

Google Maps is the interaction surface. The evidence layer underneath may consist of scattered drone imagery, thermal conversions, and partial metadata.

Required behavior:

- click on map
- derive region center and radius
- load data context: satellite imagery, thermal overlay, source records, metadata
- present loaded context to the user
- accept user prompt (question or intent)
- pass prompt + data context to the agent
- stream chain of thought steps to the frontend
- return structured answer with evidence and recommendations
- support follow-up questions in the same session

Recommended MVP fields:

- `center.lat`
- `center.lng`
- `radius_m`
- `region_id`
- `session_id`
- `available_source_count`
- `coverage_score`

## 1.1 Source Retrieval Model

The backend should assume source imagery is scattered.

That means:

- not every region will have perfect coverage
- source imagery may come from multiple files or partial crops
- confidence should reflect coverage quality

For the MVP, source retrieval can be implemented as a curated mapping for known demo regions, but the contract should already model:

- source count
- coverage quality
- whether evidence is partial

## 1.2 Source Record Contract

Every raw source should be able to enter the system even if metadata is incomplete.

Recommended minimum source contract:

- `source_id`
- `source_type`
  one of `drone`, `satellite`, `derived`
- `image_path` or `image_url`
- `lat` optional
- `lng` optional
- `bounds` optional
- `timestamp` optional
- `altitude` optional
- `heading` optional
- `resolution` optional
- `metadata_quality_score`
- `geolocation_confidence`

Rule:

- missing metadata should reduce confidence, not break the pipeline

## 1.3 Google Maps Enrichment Fallback

Google Maps may be used to enrich missing or weak metadata when the source record is incomplete.

Allowed fallback uses:

- reverse geocoding
- viewport and bounds support
- approximate place or area labeling
- contextual metadata enrichment

Not allowed:

- treating Google Maps as primary thermal evidence
- replacing missing drone evidence with fake hotspot truth

Fallback order:

1. source record metadata
2. dataset-level metadata
3. Google Maps enrichment
4. confidence penalty if uncertainty remains

---

## 2. User Prompt and Conversation Model

The user drives the investigation by typing prompts.

### 2.1 Prompt Contract

The user's prompt is a free-text question or instruction about the loaded region data.

Examples:

- "What should I fix first in this area?"
- "Are there any HVAC issues on these rooftops?"
- "Why is the northeast corner so hot?"
- "Compare the roofs in this region"
- "How confident are you about that roof?" (follow-up)

### 2.2 Session Contract

A session represents one region plus a conversation.

- `session_id` persists across follow-up questions
- each prompt is a new message in the session
- the agent sees the full conversation history for context
- the region data context is loaded once and reused across the session

### 2.3 Conversation Rules

- the first prompt in a session starts a fresh investigation
- follow-up prompts build on previous findings
- the agent can reference prior chain of thought when answering follow-ups
- the frontend shows the full conversation thread

---

## 3. Hotspot Taxonomy

The MVP uses a small, explicit taxonomy:

- `roof`
- `road_pavement`
- `parking_lot`
- `hvac_mechanical`
- `vegetation_loss`
- `other`

Rules:

- use the most specific known label
- use `other` only as a fallback
- UI and ranking logic must not depend on a larger taxonomy

---

## 4. Chain of Thought Design

The chain of thought must feel agentic without becoming unpredictable.

Every investigation produces a visible chain of thought — a sequence of reasoning steps and tool calls that the frontend renders in real time.

### 4.1 Chain of Thought Step Types

- `reasoning` — the agent's internal reasoning (text)
- `tool_call` — the agent invoked a tool (tool name + input summary + output summary)
- `finding` — the agent arrived at a conclusion about a specific item
- `answer` — the agent's final response to the user's prompt

### 4.2 Tool Vocabulary

Available tools the agent can call during investigation:

- `inspect_object`
- `request_thermal_evidence`
- `infer_surface`
- `compare_neighbors`
- `check_consistency`
- `score_hotspot`
- `discard_hotspot`
- `finalize_hotspot`

Additional tools available depending on the question:

- `list_hotspot_candidates` — enumerate candidates in the region
- `get_region_summary` — overview stats for the region
- `lookup_location` — query location metadata

### 4.3 Chain of Thought Rules

- every investigation starts with the agent interpreting the user's prompt
- tool calls must be motivated by the question — not called just because they exist
- each step has a visible summary the frontend can display
- the chain of thought ends with a structured answer
- chain of thought is streamed to the frontend step by step

### 4.4 Example Chain of Thought

User prompt: "What should I fix first in this area?"

```
1. [reasoning] User wants prioritized intervention recommendations. I need to identify and score all hotspot candidates.
2. [tool_call] list_hotspot_candidates -> found 4 candidates
3. [tool_call] inspect_object(hs_01) -> roof structure
4. [tool_call] request_thermal_evidence(hs_01) -> intensity 0.87, well above regional mean
5. [tool_call] compare_neighbors(hs_01) -> hotter than 83% of nearby comparable roofs
6. [finding] hs_01: significant roof anomaly, strong intervention candidate
7. [tool_call] inspect_object(hs_02) -> road pavement
8. [tool_call] request_thermal_evidence(hs_02) -> intensity 0.52, consistent with nearby roads
9. [tool_call] discard_hotspot(hs_02) -> expected road heat profile, not anomalous
10. [tool_call] score_hotspot(hs_01) -> anomaly: 0.82, severity: 0.76, confidence: 0.71
11. [tool_call] finalize_hotspot(hs_01) -> passed anomaly gate
12. [answer] The commercial roof at the northeast corner is the highest-priority intervention...
```

---

## 5. Discarded vs Top Hotspot

These terms must be implemented consistently across backend, scoring, and UI.

### 5.1 Discarded Hotspot

A discarded hotspot is a candidate that is not worth acting on.

It usually fails because:

- anomaly is too low relative to local context
- the heat pattern is expected for the object type
- evidence is insufficient to justify escalation
- confidence is too low to recommend action
- source coverage is too incomplete to support escalation

Discard labels must be evidence-backed, not decorative.

### 5.2 Top Hotspot

A top hotspot is a candidate that:

- passes the anomaly gate
- remains severe enough to matter
- retains enough confidence to support a recommendation
- is backed by adequate enough source coverage for the recommendation strength

Top hotspots appear in the final answer and receive an intervention recommendation.

---

## 6. Ranking Heuristic

The ranking philosophy is:

`anomaly filters`

`severity orders`

`confidence modulates and validates`

### 6.1 Gate

First apply an anomaly threshold:

```text
if anomaly_score < anomaly_threshold:
    discard
```

This is the structural filter.

### 6.2 Ranking

For survivors, rank primarily by severity with confidence modulation:

```text
final_rank_score = severity_score * confidence_score
```

Confidence should combine:

- model or reasoning confidence
- context consistency
- source coverage quality
- metadata completeness and geolocation confidence

### 6.3 Notes

- anomaly is still stored and shown in UI
- anomaly is still part of explanation
- severity is the primary ordering signal after gating

---

## 7. Caching Model

The system should feel alive even when using cached or precomputed evidence.

Caching exists to improve stability and speed, not to remove the investigation experience.

### 7.1 Region Cache

Stores:

- nearby repeated analysis regions
- region metadata
- source retrieval results

Use case:

- repeated clicks near the same area

### 7.2 Investigation Cache

Stores per prompt:

- chain of thought steps
- tool call results
- final answer

Use case:

- replaying a known demo prompt quickly and reliably

### 7.3 Chain of Thought Playback

Even when the investigation is cached, the frontend should reveal chain of thought steps progressively.

This preserves:

- perceived reasoning
- demo clarity
- visible agent behavior

Recommended behavior:

- each step transitions through `pending -> running -> completed`
- total playback adjusts based on number of steps

---

## 8. State Model

Recommended session states:

- `region_loaded` — data context loaded, waiting for user prompt
- `investigating` — agent is running chain of thought
- `answered` — agent has returned a response
- `follow_up` — user is asking a follow-up question

Recommended hotspot states:

- `candidate`
- `investigating`
- `evidence_gathered`
- `discarded`
- `finalized`

Rules:

- `discarded` is terminal
- `finalized` is terminal
- a hotspot cannot be both discarded and finalized

---

## 9. Backend/Frontend Schema

These schemas are intentionally compact and stable.

### 9.1 AnalysisRegion

```json
{
  "region_id": "stl_001",
  "session_id": "sess_abc123",
  "center": {"lat": 38.6270, "lng": -90.1994},
  "radius_m": 120,
  "available_source_count": 6,
  "coverage_score": 0.81,
  "status": "region_loaded"
}
```

### 9.1.1 SourceRecord

```json
{
  "source_id": "drone_img_001",
  "source_type": "drone",
  "image_path": "data/demo/drone_img_001.png",
  "lat": 38.6271,
  "lng": -90.1992,
  "bounds": null,
  "timestamp": null,
  "altitude": 110.0,
  "heading": null,
  "resolution": 0.12,
  "metadata_quality_score": 0.72,
  "geolocation_confidence": 0.68
}
```

### 9.2 UserPrompt

```json
{
  "session_id": "sess_abc123",
  "prompt": "What should I fix first in this area?",
  "message_index": 0
}
```

### 9.3 ChainOfThoughtStep

```json
{
  "step_id": "cot_03",
  "step_type": "tool_call",
  "tool_name": "compare_neighbors",
  "status": "completed",
  "summary": "Hotter than 83% of nearby comparable roofs",
  "evidence": {
    "neighbor_count": 12,
    "relative_percentile": 0.83,
    "coverage_score": 0.79
  },
  "timestamp": "2026-04-11T18:10:14Z"
}
```

### 9.4 HotspotCandidate

```json
{
  "hotspot_id": "hs_01",
  "region_id": "stl_001",
  "bbox": {"x": 120, "y": 80, "w": 60, "h": 44},
  "centroid": {"lat": 38.6271, "lng": -90.1991},
  "hotspot_type": "roof",
  "status": "finalized",
  "source_count": 3,
  "coverage_score": 0.79,
  "anomaly_score": 0.82,
  "severity_score": 0.76,
  "confidence_score": 0.71,
  "final_rank_score": 0.5396,
  "recommended_action": "cool-roof retrofit",
  "why": [
    "high relative anomaly vs nearby roofs",
    "large exposed dark surface",
    "high-confidence thermal evidence"
  ]
}
```

### 9.5 InvestigationResponse

```json
{
  "session_id": "sess_abc123",
  "region_id": "stl_001",
  "prompt": "What should I fix first in this area?",
  "chain_of_thought": [
    {
      "step_id": "cot_01",
      "step_type": "reasoning",
      "summary": "User wants prioritized intervention recommendations. I need to identify and score all hotspot candidates."
    },
    {
      "step_id": "cot_02",
      "step_type": "tool_call",
      "tool_name": "list_hotspot_candidates",
      "summary": "Found 4 candidates in the region"
    }
  ],
  "answer": "The commercial roof at the northeast corner is the highest-priority intervention. It shows unusually high heat relative to nearby roofs, with a dark roofing surface that is a strong candidate for cool-roof retrofit.",
  "hotspots": [],
  "top_hotspots": [
    {
      "hotspot_id": "hs_01",
      "priority_rank": 1,
      "hotspot_type": "roof",
      "recommended_action": "cool-roof retrofit",
      "why": [
        "high relative anomaly vs nearby roofs",
        "large exposed dark surface",
        "high-confidence thermal evidence"
      ]
    }
  ]
}
```

---

## 10. API Surface

Keep the backend surface small.

Recommended endpoints:

- `POST /session`
  create a session for a selected region, load data context
- `POST /session/{session_id}/prompt`
  send a user prompt, triggers agent investigation
- `GET /session/{session_id}/chain-of-thought`
  stream or poll chain of thought steps during investigation
- `GET /session/{session_id}/messages`
  fetch conversation history (prompts + answers)
- `GET /session/{session_id}/hotspots/{hotspot_id}`
  fetch hotspot details

Legacy endpoints (still supported for direct analysis):

- `POST /analysis`
- `GET /analysis/{region_id}`
- `GET /analysis/{region_id}/hotspots/{hotspot_id}`
- `GET /analysis/{region_id}/events`

---

## 11. v0 Implementation Boundary

`v0` should be used to accelerate visual implementation, not to define application logic.

Safe `v0` scope:

- sidebar shell
- prompt input component
- chain of thought timeline panel
- hotspot detail panel
- ranking cards
- recommendation card
- loading and empty states
- conversation thread display

Not `v0` scope:

- backend orchestration logic
- agent prompts or tool definitions
- hotspot scoring rules
- chain of thought semantics
- map event handling contract
- caching logic

Implementation approach:

1. Define schema and UI state contracts first in this document.
2. Use `v0` prompts to generate UI components against those fixed contracts.
3. Adapt the generated React/TypeScript output into the app without renaming schema fields to fit the UI.
4. Prefer `v0` for component structure, styling, and layout polish.
5. Keep the Google Maps container and analysis state management under direct engineer control.

Suggested `v0` prompt targets:

- a right sidebar with prompt input and chain of thought timeline
- chain of thought steps with reasoning, tool call, finding, and answer states
- ranked hotspot cards with anomaly, severity, and confidence badges
- a recommendation card for the top hotspot with action, rationale, and confidence
- conversation thread showing prompt history and agent responses

Success criteria for `v0` usage:

- the UI is visibly cleaner and more legible than a hand-built default dashboard
- the map remains the visual anchor
- the chain of thought and answers are understandable in under 10 seconds
- generated components integrate cleanly with React and TypeScript

---

## 12. Implementation Rule

If anything is ambiguous during implementation, preserve these first:

- user prompt drives the investigation
- chain of thought is fully visible in the UI
- the agent decides what tools to call based on the question
- follow-up questions work within the same session
- anomaly as gate, severity for ordering, confidence for modulation
- visible reasoning over cached evidence
- source coverage affects confidence

That is the contract that keeps the product coherent.
