# UrbanLens Demo Walkthrough

This walkthrough explains the public hackathon demo and the deterministic local demo path.

- Public video: [YouTube](https://www.youtube.com/watch?v=78SCFwdAIuk)
- Hackathon submission: [Devpost](https://devpost.com/software/urbanlens-uxwd48)

## Product Demo Flow

The intended UrbanLens flow is:

```text
select a satellite region
  -> capture map image and metadata
  -> generate relative thermal evidence with ThermalGen
  -> propose hotspots
  -> classify visible surface types
  -> compute deterministic scores
  -> rank recommendations
  -> answer follow-up questions over stored analysis artifacts
```

The important portfolio boundary is that scoring and ranking are deterministic. The LLM layer is used for explanation and planning over existing evidence, not for inventing measurements or deciding rank order.

## Deterministic Local Demo

For a quick backend credibility check without Google Maps, model checkpoints, or LLM keys, run the fixture demo:

```powershell
cd backend
python scripts\demo_analysis.py
```

Expected shape:

```json
{
  "region_id": "demo_washu",
  "status": "completed",
  "summary": {
    "candidate_count": 3,
    "discarded_count": 1,
    "finalized_count": 2
  },
  "ranking_formula": "final_rank_score = severity_score * confidence_score after anomaly gate",
  "top_hotspots": [
    {
      "hotspot_id": "hs_demo_01",
      "priority_rank": 1,
      "hotspot_type": "roof",
      "recommended_action": "cool-roof retrofit"
    }
  ],
  "discarded_hotspot_ids": ["hs_demo_03"]
}
```

This script is intentionally not a replacement for the live app. It is a reproducible contract demo that shows the ranking and output shape without relying on external services.

## Local App Demo

For the full app path:

1. Start the FastAPI backend.
2. Start the Next.js frontend.
3. Select a Google Maps satellite region.
4. Run analysis from the sidebar.
5. Inspect the thermal overlay, hotspot markers, ranking panel, and planner response.

Use `LLM_PROVIDER=mock` for a no-key explanation path. Thermal inference still requires the local ThermalGen checkpoints described in [local_setup.md](./local_setup.md).

## Demo Claims To Keep Honest

- ThermalGen produces relative heat patterns, not calibrated thermal camera measurements.
- Local file storage is a hackathon/demo tradeoff.
- The analysis trace is a visible system trace, not a promise to expose private model reasoning.
- Ranking is deterministic and inspectable.
