# UrbanLens
## Agentic Local Environment Investigation Powered by ThermalGen

UrbanLens is our hackathon build for the `Best in Agentic AI` track.

The product is not a standalone thermal image generator. The product is an agent that investigates a selected locality, decides which tools to call, and returns an answer a user can act on.

`ThermalGen` is the star custom tool inside that system. It gives UrbanLens a capability most generic agents do not have: generating thermal evidence from map imagery and using that evidence in a larger investigation loop.

---

## Product Framing

UrbanLens should be presented as:

> an agent for localized environmental investigation that uses custom thermal reasoning to explain what matters in a place and what to do next

Not as:

- a heatmap viewer
- a generic map chatbot
- a standalone thermal generation demo

The winning story is:

1. user selects a locality in Google Maps
2. frontend captures a high-quality map image plus region metadata
3. backend stores the capture and creates an analysis
4. the agent decides what tools it needs
5. the agent calls `ThermalGen` when thermal evidence is useful
6. the agent combines thermal evidence with lighter tools like heat-risk profiling, object inspection, and ranking
7. the user gets an actionable answer with visible reasoning

---

## Core Utility

The strongest utility framing is:

- localized environmental investigation
- heat mitigation planning
- anomaly exploration for city or facilities teams
- quick triage of what deserves inspection or intervention first

Example questions:

- `What should we inspect first in this block?`
- `Why does this roof look risky?`
- `Where would shade or cooling interventions help most?`
- `Is there anything in this locality that looks thermally abnormal?`

The agent answers those questions by choosing tools, gathering evidence, and reasoning through what it finds.

---

## Why This Is Agentic

UrbanLens goes beyond simple chat because it:

- receives a concrete map capture and locality context
- reasons about what evidence is missing
- chooses tools to call
- invokes custom internal tools, including `ThermalGen`
- loops over evidence when needed
- rejects weak explanations
- returns a recommendation or investigation result tied to the user question

The key behavior is:

`question -> tool choice -> evidence gathering -> reasoning -> answer`

That is the product.

---

## Core Tools

### 1. ThermalGen

The wow-factor tool.

Purpose:

- generate thermal evidence from captured satellite or map imagery
- provide thermal overlays and hotspot-oriented heat evidence
- strengthen environmental investigation with a capability other teams will not have

### 2. Heat Risk Profiler

The supporting tool that makes the system feel like a broader agent, not a mono-tool wrapper.

Purpose:

- estimate heat risk from visible environmental cues
- summarize likely heat drivers such as exposed roof area, dark surfaces, low shade, and large pavement zones
- provide a second evidence source the agent can compare against ThermalGen

### 3. Supporting Internal Tools

- `inspect_object`
- `infer_surface`
- `analyze_heat_risk`
- `request_thermal_evidence`
- `compare_neighbors`
- `score_hotspots`
- `discard_hotspot`
- `finalize_recommendation`

These tools stay internal to the backend. The agent does not need to “go out to the internet” to feel agentic.

---

## Main User Flow

1. User selects a region in Google Maps.
2. Frontend sends region metadata plus a screenshot or crop.
3. Backend stores the capture and creates an `analysis`.
4. User asks a question or triggers a default investigation.
5. Agent decides which tools to call.
6. Agent gathers evidence in visible steps.
7. Agent returns:
   - an answer
   - ranked hotspots when applicable
   - recommendation(s)
   - visible reasoning trace
8. User can ask follow-up questions against the same analysis.

Planner Mode is a question layer over an existing analysis, not the main product on its own.

---

## Hackathon Scope

We are optimizing for one polished vertical slice.

### Must Have

- Google Maps region selection
- frontend capture plus region metadata
- backend capture ingestion and storage
- one strong analysis flow over a selected locality
- visible tool-calling trace
- `ThermalGen` integrated as a real tool
- one lighter second tool, `Heat Risk Profiler`
- at least one discarded finding
- at least one strong recommendation
- follow-up question support over the same analysis

### Should Have

- thermal overlay toggle
- hotspot markers
- Top 3 ranking for intervention-style prompts
- confidence and rationale badges
- v0-polished sidebar, trace, and recommendation surfaces

### Cut

- giant multi-city platform claims
- overly broad generic assistant behavior
- fragile live dependency on one LLM vendor
- excessive learned-model sprawl

---

## Stack

- `Google Maps API` for interaction and locality capture
- `Python + FastAPI` backend
- `React + TypeScript` frontend
- `LLMProvider` abstraction over:
  - `Anthropic` as the reliable default right now
  - `Gemini` if it stabilizes
  - `Featherless` as an open-model provider path and prize-track integration
- `ThermalGen` as the custom thermal evidence tool
- `ElevenLabs` for optional voice briefing in the demo layer
- `v0` for selected UI surfaces only

Important rules:

- `LLMProvider` must be provider-neutral. The system must not depend on one flaky provider to demo successfully.
- `ElevenLabs` is a demo/output layer, not the reasoning core.
- `Featherless` should plug into the same orchestrator contract, not fork the product.

---

## Architecture Summary

- `Frontend Capture Layer`
  captures map screenshot and locality metadata
- `Analysis API`
  stores capture, creates analysis, exposes results
- `Agent Orchestrator`
  decides what tools to call based on the question
- `ThermalGen`
  produces thermal evidence
- `Heat Risk Profiler`
  produces environmental risk signals from visible cues
- `Perception + Scoring`
  classifies, compares, ranks, and discards
- `Planner Mode`
  answers targeted follow-up questions over existing analysis outputs

---

## Final Strategic Message

UrbanLens wins if judges walk away thinking:

> this is an agent that can investigate a place, use a custom thermal tool nobody else has, and give me an answer I can actually use

That is the bar for the rest of the implementation.
