# Engineer 1
## Frontend, Capture UX, and Demo Surface

Owner:

- Google Maps integration
- locality selection UX
- screenshot/crop creation
- upload of image plus metadata
- sidebar UX
- trace playback UI
- ranking and recommendation UI
- follow-up question UI
- v0-assisted component polish

## Immediate Goal

Make the frontend capture and display the real product loop:

`select locality -> send capture -> render analysis -> ask follow-up`

## First Priorities

1. Render the map and region-selection UX.
2. Gather the structured metadata for the selected locality.
3. Produce the screenshot/crop that backend will analyze.
4. Send capture to:
   - `POST /analysis/from-capture-upload` preferred
   - `POST /analysis/from-capture` fallback
5. Poll:
   - `GET /analysis/{region_id}`
   - `GET /analysis/{region_id}/events`
6. Render:
   - visible trace
   - findings
   - recommendation
   - follow-up question UI

## What You Should Assume

- the backend analysis output is the main state object
- the trace is progressive and ordered
- planner questions only happen after an analysis exists

## What You Should Not Assume

- no chat-first product
- no session-first conversation UX as the hero
- no freeform provider-specific behavior from the backend

## What Must Be Obvious in the UI

- the selected locality
- that the frontend sent a real capture of that locality
- that the agent is calling tools
- that `ThermalGen` is one of those tools
- that a second supporting tool also exists
- that the final answer is actionable

## v0 Scope

Use `v0` to accelerate:

- sidebar shell
- trace timeline
- hotspot/result cards
- recommendation card
- follow-up question input

Do not let `v0` redefine the backend contract or the product flow.
