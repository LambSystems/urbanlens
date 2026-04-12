# Urban Legend Goals
## Best in Agentic AI Strategy

This document defines the winning scope for Urban Legend in the Google Build with AI Hackathon.

It is not a generic roadmap. It is a decision document for one outcome:

> win `Best in Agentic AI`

---

## 1. Primary Objective

Build a system that clearly demonstrates:

- prompt-driven agent behavior over multimodal geospatial inputs
- evidence retrieval and reasoning over scattered drone imagery
- visible chain of thought under uncertainty
- conversational investigation that produces actionable recommendations

Urban Legend should feel like a decision-making product, not a research prototype.

---

## 2. What Winning This Track Requires

To win `Best in Agentic AI`, the project needs to make four things obvious very quickly.

Secondary objective:

> make the UI strong enough to also compete for `Best Design using v0` without compromising the core agentic slice

### 2.1 Real Agent Behavior

The system must visibly:

- interpret the user's question and decide how to investigate
- choose what tools to call and in what order
- gather evidence in steps through tool calls
- reason over imperfect source coverage
- reject weak candidates with evidence-backed reasoning
- produce a direct answer to what the user asked

If it looks like one LLM call over a prompt, it loses force. The chain of thought must show multi-step reasoning.

### 2.2 Prompt to Action

Judges must be able to follow:

`user question -> visible investigation -> chain of thought -> actionable answer`

If the output ends at "this area is hot", the project is underpowered for this track.

### 2.3 Visible Chain of Thought

The agent must look like it is thinking, not just rendering final answers.

That means the demo should show:

- the agent interpreting the user's question
- tool selection decisions
- evidence gathering in real time
- reasoning over findings
- rejection of weak signals
- final answer with supporting evidence

### 2.4 Strong Product Framing

The project should feel deployable and useful right away:

> ask a question about urban heat, watch the agent investigate, get an answer you can act on

Not:

> this is an interesting visualization or model trick

---

## 3. Final Scope Decision

We are not building the full platform.

We are building the most convincing prompt-driven investigation slice of the platform.

Recommended framing:

> ship the most convincing conversational urban heat investigation agent

This means depth over breadth.

---

## 4. Must / Should / Cut

## 4.1 Must Have

These are non-negotiable for a winning attempt.

### End-to-End Flow

- select one demo region
- user types a question about the region
- agent investigates with visible chain of thought
- agent calls tools, gathers evidence, reasons through findings
- agent discards at least one weak candidate
- agent returns an actionable answer with ranked recommendations
- user can ask a follow-up question

### Judge-Legible Chain of Thought

- every reasoning step and tool call visible in the UI
- at least 3 to 5 visible investigation steps per prompt
- tool choices motivated by the user's question, not a fixed pipeline
- clear distinction between reasoning, tool calls, findings, and the final answer

### Ranked Output

- Top 3 interventions when the question calls for prioritization
- severity, anomaly, confidence
- recommended action

### Demo-First UI

- map-first interface
- RGB plus thermal toggle
- hotspot markers
- prompt input field
- chain of thought panel
- conversation history
- recommendation display
- source-aware confidence messaging where coverage is partial

### Reliability

- one precomputed demo region
- cached chain of thought for common demo prompts
- fallback JSON or screenshots

---

## 4.2 Should Have

These increase winning odds but should never destabilize the core.

- neighbor comparison
- coarse material or surface inference
- lightweight consistency check across nearby crops or tiles
- session replay for investigation chain of thought
- polished explanation layer
- a stable schema contract shared by backend and frontend
- v0 used as a UI accelerator for the chain of thought panel and recommendation display
- coverage-aware confidence that reflects incomplete source availability

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

### 5.1 Prompt First

Every interaction starts with the user's question. The system investigates what the user asked, not what the system decided to analyze.

### 5.2 Rejection Is Mandatory

Rejecting at least one hotspot is a core proof of intelligence.

Many teams will only show detection.

Urban Legend should show discernment.

That rejection should be justified, not decorative.

### 5.3 Use Thermal as Evidence, Not the Product

The thermal model is an advantage, but not the headline.

The project should be framed as:

> an agent using thermal evidence to answer questions about urban heat

Not:

> a system that generates thermal imagery

In the best demo path, thermal should appear as evidence the agent chooses to consult based on what the user asked.

### 5.4 Explainability Over Bravado

The project should make credible claims:

- answers questions about urban heat with evidence
- prioritizes likely interventions
- compares hotspots against context
- shows its reasoning transparently

It should avoid overclaiming precise physical truth.

---

## 6. Team Plan for 4 Engineers

### Engineer 1: Frontend and Demo UX

- map interface
- thermal toggle
- prompt input and conversation UI
- chain of thought display panel
- hotspot visualization
- ranking and recommendation display
- demo mode and fallback states
- integrate and adapt v0-generated UI building blocks

### Engineer 2: Backend and Orchestrator

- API endpoints and session management
- agent orchestrator with Gemini
- chain of thought streaming
- tool routing
- structured responses for frontend
- cached execution path

### Engineer 3: Perception

- hotspot proposal
- object detection or classification
- coarse material inference
- thermal model integration
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

Region selection, thermal overlay, prompt input working.

### Milestone 2

Agent responds to a prompt with chain of thought — even if tools return stub data.

### Milestone 3

Visible chain of thought with real tool calls, evidence gathering, discard, and finalize.

### Milestone 4

Follow-up questions work. Ranked recommendations with explanations.

### Milestone 5

Polish, fallback path, demo rehearsal, and Devpost assets.

This is also the point where the team should explicitly capture and document where `v0` was used so the submission can credibly target the design prize.

---

## 8. Success Criteria

At the end of the hackathon, the system should:

- accept a user question about a region and investigate it
- show a visible chain of thought with tool calls and reasoning
- discard at least one hotspot with evidence-backed reasoning
- produce a ranked intervention list when the question calls for it
- support at least one follow-up question
- be understandable in under 60 seconds
- be stable enough for live judging

---

## 9. Final Strategic Rule

If the team gets stuck, optimize for this sequence only:

- user asks a question
- agent investigates with visible chain of thought
- agent returns an actionable answer

That loop is the product.
