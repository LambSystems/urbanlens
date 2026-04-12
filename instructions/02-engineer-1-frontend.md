# Engineer 1
## Frontend and Demo UX

Owner:

- React + TypeScript app shell
- Google Maps integration
- sidebar UX
- trace rendering
- ranking and recommendation UI
- v0-assisted component polish

## Immediate Goal

Render the full product flow from mocked backend data as fast as possible.

Do not wait for real ML or real scoring.

## First Hour

1. Set up app shell and Google Maps container.
2. Support click-to-select analysis region visually.
3. Build sidebar skeleton.
4. Build trace timeline skeleton.
5. Build Top 3 ranking cards.
6. Build recommendation card.
7. Use `v0` to accelerate:
   - sidebar layout
   - trace timeline
   - ranking cards
   - recommendation card

## Inputs Expected from Backend

- `AnalysisRegion`
- `HotspotCandidate`
- `TraceStep`
- `AnalysisResult`

Use the exact field names from [contracts.md](C:/Users/akuma/repos/thermalgen/docs/contracts.md).

## Must Show

- analysis region around click
- 3-5 hotspot markers
- selected hotspot detail
- evidence-used badges
- source coverage indicator when available
- trace playback states:
  - `pending`
  - `running`
  - `completed`
- discarded hotspot state
- Top 3 ranking
- final recommendation

## Success Condition

If backend returns a valid mock payload, the app should already look like the final product.
