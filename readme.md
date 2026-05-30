# UrbanLens

UrbanLens is a hackathon-origin urban heat investigation system built by a four-person team at the WashU Google Build with AI hackathon.

Users select a satellite region in Google Maps. UrbanLens captures the map image and metadata, runs RGB-to-thermal generation through ThermalGen, proposes heat hotspot candidates, classifies visible surface types, ranks findings with deterministic scoring, and supports grounded follow-up questions over stored analysis artifacts.

UrbanLens is not production environmental measurement software. ThermalGen outputs are relative thermal evidence, not calibrated thermal camera readings. The portfolio signal is the system design: typed contracts, artifact flow, deterministic ranking, model integration, and bounded AI behavior.

![CI](https://github.com/LambSystems/urbanlens/actions/workflows/ci.yml/badge.svg)

- Demo video: [YouTube](https://www.youtube.com/watch?v=78SCFwdAIuk)
- Hackathon submission: [Devpost](https://devpost.com/software/urbanlens-uxwd48)
- Docs index: [docs/README.md](./docs/README.md)

![UrbanLens analysis view](./assets/main.png)

## Review Paths

| If you are... | Start here |
|---|---|
| A recruiter or portfolio reviewer | [Portfolio architecture](./docs/portfolio-architecture.md), [team contributions](./docs/team-and-contributions.md), and the demo video |
| An engineer reviewing the system | [Contracts](./docs/contracts.md), [example output](./docs/examples/demo-analysis-summary.json), and [local dev setup](./docs/local-dev-setup.md) |
| Trying to run it locally | `.\scripts\dev.ps1` after copying `.env.example` to `.env` |
| Deploying the portfolio demo | [Deployment notes](./docs/deployment.md) |
| Looking for hackathon history | [Hackathon planning archive](./docs/archive/hackathon-planning/README.md) |

## Pipeline

```text
Select map region
  -> capture satellite image and map metadata
  -> generate relative thermal evidence with ThermalGen
  -> propose candidate heat hotspots
  -> classify visible surface types from RGB crops
  -> compute anomaly, severity, confidence, and rank scores
  -> return prioritized findings and grounded follow-up answers
```

## Workflow

| Select locality | Rank heat findings | Ask grounded follow-up |
|---|---|---|
| ![Region selection](./assets/1.png) | ![Priority ranking](./assets/3.png) | ![Planner response](./assets/4.png) |

## Deterministic vs AI-Assisted

- Deterministic: capture handling, artifact storage, hotspot proposal, scoring, ranking, debug views, and API response contracts.
- Model-based: ThermalGen generates relative thermal evidence from RGB satellite captures.
- AI-assisted: optional crop classification, explanation wording, and follow-up planning over stored analysis results.
- Bounded: the LLM does not own ranking math, anomaly gates, or final prioritization.

Ranking is intentionally inspectable:

```text
if anomaly_score < anomaly_threshold:
    discard

final_rank_score = severity_score * confidence_score
```

## Architecture At A Glance

- Frontend: Next.js, React, TypeScript, Tailwind, and Google Maps region selection.
- Backend: FastAPI, Pydantic contracts, local artifact persistence, ThermalGen integration, scoring/ranking, and planner endpoints.
- ThermalGen: PyTorch RGB-to-thermal generation adapted for urban imagery.
- Planner layer: provider-neutral LLM adapters for grounded follow-up answers over existing analysis results.

See [docs/portfolio-architecture.md](./docs/portfolio-architecture.md) for the full system diagram and tradeoff discussion.

## Run Locally

Fast Windows setup:

```powershell
copy .env.example .env
notepad .env
.\scripts\dev.ps1
```

The dev script syncs service env files and launches:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

Use `LLM_PROVIDER=mock` for a no-key local demo. For hosted portfolio deployments where AI keys and model checkpoints should not be required, set `DEMO_MODE=true`; the backend will keep the same API contracts but return deterministic fixture analysis instead of calling live LLMs or ThermalGen.

The live Google Maps UI still needs `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`. Full ThermalGen inference needs local checkpoints under:

```text
backend/models/hybrid_thermal/checkpoints/
```

For setup details and troubleshooting, see [docs/local-dev-setup.md](./docs/local-dev-setup.md).

Hosted portfolio deploys should use `DEMO_MODE=true`; Railway installs the lightweight `backend/requirements-deploy.txt` via `backend/nixpacks.toml` so the public demo does not pull the full ThermalGen/PyTorch stack.

## Smoke Checks

```powershell
.\scripts\smoke.ps1
```

The smoke path runs deterministic backend tests and the demo fixture without Google Maps, ThermalGen checkpoints, or real LLM keys.

Example output artifact:

- [docs/examples/demo-analysis-summary.json](./docs/examples/demo-analysis-summary.json)

## Team

UrbanLens was built by:

- [@tioluwani-enoch](https://github.com/tioluwani-enoch): frontend UI/UX, Google Maps interaction, side panels, and analysis presentation.
- [@GALGALLOR](https://github.com/GALGALLOR): ThermalGen adaptation, RGB/thermal preprocessing, inference integration, and thermal overlay work.
- [@shuja-waraich-03](https://github.com/shuja-waraich-03): backend setup, agent loop, tool-calling behavior, prompts, and investigation flow.
- [@postigodev](https://github.com/postigodev): analysis contracts, capture/API alignment, deterministic scoring/ranking, provider paths, setup docs, CI, and repo hardening.

For a fuller team-oriented writeup, see [docs/team-and-contributions.md](./docs/team-and-contributions.md).

## Hackathon Tradeoffs

- Local file storage is used for captures and generated artifacts; production would use object storage and retention/access policies.
- ThermalGen predictions are relative evidence, not calibrated measurements.
- Model checkpoints are large local artifacts and are not committed.
- The system favors a small, explainable pipeline over broad autonomous-agent behavior.
- LLM behavior is bounded to explanation and planning over stored evidence.

## License

UrbanLens is available under the [MIT License](./LICENSE).
