# Urban Legend Build Specs

This folder is the implementation guide for the 21-hour hackathon build.

Read these in order:

1. `00-overview.md`
2. `01-shared-contract.md`
3. your engineer-specific file

Core rule:

`user prompt -> agent investigates with visible chain of thought -> actionable answer`

If work does not improve that flow, cut it.

Primary target:

- `Best in Agentic AI`

Secondary target:

- `Best Design using v0`

Stack:

- Gemini (primary LLM, other Google products as needed)
- Google Maps API
- Python + FastAPI
- React + TypeScript
- v0 for selected UI surfaces only

Known assets:

- satellite-to-thermal conversion model already exists
- `hybrid_thermal` RGB-to-thermal model already exists as the thermal evidence generator
- datasets already exist, though Saint Louis-specific data is still under research
- real evidence is expected to come from scattered drone imagery, not a perfectly tiled map source

## ThermalGen Owner Scope

If you are working on ThermalGen, your scope is the product integration layer around the model:

- keep `ThermalGen` framed as the agentic triage system
- expose `hybrid_thermal` as a thermal evidence tool, not as the whole product
- make sure RGB inputs can produce thermal predictions reliably for the demo
- return thermal outputs in the shared backend schema
- support candidate discovery, thermal evidence requests, and hotspot scoring with usable thermal cues
- keep datasets, checkpoints, and generated predictions local/ignored unless explicitly approved for sharing

Out of scope for the ThermalGen owner during the hackathon:

- retraining the model unless inference is blocked
- broad model research or architecture redesign
- redistributing the private dataset/checkpoints
- expanding beyond the one-region demo loop before the core trace/ranking flow is stable

Non-negotiables:

- the user's prompt drives the investigation, not a fixed pipeline
- chain of thought is fully visible in the UI — every reasoning step and tool call
- Google Maps is the UI layer, not the ground-truth evidence layer
- the agent adapts its tool usage based on what the user asked
- follow-up questions work in the same session
- anomaly gates, severity orders, confidence modulates
- at least one hotspot rejected with evidence-backed reasoning

Do not reopen product-scope debates during implementation unless something blocks the core flow.
