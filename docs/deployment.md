# UrbanLens Deployment Notes

UrbanLens can be hosted as a portfolio demo without live AI keys or model checkpoints by enabling backend demo mode.

## Recommended Portfolio Setup

- Backend: Railway
- Frontend: Vercel
- Backend mode: `DEMO_MODE=true`
- LLM provider: `LLM_PROVIDER=mock`

This keeps the public demo stable and cheap. The deployed app uses the same API contracts as local development, but the backend returns deterministic fixture data instead of calling live LLMs or running ThermalGen checkpoints.

## Railway Backend

Create a Railway service from this repository and set the service root to:

```text
backend
```

Set the Railway config file path to:

```text
/backend/railway.toml
```

The backend also includes `backend/railpack.json`, which overrides Railpack's install step so the hosted demo installs `requirements-deploy.txt` instead of the full ThermalGen stack. This keeps the hosted demo small by excluding PyTorch, rasterio, and local model dependencies.

The expected Railpack build-step commands are split because Railpack executes each command directly, not through a shell. They live under `steps.build` because source files are not available during `steps.install`:

```text
pip install --upgrade pip
pip install -r requirements-deploy.txt
```

Use this start command if Railway asks for one manually:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set these environment variables:

```text
DEMO_MODE=true
LLM_PROVIDER=mock
PORT=8000
```

Optional voice and LLM keys should stay empty for the public demo.

Health check:

```text
/health
```

## Vercel Frontend

Create a Vercel project from this repository and set the project root to:

```text
frontend
```

Set these environment variables:

```text
NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-google-maps-browser-key
```

Build settings can remain the Next.js defaults. The frontend uses `pnpm-lock.yaml`, so Vercel should install with pnpm automatically.

## What Demo Mode Does

- `POST /analysis` and capture endpoints return the fixed `demo_washu` analysis.
- `POST /thermal/infer/upload` returns deterministic thermal metadata without running model inference.
- `/analysis/{region_id}/questions` returns a grounded fixture answer.
- `/session/*/prompt` returns fixture investigation steps without external AI calls.

## What Demo Mode Does Not Claim

- It does not generate fresh thermal predictions for arbitrary locations.
- It does not call Gemini, Featherless, Anthropic, or ElevenLabs.
- It does not replace the full local ThermalGen path documented in [local-dev-setup.md](./local-dev-setup.md).
