# Shared Contract

Source of truth is [contracts.md](C:/Users/akuma/repos/thermalgen/docs/contracts.md).

Everyone should follow these exact decisions.

## Analysis Model

- map click defines an `analysis region`
- region returns `3-5` hotspot candidates
- hotspots are investigated individually
- final output is a ranked list of survivors

## Hotspot Taxonomy

- `roof`
- `road_pavement`
- `parking_lot`
- `hvac_mechanical`
- `vegetation_loss`
- `other`

## Trace Vocabulary

- `candidate_detected`
- `inspect_object`
- `request_thermal_evidence`
- `infer_surface`
- `compare_neighbors`
- `check_consistency`
- `score_hotspot`
- `discard_hotspot`
- `finalize_hotspot`

## Trace Rules

- every hotspot starts with `candidate_detected`
- every hotspot passes through `inspect_object`
- every hotspot must request at least one extra evidence source
- `discard_hotspot` and `finalize_hotspot` are terminal
- route varies by hotspot type

## Ranking Heuristic

- anomaly filters
- severity orders
- confidence modulates

Gate:

```text
if anomaly_score < anomaly_threshold:
    discard
```

Ranking:

```text
final_rank_score = severity_score * confidence_score
```

## Caching

- cache is allowed
- visible reasoning must remain
- frontend should play back cached evidence as a 5-15 second investigation trace

## API Surface

- `POST /analysis`
- `GET /analysis/{region_id}`
- `GET /analysis/{region_id}/hotspots/{hotspot_id}`
- `GET /analysis/{region_id}/events` or equivalent polling

## UI Rule

The map is the anchor.

`v0` may be used for:

- sidebar shell
- trace timeline
- ranking cards
- recommendation card

`v0` may not redefine:

- schemas
- backend logic
- scoring
- map interaction contract
