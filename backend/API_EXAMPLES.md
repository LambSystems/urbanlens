# ThermalGen API Examples

Use these examples to connect the frontend and inspect backend behavior quickly.

Base URL examples assume local development:

```text
http://localhost:8000
```

## 1. Healthcheck

```http
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

## 2. Get Demo Regions

Use this to populate initial clickable demo choices before real map exploration is ready.

```http
GET /demo/regions
```

Example response:

```json
{
  "regions": [
    {
      "label": "downtown_core",
      "lat": 38.627,
      "lng": -90.1994,
      "radius_m": 120
    },
    {
      "label": "industrial_corridor",
      "lat": 38.6155,
      "lng": -90.2152,
      "radius_m": 140
    },
    {
      "label": "campus_zone",
      "lat": 38.6483,
      "lng": -90.3108,
      "radius_m": 110
    }
  ]
}
```

## 3. Get Example Analysis Request

```http
GET /demo/example-analysis-request
```

Example response:

```json
{
  "center": {
    "lat": 38.627,
    "lng": -90.1994
  },
  "radius_m": 120
}
```

## 4. Create Analysis

```http
POST /analysis
Content-Type: application/json
```

Request body:

```json
{
  "center": {
    "lat": 38.627,
    "lng": -90.1994
  },
  "radius_m": 120
}
```

Example response shape:

```json
{
  "region": {
    "region_id": "region_ab12cd34",
    "center": {
      "lat": 38.627,
      "lng": -90.1994
    },
    "radius_m": 120,
    "bounds": {
      "north": 38.628081,
      "south": 38.625919,
      "east": -90.198016,
      "west": -90.200784
    },
    "area_km2": 0.058,
    "available_source_count": 3,
    "coverage_score": 0.65,
    "maps_fallback_count": 1,
    "enrichment_confidence_avg": 0.77,
    "source_records": [
      {
        "source_id": "drone_img_001",
        "source_type": "drone",
        "image_path": "data/demo/drone_img_001.png",
        "image_url": null,
        "lat": 38.6274,
        "lng": -90.1991,
        "bounds": null,
        "timestamp": null,
        "altitude": 110.0,
        "heading": null,
        "resolution": 0.12,
        "metadata_quality_score": 0.82,
        "geolocation_confidence": 0.78
      },
      {
        "source_id": "drone_img_002",
        "source_type": "drone",
        "image_path": "data/demo/drone_img_002.png",
        "image_url": null,
        "lat": null,
        "lng": null,
        "bounds": null,
        "timestamp": null,
        "altitude": 95.0,
        "heading": null,
        "resolution": 0.18,
        "metadata_quality_score": 0.48,
        "geolocation_confidence": 0.35
      },
      {
        "source_id": "derived_thermal_001",
        "source_type": "derived",
        "image_path": "data/demo/thermal_overlay_001.png",
        "image_url": null,
        "lat": 38.6272,
        "lng": -90.1996,
        "bounds": null,
        "timestamp": null,
        "altitude": null,
        "heading": null,
        "resolution": null,
        "metadata_quality_score": 0.75,
        "geolocation_confidence": 0.72
      }
    ],
    "status": "running",
    "summary": {
      "candidate_count": 4,
      "discarded_count": 1,
      "finalized_count": 3
    }
  },
  "result": {
    "region_id": "region_ab12cd34",
    "status": "running",
    "hotspots": [],
    "top_hotspots": [],
    "top_hotspot_id": null,
    "discarded_hotspot_ids": []
  }
}
```

Important:

- The first response may still be `running`
- The frontend should poll after receiving `region_id`

## 5. Poll Analysis State

```http
GET /analysis/{region_id}
```

Use this to fetch the main product state:

- region summary
- hotspot list
- trace step states
- ranked hotspots
- source and coverage context for the selected region

Example:

```http
GET /analysis/region_ab12cd34
```

## 6. Get Hotspot Detail

```http
GET /analysis/{region_id}/hotspots/{hotspot_id}
```

Example:

```http
GET /analysis/region_ab12cd34/hotspots/hs_01
```

Use this for:

- sidebar detail view
- selected hotspot inspection
- recommendation detail

Example hotspot detail shape:

```json
{
  "hotspot_id": "hs_01",
  "region_id": "region_ab12cd34",
  "bbox": {"x": 112, "y": 78, "w": 64, "h": 48},
  "centroid": {"lat": 38.6277, "lng": -90.1989},
  "hotspot_type": "roof",
  "display_name": "Building Roof",
  "status": "investigating",
  "surface_temperature_c": 54.0,
  "ambient_delta_c": 16.0,
  "source_count": 3,
  "coverage_score": 0.79,
  "anomaly_score": 0.82,
  "severity_score": 0.76,
  "confidence_score": 0.71,
  "final_rank_score": 0.5396,
  "discard_reason": null,
  "recommended_action": "cool-roof retrofit",
  "evidence_urls": ["/evidence/hs_01-thermal.jpg", "/evidence/hs_01-visual.jpg"],
  "priority_rank": 1,
  "is_top_ranked": true,
  "created_at": "2026-04-11T13:10:00Z",
  "updated_at": "2026-04-11T13:10:05Z",
  "why": [
    "high relative anomaly vs nearby roofs",
    "large exposed dark surface",
    "high-confidence thermal evidence"
  ],
  "trace": []
}
```

## 7. Poll Trace Events

```http
GET /analysis/{region_id}/events
```

Example response shape:

```json
[
  {
    "region_id": "region_ab12cd34",
    "hotspot_id": "hs_01",
    "step_id": "hs_01_step_01",
    "kind": "candidate_detected",
    "status": "completed",
    "timestamp_ms": 0,
    "summary": "Candidate hotspot detected in analysis region.",
    "details": {},
    "scheduled_offset_ms": 0
  },
  {
    "region_id": "region_ab12cd34",
    "hotspot_id": "hs_01",
    "step_id": "hs_01_step_02",
    "kind": "inspect_object",
    "status": "running",
    "timestamp_ms": 1200,
    "summary": "Object inspection suggests a roof structure.",
    "details": {
      "object_confidence": 0.66,
      "object_label": "roof",
      "source_count": 4,
      "coverage_score": 0.86
    },
    "scheduled_offset_ms": 1200
  }
]
```

Use this for:

- timeline playback
- step-by-step animation
- loading progress

## 8. Debug View

```http
GET /analysis/{region_id}/debug
```

Use this only for development. It exposes:

- trace kinds by hotspot
- scoring and discard details
- perception/scoring adapters
- ranking formula and anomaly threshold
- source-aware confidence context

## 9. Planner Mode Question

Use this after an analysis already exists.

```http
POST /analysis/{region_id}/questions
Content-Type: application/json
```

Request body:

```json
{
  "question": "What should we fix first here?"
}
```

Example response:

```json
{
  "region_id": "region_ab12cd34",
  "question": "What should we fix first here?",
  "answer": "You should prioritize hs_01 first. It is a roof hotspot with anomaly 0.83, severity 0.78, confidence 0.90, and the recommended action is cool-roof retrofit.",
  "referenced_hotspot_ids": ["hs_01"],
  "planner_mode": "analysis_qa"
}
```

## 10. Suggested Frontend Flow

1. Load `GET /demo/regions` or let the user click on the map.
2. Optionally use `GET /demo/example-analysis-request` for a ready-made request body.
3. Call `POST /analysis`.
4. Store `region_id`.
5. Poll `GET /analysis/{region_id}` every 800 to 1200 ms.
6. Poll `GET /analysis/{region_id}/events` if a separate trace feed is useful.
7. Fetch `GET /analysis/{region_id}/hotspots/{hotspot_id}` when the user clicks a hotspot.
8. Once analysis exists, optionally call `POST /analysis/{region_id}/questions` for Planner Mode.

## 11. Minimal cURL Examples

Create analysis:

```bash
curl -X POST "http://localhost:8000/analysis" ^
  -H "Content-Type: application/json" ^
  -d "{\"center\":{\"lat\":38.627,\"lng\":-90.1994},\"radius_m\":120}"
```

Get analysis:

```bash
curl "http://localhost:8000/analysis/region_ab12cd34"
```

Get events:

```bash
curl "http://localhost:8000/analysis/region_ab12cd34/events"
```

Get debug view:

```bash
curl "http://localhost:8000/analysis/region_ab12cd34/debug"
```

Ask planner question:

```bash
curl -X POST "http://localhost:8000/analysis/region_ab12cd34/questions" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"What should we fix first here?\"}"
```
