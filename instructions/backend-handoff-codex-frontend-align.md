# Backend Handoff From `codex/frontend-align`

This note is for whoever is taking over this lane and wants to reuse the backend work already present in this branch family without dragging in unrelated UI experimentation or local cache noise.

## Branch context

- Current working branch: `codex/frontend-align`
- Base branch: `origin/ft-frontend-new`
- Important inherited backend line:
  - `origin/piero` at `cfcc364`
  - merged into this frontend branch earlier via `d0fae0a pulled from piero`
- This means most of the backend work below is already present in the history behind `origin/ft-frontend-new`.

## What is already valuable in backend history

These are the backend capabilities worth preserving and building on.

### 1. Analysis-first API

Canonical routes live in [backend/app/routes.py](C:/Users/akuma/repos/thermalgen/backend/app/routes.py) and [backend/app/main.py](C:/Users/akuma/repos/thermalgen/backend/app/main.py).

Important endpoints:

- `POST /analysis`
- `POST /analysis/from-capture`
- `POST /analysis/from-capture-upload`
- `GET /analysis/{region_id}`
- `GET /analysis/{region_id}/events`
- `GET /analysis/{region_id}/hotspots/{hotspot_id}`
- `GET /analysis/{region_id}/debug`
- `POST /analysis/{region_id}/questions`
- `POST /analysis/{region_id}/voice-briefing`
- `POST /thermal/infer/upload`
- `GET /health`

There is also a parallel session-style stack from Shuja:

- `POST /session`
- `GET /session/{session_id}/messages`
- `GET /session/{session_id}/chain-of-thought`

Recommendation:
- Keep `analysis` as the frontend-facing canonical flow.
- Treat `session` as optional/agentic sidecar behavior, not the primary integration contract.

### 2. Capture-based analysis pipeline

Important files:

- [backend/app/store.py](C:/Users/akuma/repos/thermalgen/backend/app/store.py)
- [backend/app/capture_pipeline.py](C:/Users/akuma/repos/thermalgen/backend/app/capture_pipeline.py)

The useful part here is that the backend already supports:

- receiving Google Maps region metadata plus capture image
- persisting capture files under `backend/data/captures/{region_id}/`
- writing `metadata.json`
- generating analysis from uploaded capture
- attaching thermal preview URLs to the analysis region

This is the right boundary for frontend:

- frontend sends `region + map + viewport + image`
- backend persists capture
- backend returns normal `AnalysisResponse`

### 3. Provider-agnostic LLM layer

Important files:

- [backend/app/llm/base.py](C:/Users/akuma/repos/thermalgen/backend/app/llm/base.py)
- [backend/app/llm/factory.py](C:/Users/akuma/repos/thermalgen/backend/app/llm/factory.py)
- [backend/app/llm/anthropic_provider.py](C:/Users/akuma/repos/thermalgen/backend/app/llm/anthropic_provider.py)
- [backend/app/llm/gemini_provider.py](C:/Users/akuma/repos/thermalgen/backend/app/llm/gemini_provider.py)
- [backend/app/llm/featherless_provider.py](C:/Users/akuma/repos/thermalgen/backend/app/llm/featherless_provider.py)
- [backend/app/llm/mock_provider.py](C:/Users/akuma/repos/thermalgen/backend/app/llm/mock_provider.py)

This is worth keeping because it lets the team switch providers without touching planner/session/orchestration code.

Current intended usage:

- `Anthropic` is the reliable default
- `Featherless` is the prize-track provider to plug in when ready
- `Gemini` remains optional
- `Mock` keeps local dev alive

### 4. Planner and answer shaping

Important file:

- [backend/app/agent/planner.py](C:/Users/akuma/repos/thermalgen/backend/app/agent/planner.py)

Why it matters:

- planner answers are already structured for UI
- responses can include:
  - `answer`
  - `answer_title`
  - `answer_sections`
  - `referenced_hotspot_ids`
- planner explicitly cites:
  - Thermal Evidence
  - Heat Risk Profile

This is already good frontend fuel and should not be thrown away.

### 5. Supporting tools and scoring pieces

Important files:

- [backend/app/heat_risk.py](C:/Users/akuma/repos/thermalgen/backend/app/heat_risk.py)
- [backend/app/scoring/anomaly.py](C:/Users/akuma/repos/thermalgen/backend/app/scoring/anomaly.py)
- [backend/app/scoring/severity.py](C:/Users/akuma/repos/thermalgen/backend/app/scoring/severity.py)
- [backend/app/scoring/confidence.py](C:/Users/akuma/repos/thermalgen/backend/app/scoring/confidence.py)
- [backend/app/scoring/ranker.py](C:/Users/akuma/repos/thermalgen/backend/app/scoring/ranker.py)

These give the product its current consistent story:

- anomaly gates
- severity orders
- confidence modulates
- ThermalGen plus Heat Risk Profile appear in trace and explanation

### 6. Voice briefing

Important file:

- [backend/app/voice_briefing.py](C:/Users/akuma/repos/thermalgen/backend/app/voice_briefing.py)

And route:

- `POST /analysis/{region_id}/voice-briefing`

This is optional for demo polish but already integrated and useful.

## What frontend already depends on from backend

Frontend is already shaped around these backend-friendly fields:

- `region.display_name`
- `region.thermal_preview_url`
- `region.thermal_image_url`
- hotspot:
  - `display_name`
  - `status_label`
  - `sidebar_summary`
  - `evidence_highlights`
  - `tool_signals`
  - `discard_reason`
  - `recommended_action`
  - `priority_rank`
  - `is_top_ranked`
- planner:
  - `answer_title`
  - `answer_sections`

If you refactor backend, preserve those fields.

## What is currently weak / known backend reality

These are important so nobody assumes magic.

### Thermal model is not actually running in this environment

Current observed blockers:

- the runtime falls back with `ModuleNotFoundError: No module named 'numpy'`
- `backend/models/hybrid_thermal/checkpoints/` currently contains only `.gitkeep`

Implication:

- ThermalGen may be returning `synthetic_fallback`
- hotspot proposals may therefore come from fallback logic instead of true model output

Do not promise pixel-accurate thermal localization unless the runtime and checkpoints are actually restored.

### Candidate fallback exists

Important file:

- [backend/app/perception/candidate_discovery.py](C:/Users/akuma/repos/thermalgen/backend/app/perception/candidate_discovery.py)

If thermal data has no real `hotspot_regions`, it uses `_STATIC_FALLBACK`.

That is useful for keeping the pipeline alive, but misleading if presented as real precision.

## Local WIP on top of this branch

These are local working-tree changes from this pairing session, not clean branch canon.

Files:

- [backend/app/thermal/generator.py](C:/Users/akuma/repos/thermalgen/backend/app/thermal/generator.py)
- [frontend/components/thermal-map.tsx](C:/Users/akuma/repos/thermalgen/frontend/components/thermal-map.tsx)
- [frontend/lib/thermal-context.tsx](C:/Users/akuma/repos/thermalgen/frontend/lib/thermal-context.tsx)
- [frontend/components/recommendation-card.tsx](C:/Users/akuma/repos/thermalgen/frontend/components/recommendation-card.tsx)

### WIP backend change

In [backend/app/thermal/generator.py](C:/Users/akuma/repos/thermalgen/backend/app/thermal/generator.py):

- started adapting centroid geo-mapping to use exact capture bounds (`north/south/east/west`) rather than generic static-map assumptions

Intent:

- if the thermal model returns real `centroid_px`, map those to the true capture footprint

Status:

- useful direction
- not yet separately smoke-tested through the full HTTP flow
- should be reviewed before cherry-picking

### WIP frontend changes

These were made only to stabilize the live demo UX locally:

- model-safe capture aspect ratio in `thermal-map`
- top-down map for overlay alignment
- overlay fallback to the analysis thermal preview
- recommendation card now uses backend reasoning fields more directly

If another engineer already fixed the hotspot alignment better, prefer their version and only borrow the backend ideas.

## What to cherry-pick vs what to ignore

### Safe to cherry-pick conceptually

- provider-neutral LLM layer under `backend/app/llm/`
- capture upload flow and persistence under `store.py` and `capture_pipeline.py`
- analysis-first routes in `routes.py`
- planner response structuring in `agent/planner.py`
- voice briefing endpoint and support
- heat risk + scoring modules

### Be careful / review first

- anything in `backend/app/thermal/generator.py`
- anything relying on true thermal hotspot localization
- any UI alignment math from this local session

### Do not carry over

- `__pycache__` changes
- any `.pyc` files
- accidental local environment artifacts

## Recommended merge strategy for the receiving engineer

1. Use `origin/ft-frontend-new` or the current demo branch as UI base.
2. Reuse backend canon already inherited from `origin/piero` rather than re-deriving it.
3. If cherry-picking, focus on backend files only:
   - `backend/app/routes.py`
   - `backend/app/main.py`
   - `backend/app/store.py`
   - `backend/app/capture_pipeline.py`
   - `backend/app/llm/*`
   - `backend/app/agent/planner.py`
   - `backend/app/heat_risk.py`
   - `backend/app/scoring/*`
   - `backend/app/voice_briefing.py`
4. Ignore local `.pyc` churn completely.
5. Treat the thermal runtime as a separate restore/debug task, not as already-solved infrastructure.

## Bottom line

The backend work worth preserving from this line is:

- analysis-first API
- capture upload pipeline
- provider-neutral LLM integration
- structured planner outputs
- voice briefing
- heat risk and ranking scaffolding

The part that is still not trustworthy is:

- real thermal runtime execution and localization

That should be merged deliberately, not implicitly.
