# UrbanLens Goals
## Winning the Agentic AI Track With the New Pivot

This document defines the strongest plan for the current product direction.

The current direction is:

> build an agent for localized environmental investigation, with `ThermalGen` as the custom standout tool inside the agent

This is no longer a “thermal demo first” project.

---

## 1. Primary Objective

Win `Best in Agentic AI` by making these things obvious in under a minute:

- the product is an agent, not a static pipeline
- the agent calls internal tools to investigate a locality
- one of those tools is a custom thermal tool that gives us a real differentiator
- the result is a grounded, useful answer

Secondary objective:

> keep the UI polished enough to also make a credible run at `Best Design using v0`

---

## 2. The Final Product Story

The product should be framed as:

> a locality analysis agent that helps users investigate a place and understand what matters there, using custom thermal reasoning when useful

The strongest examples are:

- heat mitigation planning
- city or campus operations triage
- identifying where shade or cooling interventions may matter
- environmental anomaly exploration in a small locality

The point is not “we can answer anything about the world.”

The point is:

> given a selected locality, we can investigate it better than a generic agent because we have a custom thermal tool and a tight set of supporting tools

---

## 3. What the Agent Must Do

The winning slice should visibly do this:

1. receive a locality capture from the frontend
2. understand the user’s question or investigation intent
3. decide which tools to call
4. call `ThermalGen` when thermal evidence is relevant
5. call at least one additional non-thermal analysis tool
6. reason over the combined evidence
7. reject weak explanations or low-priority findings
8. return an actionable answer

If the system looks like “LLM sees image -> final paragraph,” it is too weak.

---

## 4. Final Scope Decision

We are building one convincing agentic locality investigation loop.

We are not building:

- a giant geospatial platform
- a broad world-model assistant
- a purely thermal image generation showcase

Recommended framing:

> ship the cleanest possible example of a custom-tool locality investigation agent

---

## 5. Must / Should / Cut

## 5.1 Must Have

### Capture-Based Input

- Google Maps region selection
- structured region metadata
- screenshot or crop upload to backend
- persisted capture for replay and debugging

### Agentic Investigation

- user can ask a region-specific question or trigger the default analysis path
- agent selects tools instead of running one hidden fixed pipeline
- tool-calling trace is visible
- trace includes at least one `ThermalGen` call
- trace includes at least one non-thermal tool call

### Useful Outcome

- at least one strong finding or recommendation
- at least one discarded candidate or explanation
- rationale grounded in gathered evidence

### Reliability

- one golden demo region
- cached or replayable outputs if needed
- LLM provider abstraction so the demo is not blocked by Gemini instability

---

## 5.2 Should Have

- thermal overlay in UI
- hotspot markers
- a second internal tool like `Heat Risk Profiler`
- follow-up question support over an existing analysis
- Top 3 ranking for intervention-style prompts
- v0-polished right sidebar and trace view

---

## 5.3 Cut

- sprawling tool sets that do not improve the demo
- broad “ask anything” world-explorer claims
- physics-heavy thermal claims you cannot defend
- dependency on one vendor model if it is unstable
- adding more models just to look impressive

---

## 6. Tool Strategy

### ThermalGen

Keep `ThermalGen` as the star custom tool.

It is the wow factor and the custom capability most teams will not have.

### Supporting Tool

Add one lighter second tool to make the system feel like a broader agent:

- `Heat Risk Profiler`
  or
- `Shade Gap Analyzer`

The best default right now is `Heat Risk Profiler`.

Its job is not to beat ThermalGen. Its job is to:

- analyze visible environmental cues
- explain likely heat drivers
- give the agent another evidence source to compare against thermal output

That makes the system feel more agentic and less single-purpose.

---

## 7. LLM Strategy

Use an `LLMProvider` abstraction.

Current recommendation:

- `Anthropic` as default for demo reliability
- `Gemini` as optional or fallback provider if it stabilizes
- `Featherless` as an additional provider path for open models and prize eligibility
- deterministic scoring and ranking wherever possible

Practical team rule:

- the product must work with Anthropic alone
- Featherless should integrate through the same provider interface
- Gemini should not block the demo

The agent should use the LLM for:

- tool-selection reasoning
- follow-up question answering
- explanation wording

The LLM should not own:

- ranking math
- hotspot scores
- geometry
- hard-coded discard logic

## 7.1 ElevenLabs Strategy

`ElevenLabs` should be treated as a demo enhancement layer, not a core dependency.

Best use:

- short spoken briefing of the final result
- one-click `Play briefing` after analysis completes

Do not make voice a required step of the product loop.
The product must still win visually and functionally without audio.

---

## 8. Team Plan

### Engineer 1

- map capture UX
- screenshot packaging
- sidebar and trace UI
- analysis and follow-up interaction flow
- optional voice briefing playback UI

### Engineer 2

- capture ingestion endpoints
- storage of image plus metadata
- orchestrator and tool routing
- LLM provider abstraction
- optional ElevenLabs backend endpoint for generated voice briefings

### Engineer 3

- ThermalGen integration
- object/surface cues
- supporting tool outputs

### Engineer 4

- scoring
- ranking
- discard logic
- confidence and rationale
- test that outputs stay grounded across different LLM providers

---

## 9. Success Criteria

At the end of the hackathon, UrbanLens should:

- accept a selected locality from the frontend
- store the capture and metadata
- let the agent investigate the locality
- visibly call `ThermalGen`
- visibly call at least one supporting tool
- produce a credible answer to a useful locality question
- survive demo conditions with fallback paths

---

## 10. Final Rule

If the team gets pulled in too many directions, preserve only this:

- user selects a place
- agent investigates that place with visible tool calls
- `ThermalGen` appears as the custom superpower
- user gets a grounded answer

That is the winning slice.
