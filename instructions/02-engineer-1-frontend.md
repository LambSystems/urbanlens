# Engineer 1
## Frontend and Demo UX

Owner:

- React + TypeScript app shell
- Google Maps integration
- prompt input and conversation UI
- chain of thought display panel
- sidebar UX
- ranking and recommendation UI
- v0-assisted component polish

## Immediate Goal

Render the full product flow from mocked backend data as fast as possible.

Do not wait for real ML or real scoring.

## First Hour

1. Set up app shell and Google Maps container.
2. Support click-to-select analysis region visually.
3. Build prompt input field (text input + send).
4. Build chain of thought panel skeleton — shows steps streaming in.
5. Build conversation thread — shows prior prompts + answers.
6. Build Top 3 ranking cards.
7. Build recommendation card.
8. Use `v0` to accelerate:
   - prompt input + conversation thread
   - chain of thought timeline
   - ranking cards
   - recommendation card

## Inputs Expected from Backend

- `AnalysisRegion` (region loaded)
- `ChainOfThoughtStep` (streamed during investigation)
- `InvestigationResponse` (final answer + hotspots + recommendations)
- `HotspotCandidate` (hotspot details)

<<<<<<< Updated upstream
Use the exact field names from [contracts.md](/docs/contracts.md).
=======
Use the exact field names from [`docs/contracts.md`](../docs/contracts.md).
>>>>>>> Stashed changes

## Must Show

- analysis region around click
- prompt input field
- chain of thought panel with step types:
  - `reasoning` — text reasoning
  - `tool_call` — tool name + summary
  - `finding` — conclusion about a hotspot
  - `answer` — final response
- step status transitions: `pending -> running -> completed`
- conversation history (prompt + answer pairs)
- hotspot markers on map
- selected hotspot detail
- evidence-used badges
- source coverage indicator when available
- discarded hotspot state
- Top 3 ranking
- final recommendation

## Success Condition

If backend returns a valid mock payload, the app should already look like the final product — with visible chain of thought and conversation working.
