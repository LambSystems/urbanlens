# Engineer 2
## Backend and Orchestrator

Owner:

- FastAPI service
- schemas
- orchestrator state machine
- trace lifecycle
- cache/playback bridge
- analysis endpoints

## Immediate Goal

Expose the final-shaped API before the internals are real.

Your first win is not "AI works".

Your first win is:

- frontend can render the whole product from your API

## First Hour

1. Create backend project skeleton.
2. Create models for:
   - `AnalysisRegion`
   - `HotspotCandidate`
   - `TraceStep`
   - `AnalysisResult`
3. Implement:
   - `POST /analysis`
   - `GET /analysis/{region_id}`
   - `GET /analysis/{region_id}/hotspots/{hotspot_id}`
   - `GET /analysis/{region_id}/events` or equivalent
4. Return a fully mocked but contract-valid payload.
5. Implement hotspot states:
   - `candidate`
   - `investigating`
   - `evidence_gathered`
   - `discarded`
   - `finalized`

## Orchestrator Rules

The trace vocabulary is fixed.

Allowed steps:

- `candidate_detected`
- `inspect_object`
- `request_thermal_evidence`
- `infer_surface`
- `compare_neighbors`
- `check_consistency`
- `score_hotspot`
- `discard_hotspot`
- `finalize_hotspot`

Route is semivariable by hotspot type.

Example:

- `road_pavement`
  `candidate_detected -> inspect_object -> request_thermal_evidence -> compare_neighbors -> score_hotspot -> discard_hotspot`
- `roof`
  `candidate_detected -> inspect_object -> request_thermal_evidence -> infer_surface -> compare_neighbors -> check_consistency -> score_hotspot -> finalize_hotspot`

## Caching Rule

Cache is allowed, but the user must still experience a 5-15 second investigation.

That means:

- backend may serve cached evidence
- frontend still reveals steps progressively
- events or polling must expose step progression cleanly

## Handoffs

From Engineer 3 you need:

- hotspot evidence payloads

From Engineer 4 you need:

- scoring payloads or pure functions

To Engineer 1 you provide:

- stable API
- stable field names
- stable trace steps

## Success Condition

By hour 2, Engineer 1 should be using your real API, even if internals are still mostly mocked.
