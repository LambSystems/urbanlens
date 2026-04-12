# ThermalGen
## Best-in-Agentic-AI Urban Heat Triage Agent

ThermalGen is an agentic urban heat investigation system built for the `Best in Agentic AI` track.

Most tools stop at showing heat maps. ThermalGen goes one step further: it investigates candidate hotspots, decides what evidence it still needs, discards weak ones, prioritizes the strongest ones, and recommends what to fix first.

The project is also positioned to make a credible run at `Best Design using v0` by using `v0` to accelerate and polish the most visible UI surfaces around the core agentic flow.

The project is intentionally scoped around a single winning demo slice:

`select region -> detect hotspots -> investigate -> discard -> prioritize -> recommend`

---

## Problem

Urban heat is visible, but not actionable.

Stakeholders can often see that an area is hot, but they still cannot answer:

- Which hotspot matters most?
- What is causing it?
- Is it unusual relative to nearby structures?
- What should we fix first?

Existing tools usually provide analysis, not decisions.

In our build, Google Maps is the interaction layer, not the source of truth. The actual evidence comes from scattered drone imagery and related metadata that must first be retrieved and normalized for the selected region.

---

## Why This Is Agentic

ThermalGen is not a one-shot LLM wrapper and not just a thermal visualization pipeline.

It behaves like an agent by:

- selecting which hotspot to inspect next
- deciding what evidence it still needs
- calling tools to gather that evidence
- retrieving and normalizing available drone sources for the selected region
- comparing against context
- rejecting expected or weak candidates
- escalating strong candidates into ranked interventions

The key behavior is not just detection. It is decision-making under uncertainty.

---

## Core Demo Loop

1. User selects a region on the map
2. System retrieves and normalizes available drone evidence for that region
3. System proposes 3 to 5 candidate hotspots
4. Agent investigates a hotspot using structured tools
5. Agent discards low-value or expected hotspots
6. System ranks the remaining hotspots
7. System recommends the top intervention

This sequence is the product.

---

## Scope for the Hackathon

We are optimizing for one polished, judge-friendly experience rather than a broad platform.

### Must Have

- one stable demo region
- RGB map layer plus thermal overlay
- analysis region centered around the user click
- region-level source retrieval over scattered drone imagery
- 3 to 5 visible hotspot candidates
- investigation trace for at least 1 hotspot
- explicit tool-selection step in the investigation trace
- at least 1 discarded hotspot
- ranked Top 3 interventions
- confidence, severity, anomaly, and recommendation shown in UI
- fallback precomputed outputs for live demo reliability

### Should Have

- neighbor comparison
- coarse material or surface inference
- consistency check across nearby crops or tiles
- planner prompt like `What should we fix first in this area?`
- cached session replay for the demo
- shared schema contract between backend and frontend
- v0-assisted UI generation and polish for the sidebar, trace timeline, ranking cards, and recommendation panel
- coverage-aware confidence that reflects incomplete source availability

### Explicitly Cut

- multi-region live analysis
- temporal analysis
- intervention simulation
- overly complex model orchestration
- claims of precise physical temperature truth

---

## Architecture at a Glance

ThermalGen is built as a layered decision system:

- `Source Retrieval Layer`
  finds drone images and metadata intersecting the selected region
- `Evidence Normalization Layer`
  turns scattered imagery into analysis-ready region evidence
- `Thermal Generation Module`
  already prebuilt; treated as an evidence tool the agent can invoke
- `Candidate Discovery`
  proposes hotspots from thermal and image features
- `Perception Layer`
  identifies object or surface cues
- `Context Layer`
  compares hotspots against nearby structures
- `Agent Orchestrator`
  decides whether to inspect, call thermal/context tools, discard, or finalize
- `Planner`
  ranks interventions and produces recommendations
- `Map-First UI`
  makes the reasoning legible for judges

---

## Example Output

```json
{
  "location": "Chicago, IL",
  "hotspot_type": "commercial roof",
  "severity": 0.84,
  "anomaly": 0.71,
  "confidence": 0.78,
  "cause": "dark roofing material with unusually high heat relative to nearby roofs",
  "recommended_action": "cool-roof retrofit",
  "priority_rank": 1
}
```

---

## Demo Story

The demo is designed around one message:

> Most tools show you heat. ThermalGen tells you what to fix first.

The winning moment is when the system visibly decides it needs more evidence, rejects some hotspots, and prioritizes others.

That is the proof that the system is agentic.

---

## Team Strategy

This scope is designed for a 4-engineer team with strong implementation support from Codex and Claude Code.

- Engineer 1: frontend and demo UX
- Engineer 2: backend and orchestrator
- Engineer 3: perception and hotspot evidence
- Engineer 4: context, scoring, and ranking

The goal is not maximum feature count.

The goal is the most convincing decision-making slice of an urban heat agent.

---

## Strategic Framing

ThermalGen should be presented as:

> an agentic urban heat triage system that investigates candidate anomalies and recommends the highest-priority intervention

Not as:

- a thermal image generator
- a generic geospatial analytics dashboard
- a broad climate platform

Primary users:

- city councils
- facilities and campus operations teams
- sustainability planners

---

## Core Insight

The future of geospatial AI is not better maps.

It is agents that decide what matters and what to do next.
