# UrbanLens Local Dev Setup

This is the fastest path for running UrbanLens locally on Windows with PowerShell.

## Fast Path

From the repository root:

```powershell
copy .env.example .env
notepad .env
.\scripts\dev.ps1
```

Open:

```text
http://localhost:3000
```

The backend runs on:

```text
http://localhost:8000
```

Use `LLM_PROVIDER=mock` for a no-key local demo. A Google Maps browser key is still needed for the live map UI.

For a hosted portfolio demo where cloud costs and expired AI keys should never break the walkthrough, set:

```text
DEMO_MODE=true
LLM_PROVIDER=mock
```

`DEMO_MODE=true` keeps the same backend contracts but returns deterministic fixture data instead of calling live LLMs or heavy ThermalGen inference.

## First-Time Dependency Install

If dependencies are not installed yet:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
corepack pnpm --dir frontend install
.\scripts\dev.ps1
```

Or let the dev script install dependencies after Python and Node are available:

```powershell
.\scripts\dev.ps1 -Install
```

## Environment Model

UrbanLens uses the repository-root `.env` as the source of truth.

Tracked templates:

```text
.env.example
backend/.env.example
frontend/.env.example
```

The service-level examples are intentionally kept because Railway and Vercel may use `backend/` or `frontend/` as project roots. For normal local development, edit only the repository-root `.env`.

Local generated files:

```text
.env
backend/.env
frontend/.env
```

Run this whenever root `.env` changes:

```powershell
.\scripts\sync-env.ps1
```

The sync script writes backend-only variables into `backend/.env` and `NEXT_PUBLIC_*` variables into `frontend/.env`.

If an existing service env file was written manually, the sync script backs it up before replacing it.

## One-Command Launch

```powershell
.\scripts\dev.ps1
```

This script:

- creates `.env` from `.env.example` if missing
- syncs service env files
- starts FastAPI on `localhost:8000`
- starts Next.js on `localhost:3000`
- opens each server in its own PowerShell window

## Smoke Checks

```powershell
.\scripts\smoke.ps1
```

This runs:

```powershell
python -m unittest discover tests
python scripts\demo_analysis.py
```

The smoke path does not require Google Maps, ThermalGen checkpoints, or real LLM keys.

The hosted demo path is intentionally different from production mode:

- `POST /analysis` and capture endpoints return a fixed `demo_washu` analysis.
- `POST /thermal/infer/upload` returns deterministic thermal metadata without running the model.
- `/analysis/{region_id}/questions` and `/session/*/prompt` return grounded fixture answers without external AI calls.

CI runs the same backend smoke path using `backend/requirements-smoke.txt` so GitHub Actions does not need to install PyTorch, rasterio, or model checkpoints.

## Dependency Audit

Frontend dependencies can be audited with either package manager:

```powershell
cd frontend
corepack pnpm audit
```

Backend dependency auditing is intentionally not part of runtime requirements. Use `pip-audit` as a local tool when Python is available:

```powershell
.\.venv\Scripts\python.exe -m pip install pip-audit
.\.venv\Scripts\python.exe -m pip_audit -r backend\requirements.txt
```

## ThermalGen Checkpoints

The full thermal inference path requires local model checkpoints:

```text
backend/models/hybrid_thermal/checkpoints/best_psnr.pth
backend/models/hybrid_thermal/checkpoints/best_loss.pth
backend/models/hybrid_thermal/checkpoints/latest.pth
```

These are intentionally not committed because they are large model artifacts.

To check checkpoint discovery:

```powershell
.\.venv\Scripts\python.exe -B -c "from backend.app.thermal.hybrid_thermal.runtime import choose_checkpoint; print(choose_checkpoint())"
```

## Common Issues

### Python is not found

Install Python and ensure it is on PATH, or create `.venv` at the repository root.

### Corepack is not available

Install a current Node.js release, then enable Corepack:

```powershell
corepack enable
corepack pnpm install
```

### Google Maps fails to load

Set this in root `.env`, then rerun `.\scripts\sync-env.ps1`:

```text
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_browser_key
```

### Backend starts but thermal output is empty

Confirm checkpoints exist under `backend/models/hybrid_thermal/checkpoints/`. Without checkpoints, only fallback/mock paths are suitable.

## Docker

Docker is intentionally not required for the current local workflow. It is a good future step, but PyTorch model artifacts and local Google Maps credentials make the PowerShell workflow the lower-friction portfolio path right now.

## Local Experiments

`notebooks/` is ignored because it is used for local model experiments and scratch inference checks. Keep reusable findings in docs, scripts, or tests instead of committing exploratory notebook state.
