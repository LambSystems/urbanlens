# Engineer 3
## ThermalGen, Supporting Tools, and Evidence Packaging

Owner:

- `ThermalGen` integration
- supporting analysis tool outputs
- object/surface cues when useful
- evidence packaging for backend

## Immediate Goal

Make the agent’s tool calls return believable evidence from the captured locality.

Your work should make these tool calls real:

- `request_thermal_evidence`
- `generate_thermal_overlay`
- `analyze_heat_risk`
- optional perception helpers

## Product Rule

`ThermalGen` is the standout tool.

But the product should not feel mono-tool. That is why the supporting tool matters.

Recommended supporting tool:

- `Heat Risk Profiler`

Its job is to explain visible environmental drivers behind heat concern.

## First Priorities

1. Define the ThermalGen input and output contract for a captured image.
2. Define the Heat Risk Profiler output contract.
3. Package outputs so Engineer 2 can attach them to trace steps and findings.
4. If real inference is unstable, provide stable fixtures that match the final output shape.

## Minimum Useful Output

For ThermalGen:

```json
{
  "thermal_overlay_path": "backend/data/captures/region_123/thermal.png",
  "thermal_intensity_score": 0.86,
  "summary": "Elevated thermal evidence over the central roof mass"
}
```

For Heat Risk Profiler:

```json
{
  "heat_risk_score": 0.81,
  "factors": [
    "large exposed roof area",
    "dark surface cues",
    "low surrounding shade"
  ],
  "summary": "Visible environmental features suggest elevated retained heat risk"
}
```

## Success Condition

Engineer 2 can call your tools from the orchestrator and the frontend can show those outputs as part of a compelling investigation trace.
