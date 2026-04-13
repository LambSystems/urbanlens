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
- optional voice briefing playback UI

## Immediate Goal

Make the frontend capture and display the real product loop:

`select locality -> send capture -> render analysis -> ask follow-up`

This engineer needs the most guidance because UX can easily drift into the wrong product.

The hero interaction is not “open a chat and type anything.”

The hero interaction is:

1. select a locality on the map
2. analyze that exact place
3. watch the agent use tools
4. inspect the answer
5. optionally ask a targeted follow-up

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
7. If backend supports it, add a `Play briefing` button for ElevenLabs audio.

## UX Canon

Engineer 1 should follow this exact visual hierarchy:

### Primary Surface

- Google Maps capture view
- selected locality box or bounds
- `Analyze` button

### Secondary Surface

- analysis status
- trace timeline
- main recommendation
- ranked findings if available

### Tertiary Surface

- follow-up question input
- extra evidence details

If the UI makes the follow-up question box look like the main feature, it is pointing at the wrong product.

## What the Current Frontend Context Suggests

From the existing frontend work in `main` and `ft-galo`, the UI already wants:

- bounds and area display
- hotspot cards
- a trace timeline
- ranking output
- recommendation display

So the docs should keep Engineer 1 focused on:

- a strong map-first experience
- a very legible right sidebar
- capture/upload affordances
- analysis playback states

Not on inventing a brand-new conversational shell.

## What You Should Assume

- the backend analysis output is the main state object
- the trace is progressive and ordered
- planner questions only happen after an analysis exists
- the frontend may need an adapter layer over backend payloads
- upload UX should prefer `multipart/form-data` with a real image file

## What You Should Not Assume

- no chat-first product
- no session-first conversation UX as the hero
- no freeform provider-specific behavior from the backend
- no requirement to render every backend field directly
- no dependence on the experimental `session` API branch

## What Must Be Obvious in the UI

- the selected locality
- that the frontend sent a real capture of that locality
- that the agent is calling tools
- that `ThermalGen` is one of those tools
- that a second supporting tool also exists
- that the final answer is actionable
- that voice, if present, is a summary layer and not the core interaction

Recommended visible labels:

- `Thermal Evidence`
- `Heat Risk Profile`
- `Agent Reasoning`
- `Recommended Next Step`

These labels help judges understand the product in seconds.

## v0 Scope

Use `v0` to accelerate:

- sidebar shell
- trace timeline
- hotspot/result cards
- recommendation card
- follow-up question input

Do not let `v0` redefine the backend contract or the product flow.

## Success Condition

By the time Engineer 1 is done, a judge should understand the app without narration:

- this is a place-based analysis tool
- it captures a real locality
- the agent uses custom tools on that locality
- the answer is the point
