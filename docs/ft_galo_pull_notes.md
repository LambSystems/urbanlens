# Pull Notes For `ft-galo`

Use this when pulling `ft-galo` into another branch. It summarizes the important app behavior changes and the local setup assumptions.

## Main Change

The product path is now capture-first:

```text
frontend rectangle selection
-> normalize selected bounds to the ThermalGen 640 x 512 aspect ratio
-> capture a 640 x 512 Google Static Maps image
-> POST /analysis/from-capture-upload
-> backend stores files under backend/data/captures/{region_id}/
-> HybridThermalGen runs on the captured source image
-> backend maps thermal hotspot pixels into the exact capture bounds
-> frontend renders region.thermal_preview_url as a GroundOverlay
```

The invariant to preserve is:

```text
source image bounds == thermal preview bounds == overlay bounds == hotspot pixel-to-geo bounds
```

Breaking that invariant is what causes thermal overlays to stretch or hotspots to drift away from the bright thermal areas.

## What Changed

- The frontend no longer depends on `frontend/lib/mock-data`.
- The map now uses a fixed default center instead of a demo region object.
- User rectangle selections are normalized to the model aspect ratio before capture.
- The frontend sends `imageBounds` with capture metadata.
- The backend stores source image dimensions, file size, aligned RGB dimensions, and thermal preview dimensions on the analysis region.
- ThermalGen output is resized back to the source snippet size for preview, but hotspot extraction stays in model space.
- Hotspot markers are anchored to the brightest pixel inside each connected hot thermal region.
- Thermal hotspot ranking uses `brightness_score`, weighted toward peak brightness while still considering mean brightness and area.
- Synthetic/static thermal fallback datasets were removed from the product path.
- If ThermalGen cannot run, the backend returns no hotspot regions and reports the error instead of inventing fake hotspots.
- Tracked `__pycache__` files were removed from Git; keep them ignored.

## Important Files

```text
frontend/components/thermal-map.tsx
frontend/lib/thermal-context.tsx
frontend/lib/api.ts
backend/app/store.py
backend/app/capture_pipeline.py
backend/app/thermal/generator.py
backend/app/thermal/hybrid_thermal/runtime.py
backend/app/perception/candidate_discovery.py
docs/thermalgen_tool.md
docs/thermalgen_handoff.md
instructions/backend-handoff-codex-frontend-align.md
```

## Local Assets Needed

Datasets are not required for the app flow. Checkpoints are required for real inference:

```text
backend/models/hybrid_thermal/checkpoints/best_psnr.pth
backend/models/hybrid_thermal/checkpoints/best_loss.pth
backend/models/hybrid_thermal/checkpoints/latest.pth
```

If teammates only have `.gitkeep` in that folder, ThermalGen will not produce real thermal predictions.

## Runtime Files

The app writes generated files locally. These should stay ignored:

```text
backend/data/captures/{region_id}/source.png
backend/data/captures/{region_id}/metadata.json
backend/data/captures/{region_id}/source_aligned.png
backend/data/captures/{region_id}/source_thermal.png
backend/data/captures/{region_id}/source_thermal_preview.png
backend/data/hybrid_thermal/uploads/
backend/data/hybrid_thermal/Predict_Thermal/
backend/data/hybrid_thermal/Test_RGB_centercrop_640x512/
```

## API Contract

Frontend should prefer:

```text
POST /analysis/from-capture-upload
GET /analysis/{region_id}
GET /analysis/{region_id}/events
POST /analysis/{region_id}/questions
```

Avoid calling `/thermal/infer/upload` separately from the main frontend flow. The analysis endpoint already stores the capture, runs ThermalGen, builds hotspot candidates, and returns thermal preview URLs.

## Agentic Notes

The canonical frontend-facing flow is still the `analysis` flow. Session routes can exist as an optional agentic sidecar, but teammates should not replace the app path with session-first behavior unless the frontend contract is updated too.

Planner answers should use the existing analysis context:

```text
thermal preview
hotspots
rank scores
evidence highlights
recommended actions
question text
```

The LLM should reason over that context after analysis exists. It should not be the first component to trigger ThermalGen for the normal map-selection path.

## Things Not To Reintroduce

- `frontend/lib/mock-data`
- demo region API endpoints as product dependencies
- bundled sample image datasets under `backend/app/data`
- synthetic/static hotspot fallback regions
- tracked `__pycache__` or `.pyc` files
- duplicate frontend thermal inference calls in parallel with `/analysis/from-capture-upload`

## Known Follow-Ups

- Real checkpoints must be present locally for true ThermalGen results.
- Object/material labels are still rule-based until an object detector is integrated.
- Planner/tool calling can be improved, but it should consume the analysis output rather than bypassing it.
- UI should clearly show when ThermalGen evidence is unavailable because the checkpoint or image is missing.
