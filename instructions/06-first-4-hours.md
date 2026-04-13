# First 4 Hours

This is the execution order for the current pivot.

## Hour 0 to 1

All together for 10-15 minutes:

- freeze the product framing
- freeze the capture payload from frontend
- freeze the two-tool story:
  - `ThermalGen`
  - `Heat Risk Profiler`
- freeze one golden demo question

Then split:

- Engineer 1 builds capture UX and upload flow
- Engineer 2 stabilizes capture endpoints and analysis resource flow
- Engineer 3 defines ThermalGen + Heat Risk Profiler outputs
- Engineer 4 defines ranking and recommendation outputs

## Hour 1 to 2

- Engineer 1 connects frontend capture to backend
- Engineer 2 stores captures and returns stable analysis payloads
- Engineer 3 returns real or fixture tool outputs
- Engineer 4 plugs scoring into the orchestrator output

Goal:

- one selected locality can become one valid analysis

## Hour 2 to 3

- make the trace visibly show `ThermalGen`
- make the trace visibly show the supporting tool
- connect follow-up questions over the same analysis
- keep provider logic behind `LLMProvider`

Goal:

- the product already feels agentic and not mono-tool

## Hour 3 to 4

- polish the recommendation
- tighten discard logic
- stabilize one golden region and one golden question
- prepare fallback assets

Goal:

- one strong, replayable demo path

## Rule

Do not build more tools just to look broad.

Make the two-tool story feel intentional:

- `ThermalGen` is the standout superpower
- the supporting tool proves the agent is a broader investigation system
