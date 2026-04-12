# Local Setup And Hidden Files

This repo keeps code, docs, schemas, and example configs in Git. Large data, model artifacts, secrets, generated outputs, and local environments stay out of Git.

## Local Environments

Use one Python virtual environment at the repo root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Do not create or commit nested virtual environments inside `backend/`, `frontend/`, or the thermal model folders.

For notebooks:

```powershell
.\.venv\Scripts\python.exe -m ipykernel install --user --name urbanlens --display-name "UrbanLens .venv"
```

## Environment Files

Real env files are local-only:

```text
.env
backend/.env
frontend/.env
frontend/.env.local
```

Tracked templates:

```text
.env.example
backend/.env.example
frontend/.env.example
```

Frontend variables:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=replace_with_google_maps_browser_key
```

Backend optional toggles:

```text
THERMALGEN_ENABLE_LIVE_THERMAL=0
THERMALGEN_DEMO_IMAGE=
```

Leave `THERMALGEN_ENABLE_LIVE_THERMAL=0` for fast demos. Set it to `1` when you want `POST /analysis` to run one local hybrid thermal inference and attach the generated thermal preview URL to hotspot evidence.

## Local Models

The shared Google Drive zip should be extracted at the repo root so these paths exist:

```text
backend/models/hybrid_thermal/checkpoints/best_psnr.pth
```

These are intentionally ignored by Git:

```text
backend/models/hybrid_thermal/checkpoints/
backend/data/hybrid_thermal/Predict_Thermal/
backend/data/hybrid_thermal/Test_RGB_centercrop_640x512/
backend/data/hybrid_thermal/uploads/
*.zip
```

## Restore Checklist After Pulls

If a pull, branch switch, or merge seems to remove local thermal assets, restore the checkpoints from the shared backup zip into these exact repo-relative locations.

Required for inference:

```text
backend/models/hybrid_thermal/checkpoints/best_psnr.pth
backend/models/hybrid_thermal/checkpoints/best_loss.pth
backend/models/hybrid_thermal/checkpoints/latest.pth
```

RGB inputs are supplied at runtime by frontend upload or by setting a local file path in the notebook/API request.

Optional/generated files that can be recreated:

```text
backend/data/hybrid_thermal/Test_RGB_centercrop_640x512/
backend/data/hybrid_thermal/Predict_Thermal/
backend/data/hybrid_thermal/uploads/
backend/models/.ipynb_checkpoints/
```

Current inference smoke check:

```powershell
.\.venv\Scripts\python.exe -B -c "from backend.app.thermal.hybrid_thermal.runtime import choose_checkpoint; print(choose_checkpoint())"
```

If this raises `No hybrid_thermal checkpoints found`, restore the `.pth` files above before running the notebook or live backend thermal evidence.

## Frontend Artifacts

The frontend uses `frontend/package.json` and `frontend/pnpm-lock.yaml`. Local installs and builds are ignored:

```text
frontend/node_modules/
frontend/.next/
frontend/out/
frontend/tsconfig.tsbuildinfo
```

Run the frontend from `frontend/`:

```powershell
corepack pnpm install
corepack pnpm dev
```

If PowerShell blocks npm shims, use `npm.cmd` as the fallback:

```powershell
npm.cmd install
npm.cmd run dev
```

## ThermalGen Connection State

The frontend is connected to the FastAPI backend through `NEXT_PUBLIC_API_URL`.

The backend has the hybrid thermal model wired through:

```text
backend/app/thermal/generator.py
backend/app/thermal/hybrid_thermal/runtime.py
```

Generated thermal files are served by FastAPI from:

```text
/thermal-assets/...
```

The current agent/orchestrator can attach hybrid thermal preview evidence when `THERMALGEN_ENABLE_LIVE_THERMAL=1`. With the toggle off, the API stays fast and uses the existing static demo hotspot flow while the agentic layer is being completed.

