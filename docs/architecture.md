# ThermalGen V2 Architecture
## Winning-Slice Architecture for Best in Agentic AI

This architecture is optimized for a hackathon-winning vertical slice, not a fully generalized platform.

The objective is to support one clear end-to-end behavior:

`select region -> detect hotspots -> investigate -> discard -> prioritize -> recommend`

---

## 1. Architecture Principle

ThermalGen should be built as a layered decision system.

- deterministic components handle ingestion, normalization, routing, and scoring
- narrow models produce partial evidence
- an orchestrator decides how to investigate each hotspot
- a planner turns validated evidence into ranked actions

This keeps the system:

- debuggable
- demoable
- stable under time pressure
- legible to judges

---

## 2. Scope Philosophy

We are not trying to prove the maximum technical surface area.

We are trying to prove the clearest agentic loop.

That means:

- one strong demo region over many weak regions
- a constrained tool set over a broad action space
- visible orchestration over hidden complexity
- evidence-seeking behavior over static pipelines

---

## 3. High-Level System

```text
User selects demo region
        |
        v
Map-first frontend
        |
        v
API/session layer
        |
        v
Thermal evidence + metadata ingestion
        |
        v
Candidate discovery
        |
        v
Agent orchestrator
   |        |        |
   v        v        v
Perception  Context  Scoring
   \        |       /
    \       |      /
     v      v     v
   Evidence aggregation
        |
        v
Intervention planner
        |
        v
Ranking + recommendation UI
```

---

## 4. Main Layers

### 4.1 Frontend

The frontend is primarily a legibility layer.

It must show:

- RGB plus thermal context
- hotspot candidates
- one selected hotspot investigation trace
- discarded hotspot state
- Top 3 ranking
- final recommendation

The frontend should optimize for fast judge comprehension, not feature breadth.

### 4.2 API and Session Layer

This layer should stay thin.

Responsibilities:

- accept region analysis request
- define an analysis region around a map click
- load cached or live evidence
- coordinate orchestrator lifecycle
- return structured data for the UI

This layer should not contain complex reasoning logic.

### 4.3 Thermal Evidence Layer

This is a prebuilt advantage and should be treated as stable infrastructure plus an evidence tool.

Responsibilities:

- provide aligned thermal evidence for the region
- expose thermal-derived cues for hotspot proposal
- return hotspot-specific heat evidence when the orchestrator requests it

The thermal module is not the product. It is evidence the agent can choose to consult.

### 4.4 Candidate Discovery

This layer proposes 3 to 5 initial hotspots inside an analysis region around the user click.

Possible techniques:

- thresholding
- clustering
- contour extraction
- lightweight hotspot scoring

Its job is to generate candidates, not final conclusions.

### 4.5 Perception Layer

This layer answers:

- what object is this hotspot attached to
- what coarse surface or material might it be

Outputs should be structured and simple enough for scoring and explanation.

Supported hotspot taxonomy for the MVP:

- `roof`
- `road_pavement`
- `parking_lot`
- `hvac_mechanical`
- `vegetation_loss`
- `other`

### 4.6 Context Layer

This layer answers:

- is this hotspot unusually hot relative to nearby structures
- is it expected in local context
- is this signal consistent across nearby crops or tiles

This is where the project gains credibility as a triage system rather than a detector.

### 4.7 Scoring Layer

This layer computes:

- severity
- anomaly
- confidence

For the hackathon, this should favor explainable heuristics over fragile complexity.

Scoring hierarchy:

- `anomaly` is the structural gate
- `severity` orders surviving hotspots
- `confidence` modulates whether the result should be trusted and how strongly it should be presented

### 4.8 Agent Orchestrator

This is the core of the product.

The orchestrator should decide:

- which hotspot to inspect next
- which worker to call
- whether thermal evidence is needed yet
- whether context comparison is needed yet
- whether evidence is sufficient
- whether to discard or escalate
- when to finalize

Recommended tool/action space:

- `inspect_object`
- `request_thermal_evidence`
- `infer_surface`
- `compare_neighbors`
- `check_consistency`
- `score_hotspot`
- `discard_hotspot`
- `finalize_hotspot`

Keep the action space constrained enough that the UI trace stays understandable.

The trace vocabulary is fixed, but the route is not. Different hotspot types can take different valid paths through the same state machine.

Example routes:

- `road_pavement`
  `candidate_detected -> inspect_object -> request_thermal_evidence -> compare_neighbors -> score_hotspot -> discard_hotspot`
- `roof`
  `candidate_detected -> inspect_object -> request_thermal_evidence -> infer_surface -> compare_neighbors -> check_consistency -> score_hotspot -> finalize_hotspot`
- `hvac_mechanical`
  `candidate_detected -> inspect_object -> request_thermal_evidence -> infer_surface -> score_hotspot -> finalize_hotspot`

### 4.9 Planner

The planner turns validated hotspot evidence into:

- ranked priority
- recommended action
- concise rationale

This is the business-value layer.

Without it, the system only observes. With it, the system recommends.

---

## 5. Required Demo Behaviors

The architecture must support these behaviors explicitly:

### Candidate Proposal

The system identifies multiple hotspots.

### Investigation

The system gathers evidence in visible steps.

It should be clear that some evidence was requested because the agent determined it was necessary.

### Rejection

The system discards at least one hotspot.

The discard reason should come from gathered evidence, not a UI-only label.

### Prioritization

The system ranks the strongest candidates.

### Recommendation

The system outputs what to fix first.

If the architecture makes any of those hard to show, it is too broad for the hackathon.

---

## 6. Reliability Plan

The architecture should support both:

- live execution where feasible
- precomputed fallback where necessary

Recommended reliability layers:

- one fully cached demo region
- persisted hotspot state
- prebuilt ranking payloads
- screenshot fallback assets

Caching should accelerate the demo without removing visible reasoning.

Recommended cache layers:

- `region cache`
  reused candidate proposals and region metadata for nearby repeated clicks
- `hotspot evidence cache`
  thermal, object, surface, and neighbor-comparison outputs for known hotspots
- `trace playback layer`
  reveals cached or precomputed evidence step by step over 5 to 15 seconds so the user still experiences investigation

Winning the demo matters more than maximizing live compute.

---

## 7. Ownership by Engineer

### Engineer 1

Frontend, map, investigation trace, ranking, recommendation UI.

### Engineer 2

API, orchestrator state machine, structured responses, cache path.

### Engineer 3

Hotspot proposal, object evidence, surface evidence.

### Engineer 4

Neighbor comparison, scoring, confidence aggregation, ranker.

---

## 8. Final Architectural Rule

ThermalGen should feel like a system that chooses what matters.

If forced to simplify, preserve only this:

- candidate discovery
- structured investigation
- explicit rejection
- ranked intervention output

That is the winning slice.
