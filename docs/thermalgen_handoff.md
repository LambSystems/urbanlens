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
- Dataset files are expected locally at `backend/data/hybrid_thermal/RGB_to_thermal_dataset`.
- Generated runtime outputs are written under `backend/data/hybrid_thermal` and remain ignored.
- Model artifacts are expected locally at `backend/models/hybrid_thermal`.
- Dataset and checkpoint files are not pushed to Git. Share them as a zip, for example through Google Drive.
- One-image inference has been verified using `487.JPG`.
- Generated thermal output was written to `backend/data/hybrid_thermal/Predict_Thermal/487.png`.
- Backend now also writes an autocontrasted orange preview via `thermal_preview_path`.
- A runnable inference notebook exists at `notebooks/hybrid_thermal_inference.ipynb`.

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
backend/data/hybrid_thermal/RGB_to_thermal_dataset/
backend/data/hybrid_thermal/Test_RGB_centercrop_640x512/
backend/data/hybrid_thermal/Predict_Thermal/
notebooks/hybrid_thermal_inference.ipynb
```

`config.yaml` is repo-relative and can be pushed. Dataset/checkpoint files are local-only and should come from the shared zip.

Generated folders are intentionally ignored:

```text
backend/data/hybrid_thermal/RGB_to_thermal_dataset/
backend/data/hybrid_thermal/Predict_Thermal/
backend/data/hybrid_thermal/Test_RGB_centercrop_640x512/
backend/data/hybrid_thermal/Test_Thermal_640x512/
backend/data/hybrid_thermal/RGB_centercrop_640x512/
backend/data/hybrid_thermal/Thermal_640x512/
backend/data/hybrid_thermal/predictions/
backend/data/hybrid_thermal/metrics/
backend/data/hybrid_thermal/logs/
backend/models/hybrid_thermal/checkpoints/
```

## Inference Commands

From the repo root:

```powershell
.\.venv\Scripts\python.exe backend\app\thermal\hybrid_thermal\prealign_test_rgb_thermal.py --config backend\models\hybrid_thermal\config.yaml --limit 1

.\.venv\Scripts\python.exe backend\app\thermal\hybrid_thermal\inference.py --config backend\models\hybrid_thermal\config.yaml --limit 1
```

The app-facing call is:

```python
from backend.app.thermal.generator import generate_thermal

result = generate_thermal(
    "backend/data/hybrid_thermal/RGB_to_thermal_dataset/Test/RGB/487.JPG",
    {"lat": 38.6270, "lng": -90.1994},
)
```

## Tooling Notes

- Use the notebook for quick image generation and visual checks.
- Use `generate_thermal` when integrating with the backend agent flow.
- Use `predict_one` from `backend.app.thermal.hybrid_thermal.runtime` for direct model inference.
- Frontend/backend consumers should render `thermal_preview_path` for display and keep `thermal_image_path` as the grayscale model output.
- Keep `--limit 1` while testing to avoid processing the full dataset.
- Do not commit dataset zips, unzipped dataset files, generated predictions, cache folders, or `.pth` checkpoints.

## Teammate Setup After Clone

Download the shared data zip from Google Drive and unzip it into the repo so these paths exist.

Current bundle filename:

```text
UrbanLens_hybrid_thermal_assets.zip
```

```text
backend/data/hybrid_thermal/RGB_to_thermal_dataset/
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

## Push Checklist

Before pushing:

```powershell
git status --short
```

Expected behavior:

- dataset files under `backend/data/hybrid_thermal/RGB_to_thermal_dataset/` should stay ignored
- checkpoint files under `backend/models/hybrid_thermal/checkpoints/` should stay ignored
- generated predictions under `backend/data/hybrid_thermal/Predict_Thermal/` should stay ignored

## Next Useful Work

- Connect real thermal output to candidate discovery instead of the static hotspot library.
- Decide how the frontend should load generated thermal PNGs for map/sidebar preview.
- Add a small API endpoint or debug route that runs `generate_thermal` for a selected demo image.
- Replace remaining cached demo hotspot values gradually, while keeping fallback behavior for reliability.
