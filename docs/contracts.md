# ThermalGen V2 Contracts
## Trace, Caching, and Backend/Frontend Schema

This document defines the operating contract for the MVP so all engineers can work in parallel without drift.

It is the source of truth for:

- analysis region behavior
- source retrieval and evidence normalization behavior
- source record requirements and fallback enrichment
- hotspot taxonomy
- trace semantics
- ranking and discard heuristics
- caching behavior
- backend/frontend data contracts
- the UI boundaries where `v0` can be used safely

---

## 1. Analysis Region

The user does not analyze a single structure directly.

A click on the map defines an `analysis region` centered around that click. The system then proposes multiple hotspot candidates inside that region.

Google Maps is the interaction surface. The evidence layer underneath may consist of scattered drone imagery, cropped images, and partial metadata.

Required behavior:

- click on map
- derive region center and radius
- load or create an analysis job
- retrieve available drone sources intersecting the region
- normalize source evidence into an analysis-ready representation
- detect 3 to 5 hotspot candidates
- investigate candidates individually
- discard or finalize each candidate
- return a ranked list of survivors

Recommended MVP fields:

- `center.lat`
- `center.lng`
- `radius_m`
- `region_id`
- `available_source_count`
- `coverage_score`

## 1.1 Source Retrieval Model

The backend should assume source imagery is scattered.

That means:

- not every region will have perfect coverage
- source imagery may come from multiple files or partial crops
- confidence should reflect coverage quality

For the MVP, source retrieval can be implemented as a curated mapping for known demo regions, but the contract should already model:

- source count
- coverage quality
- whether evidence is partial

## 1.2 Source Record Contract

Every raw source should be able to enter the system even if metadata is incomplete.

Recommended minimum source contract:

- `source_id`
- `source_type`
  one of `drone`, `satellite`, `derived`
- `image_path` or `image_url`
- `lat` optional
- `lng` optional
- `bounds` optional
- `timestamp` optional
- `altitude` optional
- `heading` optional
- `resolution` optional
- `metadata_quality_score`
- `geolocation_confidence`

Rule:

- missing metadata should reduce confidence, not break the pipeline

## 1.3 Google Maps Enrichment Fallback

Google Maps may be used to enrich missing or weak metadata when the source record is incomplete.

Allowed fallback uses:

- reverse geocoding
- viewport and bounds support
- approximate place or area labeling
- contextual metadata enrichment

Not allowed:

- treating Google Maps as primary thermal evidence
- replacing missing drone evidence with fake hotspot truth

Fallback order:

1. source record metadata
2. dataset-level metadata
3. Google Maps enrichment
4. confidence penalty if uncertainty remains

---

## 2. Hotspot Taxonomy

The MVP uses a small, explicit taxonomy:

- `roof`
- `road_pavement`
- `parking_lot`
- `hvac_mechanical`
- `vegetation_loss`
- `other`

Rules:

- use the most specific known label
- use `other` only as a fallback
- UI and ranking logic must not depend on a larger taxonomy

---

## 3. Trace Design

The trace must feel agentic without becoming unpredictable.

So:

- the `trace vocabulary` is fixed
- the `trace route` is semivariable
- not every hotspot uses every step

### 3.1 Fixed Trace Vocabulary

- `candidate_detected`
- `inspect_object`
- `request_thermal_evidence`
- `infer_surface`
- `compare_neighbors`
- `check_consistency`
- `score_hotspot`
- `discard_hotspot`
- `finalize_hotspot`

### 3.2 Trace Rules

- every hotspot starts with `candidate_detected`
- every hotspot must pass through `inspect_object`
- every hotspot should request at least one additional evidence source before being finalized or discarded
- `discard_hotspot` and `finalize_hotspot` are terminal
- traces should be short and legible in UI

### 3.3 Example Trace Templates

`road_pavement`

- `candidate_detected`
- `inspect_object`
- `request_thermal_evidence`
- `compare_neighbors`
- `score_hotspot`
- `discard_hotspot`

`roof`

- `candidate_detected`
- `inspect_object`
- `request_thermal_evidence`
- `infer_surface`
- `compare_neighbors`
- `check_consistency`
- `score_hotspot`
- `finalize_hotspot`

`hvac_mechanical`

- `candidate_detected`
- `inspect_object`
- `request_thermal_evidence`
- `infer_surface`
- `score_hotspot`
- `finalize_hotspot`

---

## 4. Discarded vs Top Hotspot

These terms must be implemented consistently across backend, scoring, and UI.

### 4.1 Discarded Hotspot

A discarded hotspot is a candidate that is not worth acting on first.

It usually fails because:

- anomaly is too low relative to local context
- the heat pattern is expected for the object type
- evidence is insufficient to justify escalation
- confidence is too low to recommend action
- source coverage is too incomplete to support escalation

Discard labels must be evidence-backed, not decorative.

Examples:

- expected road heat profile
- not hotter than nearby comparable roofs
- low-confidence signal after investigation

### 4.2 Top Hotspot

A top hotspot is a candidate that:

- passes the anomaly gate
- remains severe enough to matter
- retains enough confidence to support a recommendation
- is backed by adequate enough source coverage for the recommendation strength

Top hotspots appear in the final ranked list and receive an intervention recommendation.

---

## 5. Ranking Heuristic

The ranking philosophy is:

`anomaly filters`

`severity orders`

`confidence modulates and validates`

### 5.1 Gate

First apply an anomaly threshold:

```text
if anomaly_score < anomaly_threshold:
    discard
```

This is the structural filter.

### 5.2 Ranking

For survivors, rank primarily by severity with confidence modulation:

```text
final_rank_score = severity_score * confidence_score
```

This preserves the intended hierarchy:

- anomaly decides whether the hotspot deserves attention
- severity determines how urgent it is
- confidence prevents unstable results from dominating

Confidence should combine:

- model or reasoning confidence
- context consistency
- source coverage quality
- metadata completeness and geolocation confidence

### 5.3 Notes

- anomaly is still stored and shown in UI
- anomaly is still part of explanation
- severity is the primary ordering signal after gating

---

## 6. Caching Model

The system should feel alive for 5 to 15 seconds even when using cached or precomputed evidence.

Caching exists to improve stability and speed, not to remove the investigation experience.

### 6.1 Region Cache

Stores:

- nearby repeated analysis regions
- region metadata
- candidate hotspot proposals
- source retrieval results

Use case:

- repeated clicks near the same area

### 6.2 Hotspot Evidence Cache

Stores per hotspot:

- thermal evidence
- object classification
- surface or material inference
- neighbor comparison
- consistency check outputs
- scoring outputs
- source coverage summaries

Use case:

- replaying a known hotspot investigation quickly and reliably

### 6.3 Trace Playback Layer

Even when evidence is cached, the frontend should reveal it step by step.

This preserves:

- perceived reasoning
- demo clarity
- visible agent behavior

Recommended behavior:

- total playback time: 5 to 15 seconds
- each step transitions through `pending -> running -> completed`
- terminal step becomes `discard_hotspot` or `finalize_hotspot`

---

## 7. State Model

Recommended hotspot states:

- `candidate`
- `investigating`
- `evidence_gathered`
- `discarded`
- `finalized`

Rules:

- `discarded` is terminal
- `finalized` is terminal
- a hotspot cannot be both discarded and finalized

---

## 8. Backend/Frontend Schema

These schemas are intentionally compact and stable.

### 8.1 AnalysisRegion

```json
{
  "region_id": "stl_001",
  "center": {"lat": 38.6270, "lng": -90.1994},
  "radius_m": 120,
  "available_source_count": 6,
  "coverage_score": 0.81,
  "status": "running",
  "summary": {
    "candidate_count": 5,
    "discarded_count": 2,
    "finalized_count": 3
  }
}
```

### 8.1.1 SourceRecord

```json
{
  "source_id": "drone_img_001",
  "source_type": "drone",
  "image_path": "data/demo/drone_img_001.png",
  "lat": 38.6271,
  "lng": -90.1992,
  "bounds": null,
  "timestamp": null,
  "altitude": 110.0,
  "heading": null,
  "resolution": 0.12,
  "metadata_quality_score": 0.72,
  "geolocation_confidence": 0.68
}
```

### 8.2 HotspotCandidate

```json
{
  "hotspot_id": "hs_01",
  "region_id": "stl_001",
  "bbox": {"x": 120, "y": 80, "w": 60, "h": 44},
  "centroid": {"lat": 38.6271, "lng": -90.1991},
  "hotspot_type": "roof",
  "status": "investigating",
  "source_count": 3,
  "coverage_score": 0.79,
  "anomaly_score": 0.82,
  "severity_score": 0.76,
  "confidence_score": 0.71,
  "final_rank_score": null,
  "discard_reason": null,
  "recommended_action": null,
  "why": []
}
```

### 8.3 TraceStep

```json
{
  "step_id": "step_03",
  "hotspot_id": "hs_01",
  "kind": "compare_neighbors",
  "status": "completed",
  "started_at": "2026-04-11T18:10:12Z",
  "completed_at": "2026-04-11T18:10:14Z",
  "summary": "Hotter than 83% of nearby comparable roofs",
  "evidence": {
    "neighbor_count": 12,
    "relative_percentile": 0.83,
    "coverage_score": 0.79
  }
}
```

### 8.4 AnalysisResult

```json
{
  "region_id": "stl_001",
  "status": "completed",
  "hotspots": [],
  "top_hotspots": [
    {
      "hotspot_id": "hs_01",
      "priority_rank": 1,
      "hotspot_type": "roof",
      "recommended_action": "cool-roof retrofit",
      "why": [
        "high relative anomaly vs nearby roofs",
        "large exposed dark surface",
        "high-confidence thermal evidence"
      ]
    }
  ]
}
```

---

## 9. v0 Implementation Boundary

`v0` should be used to accelerate visual implementation, not to define application logic.

Safe `v0` scope:

- sidebar shell
- hotspot detail panel
- investigation trace timeline
- Top 3 ranking cards
- final recommendation card
- loading and empty states

Not `v0` scope:

- backend orchestration logic
- hotspot scoring rules
- trace semantics
- map event handling contract
- caching logic

Implementation approach:

1. Define schema and UI state contracts first in this document.
2. Use `v0` prompts to generate UI components against those fixed contracts.
3. Adapt the generated React/TypeScript output into the app without renaming schema fields to fit the UI.
4. Prefer `v0` for component structure, styling, and layout polish.
5. Keep the Google Maps container and analysis state management under direct engineer control.

Suggested `v0` prompt targets:

- a right sidebar for hotspot analysis with status badges and evidence sections
- a vertical trace timeline with running, completed, discarded, and finalized states
- ranked hotspot cards with anomaly, severity, and confidence badges
- a recommendation card for the top hotspot with action, rationale, and confidence

Success criteria for `v0` usage:

- the UI is visibly cleaner and more legible than a hand-built default dashboard
- the map remains the visual anchor
- the trace and recommendation are understandable in under 10 seconds
- generated components integrate cleanly with React and TypeScript

---

## 10. API Surface

Keep the backend surface small.

Recommended endpoints:

- `POST /analysis`
  create an analysis job for a clicked region
- `GET /analysis/{region_id}`
  fetch aggregated state
- `GET /analysis/{region_id}/hotspots/{hotspot_id}`
  fetch hotspot details for the sidebar
- `GET /analysis/{region_id}/events`
  fetch trace progress, or replace with polling on the main analysis payload

---

## 11. Implementation Rule

If anything is ambiguous during implementation, preserve these first:

- fixed trace vocabulary
- semivariable trace routes
- region-level source retrieval before hotspot reasoning
- partial metadata is acceptable
- Google Maps enrichment is fallback-only
- anomaly as gate
- severity for ordering
- confidence for modulation
- visible playback over cached evidence

That is the contract that keeps the product coherent.
