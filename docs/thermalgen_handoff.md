# ThermalGen Handoff

This file summarizes the current project state so other coders can use the right tools without re-discovering the repo.

## Current Product Frame

ThermalGen is the agentic urban heat triage system:

```text
select region -> detect hotspots -> investigate -> discard -> prioritize -> recommend
```

The thermal model is only one evidence tool in that loop. The canonical model package name is `hybrid_thermal`.

## What Has Been Done

- Backend scaffold exists under `backend/app`.
- Shared contracts and engineering instructions exist under `docs/` and `instructions/`.
- The thermal evidence wrapper is `backend/app/thermal/generator.py`.
- The RGB-to-thermal model package is centralized at `backend/app/thermal/hybrid_thermal`.
- No local dataset is required for live inference; RGB inputs come from frontend upload or a repo-local file path.
- Generated runtime outputs are written under `backend/data/hybrid_thermal` and remain ignored.
- Model artifacts are expected locally at `backend/models/hybrid_thermal`.
- Checkpoint files are not pushed to Git. Share them as a small zip, for example through Google Drive.
- One-image inference has been verified using a repo-local RGB file path.
- Backend now also writes an autocontrasted orange preview via `thermal_preview_path`.
- FastAPI serves generated thermal assets from `/thermal-assets/...`.
- A runnable inference notebook exists at `notebooks/hybrid_thermal_inference.ipynb`.
- Local environment and hidden-file rules are documented in `docs/local_setup.md`.

## Naming Rules

- Use `ThermalGen` for the product.
- Use `hybrid_thermal` for the model package, folders, runtime paths, and docs.
- Do not use `hybrid-thermal`.
- Do not keep a root-level `HybridThermal/` project folder.

## Canonical Paths

```text
backend/app/thermal/generator.py
backend/app/thermal/hybrid_thermal/
backend/models/hybrid_thermal/config.yaml.example
backend/models/hybrid_thermal/config.yaml
backend/models/hybrid_thermal/checkpoints/
backend/data/hybrid_thermal/uploads/
backend/data/hybrid_thermal/Test_RGB_centercrop_640x512/
backend/data/hybrid_thermal/Predict_Thermal/
notebooks/hybrid_thermal_inference.ipynb
```

`config.yaml` is repo-relative and can be pushed. Checkpoint files are local-only and should come from the shared zip.

Generated folders are intentionally ignored:

```text
backend/data/hybrid_thermal/Predict_Thermal/
backend/data/hybrid_thermal/Test_RGB_centercrop_640x512/
backend/data/hybrid_thermal/uploads/
backend/models/hybrid_thermal/checkpoints/
```

## Inference Commands

For current app/tool usage, prefer `generate_thermal` or the API endpoints in `docs/thermalgen_tool.md`. Legacy batch scripts still exist for model development, but the product path does not require a dataset.

The app-facing call is:

```python
from backend.app.thermal.generator import generate_thermal

result = generate_thermal(
    "backend/data/hybrid_thermal/uploads/map-capture.png",
    {"center": {"lat": 38.6270, "lng": -90.1994}},
    output_path="backend/data/hybrid_thermal/Predict_Thermal/demo_471.png",
    allow_fallback=False,
)
```

## Tooling Notes

- Use the notebook for quick image generation and visual checks.
- Use `generate_thermal` when integrating with the backend agent flow.
- Use `predict_one` from `backend.app.thermal.hybrid_thermal.runtime` for direct model inference.
- Runtime inference still preprocesses one image at a time: RGB open, center-crop/align, resize to 512x640, tensor normalization, checkpoint prediction, grayscale output, orange preview output.
- Teammates do not need dataset preprocessing for the app flow. Do not run manifest building, train/test splitting, AlphaEarth export, or batch alignment unless doing separate model-development work.
- Frontend/backend consumers should render `thermal_preview_url` for display and keep `thermal_image_path` as the grayscale model output.
- Do not commit uploaded images, generated predictions, cache folders, or `.pth` checkpoints.

## Frontend And Backend Connection

The frontend calls FastAPI through:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Keep the real value in `frontend/.env`; commit only `frontend/.env.example`.

The backend can attach live hybrid thermal evidence to `/analysis` responses when this local toggle is enabled:

```text
THERMALGEN_ENABLE_LIVE_THERMAL=1
```

Default is off so the demo remains fast while the agentic orchestration layer is still being finished. With the toggle on, the orchestrator runs one local RGB image through `generate_thermal`, adds region-level `thermal_image_url` / `thermal_preview_url`, and prepends the preview URL to hotspot `evidence_urls`.

Current browser flow:

```text
draw/select region in frontend
-> optionally POST /thermal/infer/upload with map/RGB image bytes
-> backend stores upload and runs ThermalGen
-> POST /analysis
-> backend creates region + hotspot trace and can attach ThermalGen evidence
-> frontend polls GET /analysis/{region_id}
-> frontend maps backend hotspots into UI hotspots
-> trace panel displays generated thermal preview only when the URL starts with /thermal-assets/
```

Known placeholder paths such as `/evidence/hs_01-thermal.jpg` are legacy demo metadata. They are not real files unless someone adds static evidence assets. The UI should not render them as images.

ThermalGen tool calls:

```text
POST /thermal/infer/upload
POST /thermal/infer/path
```

Use upload for frontend map snippets. Use path for internal backend/agent work after an image has already been saved. Avoid base64 image payloads for normal inference because they make requests larger and slower.

Detailed teammate instructions live in:

```text
docs/thermalgen_tool.md
```

## Teammate Setup After Clone

Download the shared checkpoint zip from Google Drive and unzip it into the repo so these paths exist.

Current bundle filename:

```text
UrbanLens_hybrid_thermal_checkpoints.zip
```

```text
backend/models/hybrid_thermal/checkpoints/best_psnr.pth
```

Expected checkpoint directory:

```text
backend/models/hybrid_thermal/checkpoints/
|-- best_psnr.pth
|-- best_loss.pth
`-- latest.pth
```

Then create the environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name urbanlens --display-name "UrbanLens .venv"
```

Open `notebooks/hybrid_thermal_inference.ipynb`, select the `UrbanLens .venv` kernel, and run all cells.

Copy env templates before running services:

```powershell
Copy-Item frontend\.env.example frontend\.env
Copy-Item backend\.env.example backend\.env
```

Then fill in the Google Maps browser key in `frontend/.env`.

## Push Checklist

Before pushing:

```powershell
git status --short
```

This command is not required for the app to run. It is a quick safety check before committing so secrets, checkpoints, generated predictions, uploaded images, and build artifacts do not accidentally get pushed.

Expected behavior:

- checkpoint files under `backend/models/hybrid_thermal/checkpoints/` should stay ignored
- generated predictions under `backend/data/hybrid_thermal/Predict_Thermal/` should stay ignored
- uploaded map snippets under `backend/data/hybrid_thermal/uploads/` should stay ignored

## Next Useful Work

- Connect real thermal output to candidate discovery instead of the static hotspot library.
- Use the existing `thermal_preview_url` consistently for map/sidebar preview.
- Replace remaining cached demo hotspot values gradually, while keeping fallback behavior for reliability.
