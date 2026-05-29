# Shared Contract

Source of truth is [contracts.md](../docs/contracts.md).

Everyone should follow these exact decisions.

## Core Flow
Source of truth is [`docs/contracts.md`](../docs/contracts.md).

Everyone should follow these exact decisions.

## Naming Rule

- `ThermalGen` is the product: the agentic urban heat triage system.
- `hybrid_thermal` is the RGB-to-thermal model package used by the thermal evidence layer.
- Do not create or reference a separate `hybrid-thermal` package.
- Do not keep a root-level `HybridThermal/` project folder inside UrbanLens.

## Analysis Model

- user selects a locality in Google Maps
- frontend captures region metadata plus screenshot/crop
- backend stores the capture and creates an `analysis`
- user asks a question or triggers the default investigation path
- agent decides what tools to call
- agent investigates with visible trace
- agent returns a grounded answer and, when useful, ranked findings
- user can ask follow-up questions over the same analysis

## Product Rule

The product is the agent.

`ThermalGen` is the standout tool inside the product.

## Main Tool Set

- `generate_thermal_overlay`
- `request_thermal_evidence`
- `analyze_heat_risk`
- `inspect_object`
- `infer_surface`
- `compare_findings`
- `score_hotspots`
- `discard_hotspot`
- `finalize_recommendation`

## Trace Rule

- trace vocabulary is stable
- investigation path may vary by question
- `ThermalGen` should be visibly called in the golden path
- at least one supporting tool should also be visibly called

## API Rule

Canonical endpoints:

- `POST /analysis`
- `POST /analysis/from-capture`
- `POST /analysis/from-capture-upload`
- `GET /analysis/{region_id}`
- `GET /analysis/{region_id}/events`
- `GET /analysis/{region_id}/hotspots/{hotspot_id}`
- `POST /analysis/{region_id}/questions`

Experimental branches may contain a `session` API.

For the current product and frontend integration, that API is not canonical.
Treat it as exploratory unless the team explicitly decides to switch.

## LLM Rule

- use `LLMProvider`
- default to Anthropic for demo reliability
- support Featherless through the same interface
- do not hardcode Gemini-only assumptions into the product

## Voice Rule

- `ElevenLabs` is optional and downstream
- voice should read grounded analysis output
- voice must never become the primary product interaction

## UI Rule

The map is the anchor.

Planner Mode is a question layer over an existing analysis, not the entry point.

`v0` may help with:

- sidebar
- trace timeline
- ranking cards
- recommendation card
- follow-up question UI
