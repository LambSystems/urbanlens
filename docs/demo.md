# Urban Legend Demo
## Best in Agentic AI Demo Script and Execution Plan

This demo is designed to win `Best in Agentic AI`.

The goal is not to explain every model. The goal is to make judges feel, very quickly, that the system is:

> listening to what the user asks, investigating with visible reasoning, and coming back with an answer you can act on

---

## 1. Demo Objective

By the first minute, a judge should understand:

- why this is an agent (it investigates based on what you ask)
- why it is more than a heat map (it reasons, rejects, and recommends)
- that you can have a conversation with it about urban heat data

If those three things are clear, the demo is doing its job.

---

## 2. Core Narrative

Use this framing:

> Ask a question about urban heat. Watch the agent investigate. Get an answer you can act on.

This framing is stronger than leading with models or thermal generation. It puts the user's question at the center.

---

## 3. Golden Path

### Step 1: Establish the Region

What you say:

> We are looking at a real region. The system has loaded satellite imagery, thermal data from our conversion model, and metadata from scattered drone sources.

What you show:

- map view
- RGB layer
- thermal overlay toggle
- data context loaded indicator

Time:

- 5 to 10 seconds

Goal:

- establish the data context fast
- frame Google Maps as the interface, not the only data source

---

### Step 2: Ask the First Question

This is the key moment. The user types a question.

What you say:

> Now we ask: "What should I fix first in this area?"

What you show:

- user types the prompt
- agent begins investigating — chain of thought starts streaming

Time:

- 5 seconds to type

Goal:

- show that the user drives the investigation
- the agent responds to the specific question

---

### Step 3: Watch the Chain of Thought

This is the most important section.

What you say:

> Watch the agent think. It is deciding what evidence to gather, calling tools, and reasoning through what it finds.

What you show:

- chain of thought panel with steps appearing in real time:
  1. agent interprets the question
  2. lists hotspot candidates
  3. inspects an object — identifies it as a roof
  4. requests thermal evidence — high intensity detected
  5. compares against neighbors — hotter than 83% of nearby roofs
  6. scores the hotspot

Time:

- 15 to 25 seconds

Goal:

- prove visible reasoning and tool use driven by the question

---

### Step 4: Show Rejection

What you say:

> Not every hotspot matters. The agent found a road with expected heat and dismissed it.

What you show:

- chain of thought step: agent inspects road pavement
- chain of thought step: agent checks thermal — consistent with nearby roads
- chain of thought step: agent discards — "expected road heat profile"

Time:

- 10 to 15 seconds

Goal:

- prove discernment, not just detection
- the rejection reason is visible in the chain of thought

---

### Step 5: See the Answer

What you say:

> The agent has finished investigating. Here is what it recommends.

What you show:

- agent's final answer in the conversation
- Top 3 ranked hotspots with severity, anomaly, confidence
- recommendation card: what to fix, why, what action to take

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

### Step 6: Ask a Follow-Up

What you say:

> Now we dig deeper. We ask: "How confident are you about that roof?"

What you show:

- user types follow-up prompt
- agent reasons over prior findings and source coverage
- returns a focused answer about confidence factors

Time:

- 10 to 15 seconds

Goal:

- prove the system is conversational and can build on prior investigation
- this is a strong differentiator that most hackathon projects will not have

---

## 4. Time Budget

| Section | Time |
| --- | --- |
| Setup and region load | 10s |
| Type first question | 5s |
| Chain of thought investigation | 25s |
| Rejection visible | 15s |
| Answer and recommendations | 15s |
| Follow-up question | 15s |

Total:

- about 1.5 to 2 minutes

---

## 5. UI Requirements

### Map Layer

- one stable demo region
- RGB plus thermal toggle
- hotspot markers

### Prompt Input

- text input field for the user's question
- visible in the sidebar or bottom panel
- send button or enter to submit

### Chain of Thought Panel

- real-time display of agent reasoning steps
- step types: reasoning, tool_call, finding, answer
- each step shows a summary
- tool calls show which tool was invoked and what it returned
- steps transition through pending -> running -> completed

### Conversation History

- shows prior prompts and answers
- follow-up questions appear in the same thread
- scrollable

### Recommendation Display

- Top 3 hotspots when applicable
- short rationale
- priority labels
- anomaly, severity, and confidence values or badges

### Recommendation Card

- what it is
- why it matters
- what to do next

### v0 UI Scope

Use `v0` to accelerate and polish the highest-visibility UI pieces:

- prompt input and conversation thread
- chain of thought timeline
- ranking cards
- recommendation card

The map and application logic remain custom. `v0` is used to speed up strong UI composition around the core flow.

---

## 6. What Makes This Demo Competitive

### User-Driven Investigation

The user asks a question. The agent investigates that specific question. This is more agentic than a system that auto-runs the same pipeline every time.

### Visible Chain of Thought

Every reasoning step is shown. Judges can watch the agent think.

### Rejection

Showing a discarded hotspot is not optional. It is one of the cleanest proofs of agency.

### Conversational Depth

Follow-up questions prove the system maintains context and builds on prior investigation. Most hackathon projects will not have this.

### Clear End State

The demo must end with an actionable answer, not a finding.

### Speed and Stability

Precompute aggressively if needed. Judging rewards clarity and reliability more than live complexity.

---

## 7. Backup Plan

### Primary Safety Net

- one fully precomputed region
- cached chain of thought for demo prompts
- fallback JSON responses

### Screenshot Safety Net

- map with hotspots screenshot
- chain of thought screenshot
- answer with recommendations screenshot

### Reduced Mode

If the full agent path breaks:

- show cached chain of thought
- still show rejection
- still show the answer
- still show the recommendation

The demo must survive partial failure.

---

## 8. Team Roles During Demo

### Presenter

- controls the narrative
- explains behavior, not internals

### Operator

- clicks map, types prompts
- keeps the pace tight

### Support 1

- watches backend state

### Support 2

- prepares fallback instantly if needed

---

## 9. Recommended Lines

### Opening

> Most tools show you heat. We built an agent you can ask questions — and it investigates with visible reasoning.

### When Typing the Prompt

> We ask: what should I fix first in this area?

### During Chain of Thought

> The agent is deciding what evidence it needs. Watch it reason through each step.

### During Rejection

> This hotspot is real, but the agent found it is not worth acting on first. Here is why.

### During Answer

> Here is the agent's answer — with ranked recommendations and reasoning you can trace.

### During Follow-Up

> Now we dig deeper with a follow-up question. The agent builds on what it already found.

### Final Line

> That is Urban Legend. Ask a question about urban heat. Get an answer you can act on.

---

## 10. Demo Mistakes to Avoid

- opening with technical model details
- overexplaining infrastructure
- skipping the rejection step
- ending on analysis instead of an answer
- relying on live inference without fallback
- not showing the follow-up question (it is a strong differentiator)
- forcing a v0-generated layout that hurts chain of thought legibility

---

## 11. Final Demo Rule

If time is short, preserve this sequence at all costs:

- user asks a question
- chain of thought streams with visible tool calls
- at least one hotspot rejected
- answer with ranked recommendations
- one follow-up question

That is the proof of agentic behavior.
