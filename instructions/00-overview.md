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
- datasets already exist, though Saint Louis-specific data is still under research
- real evidence is expected to come from scattered drone imagery, not a perfectly tiled map source

Non-negotiables:

- the user's prompt drives the investigation, not a fixed pipeline
- chain of thought is fully visible in the UI — every reasoning step and tool call
- Google Maps is the UI layer, not the ground-truth evidence layer
- the agent adapts its tool usage based on what the user asked
- follow-up questions work in the same session
- anomaly gates, severity orders, confidence modulates
- at least one hotspot rejected with evidence-backed reasoning

Do not reopen product-scope debates during implementation unless something blocks the core flow.
