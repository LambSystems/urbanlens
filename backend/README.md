# ThermalGen Backend

FastAPI backend scaffold for the hackathon MVP.

## Run

```bash
uvicorn app.main:app --reload
```

If running from `backend/`:

```bash
uvicorn app.main:app --reload
```

If running from repo root:

```bash
uvicorn backend.app.main:app --reload
```

## ThermalGen Tool Endpoint

The current tool path is RGB-only. Google Maps/location context is passed as metadata for downstream agent reasoning. No dataset is required for live inference; only the checkpoints under `backend/models/hybrid_thermal/checkpoints/` are needed.

Runtime inference still preprocesses the single submitted image: open RGB, center-crop/align, resize to `512x640`, normalize, run the checkpoint, then save both a grayscale thermal output and an autocontrasted orange preview. Teammates do not need to run the old dataset preprocessing scripts for app usage.

For a repo-local image path:

```bash
curl -X POST http://localhost:8000/thermal/infer/path \
  -H "Content-Type: application/json" \
  -d "{\"image_path\":\"backend/data/hybrid_thermal/uploads/map-capture.png\",\"metadata\":{\"center\":{\"lat\":38.627,\"lng\":-90.1994}}}"
```

For a frontend map capture, send the image bytes directly to:

```text
POST /thermal/infer/upload?lat=38.627&lng=-90.1994&radius_m=120
```

The backend stores the upload locally, runs ThermalGen, and returns `thermal_image_url`, `thermal_preview_url`, hotspot regions, and metadata for the agent.
