# UrbanLens Models
## Tool and Reasoning Stack After the Pivot

This document reflects the new best plan:

the product is an agent, and the models exist to support its tools.

The current stack should be explained as:

- one standout custom model or tool: `ThermalGen`
- one lighter supporting analysis tool: `Heat Risk Profiler`
- small perception helpers
- deterministic scoring
- an LLM-driven orchestrator behind an `LLMProvider`

---

## 1. Model Philosophy

Do not build a pile of disconnected models.

The strongest version is:

- a small number of clear internal tools
- one unique tool nobody else has
- one supporting tool that broadens the product story
- deterministic ranking and recommendations
- a provider-neutral orchestrator

The models produce evidence.
The agent decides what to do with that evidence.

---

## 2. Core Tool Stack

## 2.1 ThermalGen

This is the signature tool.

Purpose:

- generate thermal evidence from a captured map image
- support thermal overlay and hotspot analysis
- provide differentiated capability for the agent

ThermalGen is not the whole product, but it is the strongest technical differentiator.

## 2.2 Heat Risk Profiler

This is the recommended second tool.

Purpose:

- analyze a captured locality for visible heat-risk signals
- estimate likely drivers such as dark roofs, exposed pavement, low shade, or large surface exposure
- provide a second evidence stream the agent can compare against ThermalGen

This tool is allowed to be lighter and more heuristic than ThermalGen.

## 2.3 Perception Helpers

Useful but lightweight helpers:

- object typing
- coarse surface inference
- rooftop or paved-area inspection

These should stay narrow and legible.

---

## 3. Orchestrator Layer

The orchestrator should be LLM-assisted but not LLM-owned in every part.

Responsibilities:

- interpret the user question
- decide which internal tools to call
- sequence tool calls
- summarize tool outputs
- answer follow-up questions

Keep hard logic outside the LLM where possible.

---

## 4. LLM Provider

Use a provider abstraction.

Recommended providers:

- `AnthropicProvider` as current default
- `GeminiProvider` as optional or fallback
- `FeatherlessProvider` as an open-model provider path
- `MockProvider` for tests and demo fallback

The project should not fail just because one vendor is unstable.

The LLM should mainly help with:

- tool choice reasoning
- explanation wording
- analysis follow-up questions

The LLM should not own:

- ranking math
- anomaly/severity/confidence calculations
- final deterministic sorting

Recommended operating rule:

- `AnthropicProvider` should be the safe demo default
- `FeatherlessProvider` should be implemented against the same interface so the team can credibly claim and test sponsor integration
- `GeminiProvider` should remain optional until it is reliable

## 4.1 Voice Output Layer

Voice does not belong inside `LLMProvider`.

Treat voice separately as a downstream output system.

Recommended provider:

- `ElevenLabs`

Best use:

- convert the final answer into a short decision briefing
- keep the audio layer small and deterministic

---

## 5. What Should Stay Deterministic

Keep these deterministic:

- ranking
- discard logic
- confidence modulation
- hotspot ordering
- recommendation strength

Recommended scoring rule:

- anomaly gates
- severity orders
- confidence modulates

That makes the system easier to defend and easier to demo.

---

## 6. Recommended Investigation Pattern

For the strongest demo path, the agent should look like this:

1. see the selected locality and question
2. decide whether thermal evidence is needed
3. call `ThermalGen`
4. call `Heat Risk Profiler`
5. optionally inspect objects or surfaces
6. reconcile findings
7. rank or explain
8. answer

This gives you visible, believable tool-calling without too much chaos.

---

## 7. Final Rule

If you are deciding whether to add another model, the answer is probably no.

Prefer to strengthen:

- the usefulness of `ThermalGen`
- the clarity of `Heat Risk Profiler`
- the legibility of the orchestrator trace
- the stability of the deterministic scoring layer

That is the most convincing stack for the hackathon.
