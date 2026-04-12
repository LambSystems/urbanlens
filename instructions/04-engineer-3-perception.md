# Engineer 3
## Perception, Thermal Integration, and Hotspot Evidence

Owner:

- hotspot proposal
- object typing
- coarse material/surface inference
- thermal model integration
- evidence packaging for backend
- work from scattered drone imagery or curated region evidence, not from an assumed perfect tile source

## Immediate Goal

Provide believable hotspot evidence fast enough that the agent's tool calls return real data.

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
5. Wire the thermal model stub so `request_thermal_evidence` returns useful data.

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
- expose coverage quality or source-count hints when possible
- assume some source records may have incomplete geolocation metadata

## How Your Code Gets Called

The agent orchestrator calls your code through tools:

- `inspect_object` -> `perception/object_classifier.py`
- `infer_surface` -> `perception/surface_inference.py`
- `request_thermal_evidence` -> `thermal/evidence.py`
- `list_hotspot_candidates` -> `perception/candidate_discovery.py`

When the user asks a question and the agent decides it needs object or thermal evidence, it calls your functions. Your output appears as a chain of thought step in the UI.

## Handoff to Engineer 2

Provide a shape that can be attached to each tool call result.

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

Engineer 2 can call your functions from the agent tool registry and get real evidence back. Engineer 1 can see that evidence in the chain of thought panel.
