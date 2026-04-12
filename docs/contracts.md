# UrbanLens Contracts
## Capture-Based Analysis, Tooling, and Output Contracts

This document is the implementation source of truth for the new pivot.

It defines:

- what the frontend sends
- what the backend stores
- what the agent is allowed to call
- how output stays stable even as internal tools evolve

The key contract rule is:

> different investigation paths are allowed, but they must converge to the same stable analysis output shape

---

## 1. Product Contract

The product is an `analysis` of a selected locality.

Users may:

- create an analysis from a map capture
- inspect results
- ask follow-up questions over that analysis

The API is analysis-first, not chat-first.

---

## 2. Input Contract

## 2.1 Preferred Input

Preferred frontend submission:

- `multipart/form-data`

Fields:

- `metadata`
- `image`

`metadata` is a JSON string.
`image` is the screenshot or crop file.

## 2.2 Fallback Input

Fallback submission:

- JSON payload with `imageBase64`

This is allowed for compatibility, but multipart is the preferred production-demo path.

---

## 3. Capture Metadata Contract

Recommended metadata shape:

```json
{
  "region": {
    "bounds": {
      "north": 42.28145703795954,
      "south": 42.28057862649839,
      "east": -83.74731891703615,
      "west": -83.74839984726916
    },
    "center": {
      "lat": 42.28101783222897,
      "lng": -83.74785938215265
    },
    "areaKm2": 0.008655410213870432
  },
  "map": {
    "zoom": 19,
    "mapTypeId": "hybrid",
    "tilt": 45,
    "heading": null
  },
  "viewport": {
    "north": 42.282105314602525,
    "south": 42.28025027146603,
    "east": -83.74623262238511,
    "west": -83.75036322426804
  }
}
```

Required ideas:

- region bounds
- region center
- area
- map state
- viewport

---

## 4. Capture Storage Contract

Every created analysis should be reproducible from stored capture assets.

Recommended local storage:

- `backend/data/captures/{region_id}/metadata.json`
- `backend/data/captures/{region_id}/source.png`
- optional `thermal.png`

This is enough for:

- replay
- debugging
- review and debugging

---

## 5. Tool Contract

The agent may call a constrained internal tool set.

Recommended MVP tool vocabulary:

- `generate_thermal_overlay`
- `request_thermal_evidence`
- `analyze_heat_risk`
- `inspect_object`
- `infer_surface`
- `compare_findings`
- `score_hotspots`
- `discard_hotspot`
- `finalize_recommendation`

Rules:

- `ThermalGen` is represented through the thermal tool(s)
- `Heat Risk Profiler` is represented through `analyze_heat_risk`
- tools are internal backend operations, not arbitrary web actions
- the trace may vary by question, but tool names stay stable

---

## 6. Trace Contract

The trace should feel agentic but stay easy for the frontend to render.

### 6.1 Step Types

- `reasoning`
- `tool_call`
- `finding`
- `answer`

### 6.2 Step Fields

Minimum useful step shape:

```json
{
  "step_id": "step_01",
  "analysis_id": "region_123",
  "status": "completed",
  "step_type": "tool_call",
  "tool_name": "request_thermal_evidence",
  "summary": "Thermal evidence generated for the selected roof cluster",
  "details": {
    "tool_family": "thermal",
    "coverage_score": 0.88
  },
  "timestamp_ms": 1712940001000
}
```

Rules:

- steps are visible in order
- steps can be replayed progressively
- the final step for a prompt should be an `answer`

---

## 7. Output Contract

All investigations should converge to the same output family.

## 7.1 Analysis Summary

```json
{
  "region_id": "region_123",
  "status": "completed",
  "top_hotspot_id": "hs_01",
  "discarded_hotspot_ids": ["hs_02"],
  "summary": {
    "candidate_count": 4,
    "discarded_count": 1,
    "finalized_count": 3
  }
}
```

## 7.2 Hotspot Candidate

```json
{
  "hotspot_id": "hs_01",
  "display_name": "Central Roof Cluster",
  "hotspot_type": "roof",
  "status": "finalized",
  "anomaly_score": 0.82,
  "severity_score": 0.79,
  "confidence_score": 0.88,
  "final_rank_score": 0.6952,
  "recommended_action": "Inspect for cool-roof retrofit opportunity",
  "why": [
    "thermal evidence elevated",
    "large exposed roof area",
    "heat-risk profile agrees with low shade and dark surface cues"
  ]
}
```

## 7.3 Planner Answer

```json
{
  "region_id": "region_123",
  "question": "Why did you choose that roof first?",
  "answer": "It ranked first because both ThermalGen and the heat-risk profile indicated elevated concern, and the roof remained high-confidence after scoring.",
  "referenced_hotspot_ids": ["hs_01"],
  "planner_mode": "analysis_qa"
}
```

---

## 8. Ranking Contract

Keep the ranking contract stable:

- anomaly gates
- severity orders
- confidence modulates

Gate:

```text
if anomaly_score < anomaly_threshold:
    discard
```

Ranking:

```text
final_rank_score = severity_score * confidence_score
```

Confidence may reflect:

- model confidence
- agreement between tools
- evidence completeness
- capture quality

---

## 9. API Contract

Canonical endpoints:

- `POST /analysis`
- `POST /analysis/from-capture`
- `POST /analysis/from-capture-upload`
- `GET /analysis/{region_id}`
- `GET /analysis/{region_id}/hotspots/{hotspot_id}`
- `GET /analysis/{region_id}/events`
- `GET /analysis/{region_id}/debug`
- `POST /analysis/{region_id}/questions`

Rules:

- old endpoints stay resource-oriented
- capture endpoints create normal analyses
- follow-up questions always attach to an existing analysis

---

## 10. LLM Provider Contract

The orchestrator must not be hard-bound to one provider.

Required abstraction:

- `AnthropicProvider`
- `GeminiProvider`
- `FeatherlessProvider`
- `MockProvider`

Provider choice should be environment-configurable.

Recommended env:

- `LLM_PROVIDER=anthropic`

Recommended additional env values:

- `LLM_PROVIDER=featherless`
- `LLM_PROVIDER=gemini`

Featherless must implement the same contract as the other providers.
No branch-specific orchestration logic is allowed just for Featherless.

## 10.1 Voice Briefing Contract

Voice output is optional and separate from the LLM provider layer.

Recommended endpoint shape:

- `POST /analysis/{region_id}/voice-briefing`

Recommended response:

```json
{
  "region_id": "region_123",
  "audio_url": "/data/captures/region_123/briefing.mp3",
  "summary_text": "The central roof cluster is the top inspection target..."
}
```

Rules:

- generated only after an analysis exists
- uses the final grounded answer as input
- must not invent new evidence
- may be disabled without affecting the core product

---

## 11. UI Boundary Contract

The frontend may assume:

- map is the visual anchor
- analyses are the main backend resource
- traces are progressive and ordered
- planner questions are secondary to analysis creation

The frontend should not assume:

- a chat-session-first API
- arbitrary freeform tool names
- provider-specific LLM behavior

---

## 12. Final Rule

If implementation details drift, preserve these first:

- selected locality capture
- stable analysis output shape
- visible tool-calling trace
- `ThermalGen` as the standout tool
- one supporting analysis tool
- grounded final answer

That is the contract that keeps the pivot coherent.
