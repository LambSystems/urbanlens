# Urban Legend Architecture
## Prompt-Driven Agentic Investigation for Best in Agentic AI

This architecture is optimized for a hackathon-winning vertical slice, not a fully generalized platform.

The objective is to support one clear end-to-end behavior:

`select region -> load data -> user prompt -> agent investigates with visible chain of thought -> actionable answer`

---

## 1. Architecture Principle

Urban Legend should be built as a prompt-driven investigation system.

- deterministic components handle ingestion, normalization, and source retrieval
- narrow models produce partial evidence (thermal, perception, context)
- an agent orchestrator interprets the user's prompt and decides how to investigate
- every reasoning step and tool call is visible in the UI as chain of thought
- the user can ask follow-up questions in the same session

This keeps the system:

- debuggable
- demoable
- stable under time pressure
- legible to judges
- genuinely agentic — the user drives the investigation

---

## 2. Scope Philosophy

We are not trying to prove the maximum technical surface area.

We are trying to prove the clearest agentic loop driven by user intent.

That means:

- one strong demo region over many weak regions
- prompt-driven investigation over a fixed pipeline
- visible chain of thought over hidden complexity
- conversational depth over breadth of features
- evidence-seeking behavior motivated by what the user asked

---

## 3. High-Level System

```text
User selects demo region
        |
        v
Map-first frontend loads data context
(satellite, thermal overlay, source metadata)
        |
        v
User types a prompt
        |
        v
API/session layer (passes prompt + region context)
        |
        v
Agent orchestrator (Gemini)
   |-- interprets user intent
   |-- examines available data
   |-- decides what tools to call
   |
   |   Tool calls (visible chain of thought):
   |        |        |        |
   |        v        v        v
   |   Perception  Thermal  Context/Scoring
   |        \        |       /
   |         \       |      /
   |          v      v     v
   |      Evidence gathered
   |        |
   |        v
   |   Agent reasons over evidence
   |   (loop: need more evidence? call another tool)
   |        |
   |        v
   |   Agent produces answer
        |
        v
Structured response with chain of thought
        |
        v
Frontend renders: chain of thought + answer + recommendations
        |
        v
User asks follow-up question (same session)
```

---

## 3.1 Current Implemented Flow

This is the actual repo flow right now, before the final agentic layer is complete:

```text
Frontend map selection
        |
        v
POST /analysis
        |
        v
backend.app.orchestrator.build_analysis
   |-- retrieves local/demo source metadata
   |-- builds deterministic hotspot candidates
   |-- runs scoring and ranking
   |-- optionally calls hybrid thermal inference
        |
        v
GET /analysis/{region_id} polling
        |
        v
Frontend renders hotspot markers, ranking, trace steps, and recommendations
```

Live hybrid thermal inference inside `/analysis` is intentionally behind a local flag:

```text
THERMALGEN_ENABLE_LIVE_THERMAL=1
```

With the flag off, the demo remains fast and uses deterministic hotspot evidence. With the flag on, the orchestrator runs one local RGB image through `backend/app/thermal/generator.py`, writes generated thermal outputs under `backend/data/hybrid_thermal/`, serves them from `/thermal-assets/...`, and attaches `thermal_preview_url` to the analysis response.

The generated thermal image is evidence for the investigation. It is not yet the source of candidate discovery in `/analysis`; candidate discovery still uses the current static demo hotspot library.

For direct ThermalGen work, the backend also exposes focused tool endpoints:

```text
POST /thermal/infer/upload
  browser sends image bytes from a map capture
  backend stores the upload under backend/data/hybrid_thermal/uploads/
  backend writes prediction files under backend/data/hybrid_thermal/Predict_Thermal/

POST /thermal/infer/path
  internal/dev path for an existing repo-local RGB image
```

The normal frontend path should upload image bytes, not base64 JSON. The internal agent/tool path should pass file paths once the image is stored.

---

## 4. Main Layers

### 4.1 Frontend

The frontend is the investigation interface.

It must show:

- map with RGB plus thermal overlay
- prompt input for the user to ask questions
- chain of thought panel showing every agent reasoning step and tool call in real time
- evidence gathered at each step
- final answer with structured recommendations
- conversation history for follow-ups on the same region

The frontend should optimize for fast judge comprehension of the agent's reasoning process.

### 4.2 API and Session Layer

This layer manages the conversation between user and agent.

Responsibilities:

- accept region selection and load data context
- accept user prompt
- maintain session state so follow-up questions have context
- route prompt + data context to the agent orchestrator
- stream chain of thought steps back to the frontend
- return structured response with answer and evidence

This layer should not contain reasoning logic — that belongs to the agent.

### 4.2.1 Source Retrieval and Evidence Normalization

Google Maps is the interface layer, not the ground-truth data layer.

The selected region must first be resolved against available drone imagery and metadata, which may be scattered, partial, or inconsistent in coverage.

Responsibilities:

- find drone images intersecting the selected region
- attach source metadata
- normalize crops or region evidence into a shared internal format
- expose coverage quality to downstream confidence logic
- tolerate incomplete metadata
- optionally enrich weak metadata using Google Maps context

### 4.3 Thermal Evidence Layer

The satellite-to-thermal conversion model is prebuilt and should be treated as stable infrastructure plus an evidence tool.

Responsibilities:

- convert satellite imagery to thermal representation
- provide the thermal image for UI overlay display
- expose thermal-derived data for the analysis pipeline
- return hotspot-specific heat evidence when the agent requests it

The thermal module is not the product. It is evidence the agent can choose to consult.

### 4.4 Perception Layer

This layer answers:

- what object is this hotspot attached to
- what coarse surface or material might it be

These are tools the agent calls when it decides it needs object or material evidence to answer the user's question.

Supported hotspot taxonomy for the MVP:

- `roof`
- `road_pavement`
- `parking_lot`
- `hvac_mechanical`
- `vegetation_loss`
- `other`

### 4.5 Context Layer

This layer answers:

- is this hotspot unusually hot relative to nearby structures
- is it expected in local context
- is this signal consistent across nearby crops or tiles
- is source coverage sufficient to trust the finding strongly

This is where the project gains credibility as a triage system rather than a detector.

### 4.6 Scoring Layer

This layer computes:

- severity
- anomaly
- confidence

For the hackathon, this should favor explainable heuristics over fragile complexity.

Scoring hierarchy:

- `anomaly` is the structural gate
- `severity` orders surviving hotspots
- `confidence` modulates whether the result should be trusted and how strongly it should be presented

Confidence should incorporate both reasoning quality and evidence coverage quality.

### 4.7 Agent Orchestrator

This is the core of the product.

The agent receives:

- the user's prompt (their question or intent)
- the data context for the selected region (thermal data, source records, metadata)
- conversation history (for follow-ups)

The agent then:

- interprets what the user is asking
- examines the available data to understand what evidence exists
- decides what tools to call and in what order based on the question
- executes tools and gathers evidence
- reasons over the evidence and decides if more is needed
- produces an answer with supporting evidence and recommendations

Every reasoning step and tool call is recorded as chain of thought and streamed to the frontend.

Available tools:

- `inspect_object` — identify the object type at a hotspot
- `request_thermal_evidence` — get thermal data for a specific location
- `infer_surface` — estimate surface material
- `compare_neighbors` — compare against nearby structures
- `check_consistency` — verify signal across sources
- `score_hotspot` — compute anomaly, severity, confidence
- `discard_hotspot` — reject a weak candidate with reasoning
- `finalize_hotspot` — promote a candidate for recommendation

The agent may also access additional tools depending on what the user asks — location lookups, metadata queries, broader context retrieval.

The tool set is kept constrained enough that the chain of thought stays understandable.

Different user prompts lead to different investigation paths through the same tool set. The agent's route is driven by the question, not by a fixed pipeline.

### 4.8 Planner

The planner turns validated evidence into:

- ranked priority
- recommended action
- concise rationale

This is the business-value layer.

Without it, the system only observes. With it, the system recommends.

---

## 5. Required Demo Behaviors

The architecture must support these behaviors explicitly:

### Prompt-Driven Investigation

The user types a question. The agent investigates based on that question, not a fixed pipeline.

### Visible Chain of Thought

Every reasoning step and tool call is shown in the UI. Judges can watch the agent think.

### Evidence Gathering

The agent gathers evidence in visible steps. It should be clear that evidence was requested because the agent determined it was necessary to answer the user's question.

### Rejection

The agent discards at least one hotspot or finding. The discard reason should come from gathered evidence and relate to the user's question.

### Actionable Answer

The agent returns an answer the user can act on — not just data, but a recommendation.

### Follow-Up Questions

The user can ask follow-up questions that build on the previous investigation.

If the architecture makes any of those hard to show, it is too broad for the hackathon.

---

## 6. Reliability Plan

The architecture should support both:

- live execution where feasible
- precomputed fallback where necessary

Recommended reliability layers:

- one fully cached demo region
- persisted session state
- prebuilt chain of thought sequences for common prompts
- screenshot fallback assets

Caching should accelerate the demo without removing visible reasoning.

Recommended cache layers:

- `region cache`
  reused data context and source records for nearby repeated clicks
- `investigation cache`
  cached chain of thought and answers for known demo prompts
- `chain of thought playback`
  reveals cached reasoning step by step so the user still experiences investigation

For the hackathon, source retrieval can be simplified to a curated region-to-drone-evidence mapping as long as the backend contract already models scattered source inputs.

Winning the demo matters more than maximizing live compute.

---

## 7. Ownership by Engineer

### Engineer 1

Frontend, map, prompt input, chain of thought display, conversation UI, recommendation panels.

### Engineer 2

API, agent orchestrator, session management, chain of thought streaming, cache path.

### Engineer 3

Hotspot proposal, object evidence, surface evidence, thermal integration.

### Engineer 4

Neighbor comparison, scoring, confidence aggregation, ranker.

---

## 8. Final Architectural Rule

Urban Legend should feel like a system that answers your questions about urban heat by investigating the evidence.

If forced to simplify, preserve only this:

- user types a question
- agent investigates with visible chain of thought
- agent returns an actionable answer

That is the winning slice.
