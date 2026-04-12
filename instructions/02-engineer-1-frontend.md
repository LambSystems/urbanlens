# Engineer 1
## Frontend and Demo UX

Owner:

- React + TypeScript app shell
- Google Maps integration
- region selection UX
- sidebar UX
- ranking and recommendation UI
- trace playback UI
- planner question input after analysis
- v0-assisted component polish

## Immediate Goal

Render the real hackathon product flow from the backend analysis API as fast as possible.

Do not wait for real ML or perfect datasets.

Use the adapter in [frontend/lib/api.ts](/C:/Users/akuma/repos/thermalgen/frontend/lib/api.ts) as the bridge from backend payloads to frontend UI types.

## First Hour

1. Set up app shell and Google Maps container.
2. Support click-to-select analysis region visually.
3. Convert selected bounds into backend `center + radius_m`.
4. Call `POST /analysis`.
5. Poll `GET /analysis/{region_id}`.
6. Render hotspot markers, ranking cards, recommendation card, and trace timeline.
7. Add planner question input for `POST /analysis/{region_id}/questions`.
8. Use `v0` to accelerate:
   - sidebar
   - ranking cards
   - recommendation card
   - trace timeline

## Inputs Expected from Backend

- `AnalysisResponse`
- `HotspotCandidate`
- `AnalysisEvent`
- `PlannerQuestionResponse`

Canonical endpoints:

- `POST /analysis`
- `GET /analysis/{region_id}`
- `GET /analysis/{region_id}/hotspots/{hotspot_id}`
- `GET /analysis/{region_id}/events`
- `POST /analysis/{region_id}/questions`

## Must Show

- analysis region around click
- map markers for hotspots
- selected hotspot detail
- trace playback with step status `pending -> running -> completed`
- discarded hotspot state
- Top 3 ranking
- final recommendation
- source coverage indicator when available
- planner question input after analysis completes

## Must Not Assume

- no chat session API
- no chain-of-thought text stream as the primary product
- no freeform conversation thread as the main interaction model

Planner Mode is a question layer on top of an existing analysis, not the main entry point.

## Success Condition

If backend returns a valid analysis payload, the app should already look like the final product:

- region selected
- analysis running
- hotspots ranked
- trace inspectable
- recommendation visible
- planner question answering over the selected region
