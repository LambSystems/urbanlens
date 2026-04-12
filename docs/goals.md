# ThermalGen V2 Goals
## Best in Agentic AI Strategy

This document defines the winning scope for ThermalGen in the Google Build with AI Hackathon.

It is not a generic roadmap. It is a decision document for one outcome:

> win `Best in Agentic AI`

---

## 1. Primary Objective

Build a system that clearly demonstrates:

- agent behavior over multimodal geospatial inputs
- evidence retrieval and reasoning over scattered drone imagery
- visible decision-making under uncertainty
- ranked, actionable outputs instead of passive analysis

ThermalGen should feel like a decision-making product, not a research prototype.

---

## 2. What Winning This Track Requires

To win `Best in Agentic AI`, the project needs to make four things obvious very quickly.

Secondary objective:

> make the UI strong enough to also compete for `Best Design using v0` without compromising the core agentic slice

### 2.1 Real Agent Behavior

The system must visibly:

- choose what to inspect
- decide what evidence is missing
- gather evidence in steps through tool calls
- reason over imperfect source coverage
- reject weak candidates
- prioritize the strongest ones

If it looks like one LLM call over a prompt, it loses force.

### 2.2 Input to Action

Judges must be able to follow:

`region -> investigation -> reasoning -> ranked recommendation`

If the output ends at "this area is hot", the project is underpowered for this track.

### 2.3 Visible Reasoning

The agent must look like it is thinking, not just rendering final answers.

That means the demo should show:

- candidate discovery
- tool selection
- investigation trace
- rejection
- prioritization

### 2.4 Strong Product Framing

The project should feel deployable and useful right away:

> this helps decide what to fix first

Not:

> this is an interesting visualization or model trick

---

## 3. Final Scope Decision

We are not building the full platform.

We are building the most convincing vertical slice of the platform.

Recommended framing:

> ship the most convincing decision-making slice of an urban heat agent

This means depth over breadth.

---

## 4. Must / Should / Cut

## 4.1 Must Have

These are non-negotiable for a winning attempt.

### End-to-End Flow

- select one demo region
- show candidate hotspots
- investigate at least one hotspot in detail
- show at least one explicit evidence-seeking decision
- discard at least one low-value candidate
- rank the remaining hotspots
- recommend the top action

### Judge-Legible Agent Loop

- at least 2 to 3 visible investigation steps
- explicit orchestrator state or trace
- tool choices limited enough to be legible
- at least one trace step where the agent decides to call thermal or context evidence

### Ranked Output

- Top 3 interventions
- severity
- anomaly
- confidence
- recommended action

### Demo-First UI

- map-first interface
- RGB plus thermal toggle
- hotspot markers
- evidence panel
- ranking panel
- recommendation card
- source-aware confidence messaging where coverage is partial

### Reliability

- one precomputed demo region
- cached outputs
- fallback JSON or screenshots

---

## 4.2 Should Have

These increase winning odds but should never destabilize the core.

- neighbor comparison
- coarse material or surface inference
- lightweight consistency check across nearby crops or tiles
- prompt-based planner mode
- session replay for investigation trace
- polished explanation layer
- a stable schema contract shared by backend and frontend
- v0 used as a UI accelerator for the demo shell and the highest-visibility result panels

---

## 4.3 Cut

These are attractive but not aligned with the fastest path to winning.

- multi-region live analysis
- temporal analysis across multiple images
- intervention simulation
- platform-style workflow features
- too many new learned models
- perfect thermal realism work
- broad climate adaptation claims

---

## 5. Product Principles

### 5.1 Decision First

Every screen and every model output should support one question:

> what should we fix first?

### 5.2 Rejection Is Mandatory

Rejecting at least one hotspot is a core proof of intelligence.

Many teams will only show detection.

ThermalGen should show discernment.

That rejection should be justified, not decorative.

Examples:

- expected road heat profile
- not anomalous relative to nearby roofs
- insufficient evidence to prioritize

### 5.3 Use Thermal as Evidence, Not the Product

The thermal generator is an advantage, but not the headline.

The project should be framed as:

> an agent using thermal evidence to make intervention decisions

Not:

> a system that generates thermal imagery

In the best demo path, thermal should appear as evidence the agent chooses to consult, not just a static layer shown from the beginning.

The same is true for source coverage: the system should acknowledge when it is reasoning over strong region evidence versus partial scattered drone evidence.

### 5.4 Explainability Over Bravado

The project should make credible claims:

- prioritizes likely interventions
- helps triage heat risks
- compares hotspots against context

It should avoid overclaiming precise physical truth.

---

## 6. Team Plan for 4 Engineers

### Engineer 1: Frontend and Demo UX

- map interface
- thermal toggle
- hotspot visualization
- investigation trace UI
- ranking panel
- recommendation card
- demo mode and fallback states
- integrate and adapt v0-generated UI building blocks

### Engineer 2: Backend and Orchestrator

- API endpoints
- hotspot state machine
- tool routing
- evidence-request logic
- structured responses for frontend
- cached execution path

### Engineer 3: Perception

- hotspot proposal
- object detection or classification
- coarse material inference
- evidence packaging

### Engineer 4: Context and Scoring

- neighbor comparison
- consistency checks across nearby crops or tiles
- anomaly score
- severity score
- confidence aggregation
- final ranking logic

---

## 7. Integration Milestones

### Milestone 1

Region selection, thermal overlay, hotspot markers.

### Milestone 2

Per-hotspot evidence panel with object, material, and initial scores.

### Milestone 3

Visible orchestrator trace with evidence-request decisions, compare, discard, finalize.

### Milestone 4

Top 3 ranked recommendations with explanations.

### Milestone 5

Polish, fallback path, demo rehearsal, and Devpost assets.

This is also the point where the team should explicitly capture and document where `v0` was used so the submission can credibly target the design prize.

---

## 8. Success Criteria

At the end of the hackathon, the system should:

- process one region end-to-end without confusion
- show that it investigated more than one candidate
- show that it requested additional evidence before finalizing at least one candidate
- visibly discard at least one hotspot
- produce a ranked intervention list
- be understandable in under 60 seconds
- be stable enough for live judging

---

## 9. Final Strategic Rule

If the team gets stuck, optimize for this sequence only:

- detect candidates
- investigate them
- discard weak ones
- prioritize strong ones
- recommend action

That loop is the product.
