# UrbanLens Architecture
## Capture-Based Locality Investigation Agent

This architecture reflects the current best plan for the hackathon.

The product is:

> an agent that investigates a selected locality using internal tools, with `ThermalGen` as the custom standout tool

The old “scattered drone imagery as primary source” framing is no longer the core story. We still support external imagery or supplemental data later, but the canonical MVP flow starts from a frontend map capture.

---

## 1. High-Level Principle

UrbanLens should feel like:

- a locality investigation system
- with visible tool-calling
- using a custom thermal tool
- to answer useful questions about a place

It should not feel like:

- a one-shot image-to-text wrapper
- a standalone thermal map generator
- a generic chat assistant attached to Google Maps

---

## 2. Canonical MVP Flow

```text
User selects region in Google Maps
        |
        v
Frontend captures:
- region metadata
- viewport/map state
- screenshot/crop
        |
        v
Backend stores capture and creates analysis
        |
        v
User asks a question or triggers default analysis
        |
        v
Agent orchestrator examines:
- prompt
- region metadata
- captured image
- prior analysis state
        |
        v
Agent calls internal tools:
- ThermalGen
- Heat Risk Profiler
- object/surface inspection
- scoring/ranking
        |
        v
Agent reasons over evidence
        |
        v
Agent returns:
- answer
- recommendations
- visible trace
- hotspot findings when applicable
```

---

## 3. Main Layers

### 3.1 Frontend Capture Layer

The frontend is responsible for:

- region selection
- Google Maps state capture
- screenshot or crop creation
- sending structured metadata plus the image to the backend

Recommended capture payload:

- `region.bounds`
- `region.center`
- `region.areaKm2`
- `map.zoom`
- `map.mapTypeId`
- `map.tilt`
- `map.heading`
- `viewport`
- `image`

The backend should support both:

- `multipart/form-data` with a real image file
- JSON + base64 fallback

### 3.2 Analysis API

The API layer should:

- accept captures
- persist them to a local directory for replay/debugging
- create an `analysis`
- expose analysis state and outputs
- expose a follow-up question layer over an existing analysis

Canonical resource model:

- `analysis` is the main resource
- `questions` are nested over an analysis

### 3.3 Agent Orchestrator

This is the product core.

It receives:

- the user question or investigation intent
- region metadata
- screenshot/crop
- prior analysis state

It decides:

- whether to call `ThermalGen`
- whether to call `Heat Risk Profiler`
- whether to inspect objects or surfaces
- whether to rank or simply explain

The orchestrator should stay provider-neutral through `LLMProvider`.

### 3.4 ThermalGen

ThermalGen is the special internal tool.

Responsibilities:

- generate thermal evidence from captured map imagery
- provide a thermal overlay or thermal-derived signals
- support hotspot reasoning

ThermalGen is not the whole product. It is the custom capability that makes the larger agent more powerful.

### 3.5 Heat Risk Profiler

This is the recommended second tool.

Responsibilities:

- estimate heat risk from visible environmental cues
- summarize likely risk drivers such as large roof area, dark surfaces, exposed pavement, and low shade
- provide a second evidence source the agent can reconcile with thermal output

This keeps the system from feeling like a single-tool wrapper.

### 3.6 Perception Layer

Supporting perception tools may include:

- object typing
- coarse surface inference
- visible structure hints

These tools are narrow and supporting. They feed evidence to the agent; they are not the headline.

### 3.7 Scoring Layer

Use deterministic scoring where possible.

Recommended hierarchy:

- anomaly gates
- severity orders
- confidence modulates

This should remain transparent and stable, not LLM-owned.

### 3.8 Planner Mode

Planner Mode is a question layer on top of existing analysis.

Examples:

- `What should we inspect first here?`
- `Why is this roof risky?`
- `What evidence made you call this a priority?`

Planner Mode is not the main product by itself. It is a way to deepen the investigation after the initial answer.

---

## 4. Tool Set

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

Design rule:

keep tools internal, explicit, and controlled. The agent should feel powerful because it has real custom tools, not because it has unbounded freedom.

---

## 5. LLM Provider Strategy

The architecture must not depend on one flaky vendor.

Use:

- `Anthropic` as current reliable default
- `Gemini` behind the same provider abstraction
- `MockProvider` for fallback and testing

`LLMProvider` should support at least:

- free-text generation
- structured generation when needed
- tool-selection assistance

This lets the demo survive vendor instability.

---

## 6. Storage and Reproducibility

Store captures locally for replay:

- `backend/data/captures/{region_id}/source.png`
- `backend/data/captures/{region_id}/metadata.json`
- optionally `thermal.png`

This gives:

- reproducible demos
- debug visibility
- easy fallback

For the hackathon, local file storage is enough.

---

## 7. Demo Architecture Rule

If the team has to simplify, preserve only this:

- selected locality
- captured image
- agent tool-calling
- `ThermalGen` visibly used
- one supporting tool visibly used
- grounded answer returned

That is the architecture that best matches the pivot and the judging criteria.
