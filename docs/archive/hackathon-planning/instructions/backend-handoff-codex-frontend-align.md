# Frontend Align Merge Handoff

This note records what was kept from `origin/codex/frontend-align` and how it fits the current `ft-galo` app flow.

## Decision

The useful work from `codex/frontend-align` is the map/capture alignment logic. I kept that direction and merged it with the current ThermalGen backend path.

Canonical app flow remains:

```text
frontend rectangle selection
-> normalize selected bounds to 640 x 512 model aspect ratio
-> capture a Google Static Maps image at 640 x 512
-> POST /analysis/from-capture-upload
-> backend stores capture files under backend/data/captures/{region_id}/
-> HybridThermalGen runs on the captured source image
-> backend maps model-space hotspot pixels into the exact capture bounds
-> frontend overlays region.thermal_preview_url using the same capture bounds
```

## What Was Kept

- `analysis` remains the frontend-facing API contract.
- `session` remains optional/agentic sidecar behavior.
- The capture upload pipeline remains the main integration point.
- Provider-neutral LLM files stay in place.
- Planner responses stay structured for the UI.
- Voice briefing stays optional.
- The frontend now normalizes rectangle selections to the model aspect ratio before capture.
- The frontend calculates a Static Maps zoom that fits the selected model-safe region.

## What Was Rejected Or Corrected

- Do not use `frontend/lib/mock-data` or `DEMO_REGION` for the product path.
- Do not carry `__pycache__` or `.pyc` files through the merge.
- Do not use synthetic/static fallback hotspot datasets.
- Do not run a separate frontend `/thermal/infer/upload` call in parallel with `/analysis/from-capture-upload`; the analysis endpoint already runs ThermalGen and returns the preview URL.

## Current ThermalGen Reality

ThermalGen requires local checkpoint files under:

```text
backend/models/hybrid_thermal/checkpoints/
```

If the checkpoint or image is unavailable, the backend returns no hotspot regions and reports the error. It should not invent demo hotspots.

Hotspot localization currently uses model output brightness:

```text
connected bright thermal region
-> brightest pixel inside region becomes centroid_px
-> centroid_px maps into capture bounds
-> frontend marker appears on the thermal peak
```

## Teammate Rule

When continuing this work, preserve this invariant:

```text
source image bounds == thermal preview bounds == GroundOverlay bounds == hotspot pixel-to-geo bounds
```

Breaking that invariant is what causes thermal overlays to look stretched and hotspot markers to drift away from the bright heat regions.
