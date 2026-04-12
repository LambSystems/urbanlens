# Engineer 3
## Perception and Hotspot Evidence

Owner:

- hotspot proposal
- object typing
- coarse material/surface inference
- evidence packaging for backend

## Immediate Goal

Provide believable hotspot evidence fast enough that the orchestrator can operate over it.

If real inference is slow, ship precomputed fixtures first.

## First Hour

1. Decide what candidate proposal path is fastest.
2. Produce 3-5 hotspot candidates for one stable demo region.
3. For each hotspot, provide:
   - `hotspot_type`
   - `object_confidence`
   - `material_type`
   - `material_confidence`
4. Package results in a backend-friendly format.

## Supported Types

- `roof`
- `road_pavement`
- `parking_lot`
- `hvac_mechanical`
- `vegetation_loss`
- `other`

## Rules

- use coarse labels
- optimize for stable and legible evidence
- do not overinvest in perfect classification

## Handoff to Engineer 2

Provide a shape that can be attached to each hotspot as evidence.

Minimum useful payload:

```json
{
  "hotspot_id": "hs_01",
  "hotspot_type": "roof",
  "object_confidence": 0.88,
  "material_type": "dark_roof",
  "material_confidence": 0.74
}
```

## Success Condition

Engineer 2 can attach your evidence to hotspot traces and Engineer 1 can render it in the sidebar.
