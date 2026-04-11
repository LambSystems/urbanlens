# ThermalGen V2 Demo
## Best in Agentic AI Demo Script and Execution Plan

This demo is designed to win `Best in Agentic AI`.

The goal is not to explain every model. The goal is to make judges feel, very quickly, that the system is:

> detecting, deciding what evidence it needs, investigating, rejecting, prioritizing, and recommending

---

## 1. Demo Objective

By the first minute, a judge should understand:

- why this is an agent
- why it is more than a heat map
- what action the system recommends

If those three things are clear, the demo is doing its job.

---

## 2. Core Narrative

Use this framing:

> Most tools show you heat. ThermalGen investigates hotspots and tells you what to fix first.

This framing is stronger than leading with models or thermal generation.

---

## 3. Golden Path

### Step 1: Establish the Region

What you say:

> We are looking at a real region with RGB imagery, generated thermal evidence, and geospatial context.

What you show:

- map view
- RGB layer
- thermal overlay toggle

Time:

- 5 to 10 seconds

Goal:

- establish inputs fast

---

### Step 2: Show Candidate Hotspots

What you say:

> First, the system proposes candidate hotspots worth investigating.

What you show:

- 3 to 5 hotspot markers

Time:

- 10 to 15 seconds

Goal:

- make it clear these are candidates, not final answers

---

### Step 3: Walk Through Investigation

This is the most important section.

What you say:

> Instead of stopping at detection, the agent decides what evidence it needs next.

Walk one hotspot through a visible trace:

1. detect object
2. decide it needs thermal or context evidence
3. infer surface or material
4. compare against nearby structures
5. decide whether to discard or escalate

What you show:

- selected hotspot
- evidence panel
- investigation trace
- tool call or evidence request label
- labels such as roof, dark membrane, hotter than neighbors

Time:

- 20 to 30 seconds

Goal:

- prove visible reasoning and tool use

---

### Step 4: Show Rejection

What you say:

> Not every hotspot matters. The agent filters out expected or low-value ones.

What you show:

- one hotspot marked `discarded` or `low priority`

Time:

- 10 to 15 seconds

Goal:

- prove discernment, not just detection

This is one of the strongest agentic signals in the whole demo.

Make the rejection reason visible.

Examples:

- expected road heat pattern
- not hotter than nearby comparable roofs
- low confidence after evidence gathering

---

### Step 5: Show Prioritization

What you say:

> Then the system ranks the remaining hotspots by actionability and confidence.

What you show:

- Top 3 ranked hotspots
- severity
- anomaly
- confidence

Time:

- 10 to 15 seconds

Goal:

- prove decision quality, not just analysis

---

### Step 6: Land the Recommendation

What you say:

> This is the first thing you should fix.

What you show:

- final recommendation card
- hotspot type
- why it matters
- recommended intervention

Example:

- Commercial roof
- Unusually hot relative to nearby roofs
- Recommended action: cool-roof retrofit
- Confidence: 78%

Time:

- 10 to 15 seconds

Goal:

- end on action, not description

---

## 4. Time Budget

| Section | Time |
| --- | --- |
| Setup | 10s |
| Candidate discovery | 15s |
| Investigation | 30s |
| Rejection | 15s |
| Prioritization | 15s |
| Final recommendation | 15s |

Total:

- about 1.5 to 2 minutes

---

## 5. UI Requirements

### Map Layer

- one stable demo region
- RGB plus thermal toggle
- hotspot markers

### Evidence Panel

- object type
- material or surface class
- thermal evidence used or not used
- context evidence used or not used
- anomaly
- severity
- confidence

### Investigation Trace

- detected object
- requested thermal evidence
- requested context comparison
- inferred material
- compared neighbors
- discarded or escalated

### Ranking Panel

- Top 3 hotspots
- short rationale
- priority labels

### Recommendation Card

- what it is
- why it matters
- what to do next

---

## 6. What Makes This Demo Competitive

### Visible Thinking

The system must look like it is deciding what to do next.

### Rejection

Showing a discarded hotspot is not optional. It is one of the cleanest proofs of agency.

### Clear End State

The demo must end with a recommendation, not a finding.

### Speed and Stability

Precompute aggressively if needed. Judging rewards clarity and reliability more than live complexity.

If live tool-calling is risky, precompute the outputs but still render the evidence-request steps clearly in the trace.

---

## 7. Backup Plan

### Primary Safety Net

- one fully precomputed region
- cached investigation outputs
- fallback JSON responses

### Screenshot Safety Net

- hotspot map screenshot
- investigation trace screenshot
- ranked output screenshot

### Reduced Mode

If the full orchestrator path breaks:

- show cached investigation
- still show rejection
- still show ranking
- still land the recommendation

The demo must survive partial failure.

---

## 8. Team Roles During Demo

### Presenter

- controls the narrative
- explains behavior, not internals

### Operator

- clicks through UI
- keeps the pace tight

### Support 1

- watches backend state

### Support 2

- prepares fallback instantly if needed

---

## 9. Recommended Lines

### Opening

> Most tools show you heat. We built an agent that tells you what to fix first.

### During Investigation

> The agent is deciding what evidence it needs next.

### During Rejection

> This hotspot is real, but not worth acting on first.

### During Ranking

> Now the system prioritizes by severity, anomaly, and confidence.

### Final Line

> This is the first intervention we would recommend.

---

## 10. Demo Mistakes to Avoid

- opening with technical model details
- overexplaining infrastructure
- skipping the rejection step
- ending on analysis instead of action
- relying on live inference without fallback

---

## 11. Final Demo Rule

If time is short, preserve this sequence at all costs:

- hotspot candidates
- evidence-request step
- investigation trace
- rejected hotspot
- Top 3 ranking
- final recommendation

That is the proof of agentic behavior.
