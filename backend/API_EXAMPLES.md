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

## 3. Create Analysis

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
    "top_hotspots": []
  }
}
```

Important:

- The first response may still be `running`
- The frontend should poll after receiving `region_id`

## 4. Poll Analysis State

```http
GET /analysis/{region_id}
```

Use this to fetch the main product state:

- region summary
- hotspot list
- trace step states
- ranked hotspots

Example:

```http
GET /analysis/region_ab12cd34
```

## 5. Get Hotspot Detail

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

## 6. Poll Trace Events

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
    "summary": "Candidate hotspot detected in analysis region.",
    "scheduled_offset_ms": 0
  },
  {
    "region_id": "region_ab12cd34",
    "hotspot_id": "hs_01",
    "step_id": "hs_01_step_02",
    "kind": "inspect_object",
    "status": "running",
    "summary": "Object inspection suggests a roof structure.",
    "scheduled_offset_ms": 1200
  }
]
```

Use this for:

- timeline playback
- step-by-step animation
- loading progress

## 7. Debug View

```http
GET /analysis/{region_id}/debug
```

Use this only for development. It exposes:

- trace kinds by hotspot
- scoring and discard details
- perception/scoring adapters
- ranking formula and anomaly threshold

## Suggested Frontend Flow

1. Load `GET /demo/regions` or let the user click on the map.
2. Call `POST /analysis`.
3. Store `region_id`.
4. Poll `GET /analysis/{region_id}` every 800 to 1200 ms.
5. Poll `GET /analysis/{region_id}/events` if a separate trace feed is useful.
6. Fetch `GET /analysis/{region_id}/hotspots/{hotspot_id}` when the user clicks a hotspot.

## Minimal cURL Examples

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
