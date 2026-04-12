# First 4 Hours

This is the execution order for the team.

## Hour 0 to 1

All together for 10-15 minutes:

- freeze shared contract
- freeze one demo region
- freeze one discarded hotspot example
- freeze one Top 1 hotspot example

Then split:

- Engineer 1 builds UI shell
- Engineer 2 builds API and orchestrator skeleton
- Engineer 3 builds hotspot evidence fixtures
- Engineer 4 builds scoring logic

## Hour 1 to 2

- Engineer 2 exposes real endpoints
- Engineer 1 connects to backend payloads
- Engineer 3 improves evidence quality
- Engineer 4 plugs scoring into backend flow

Goal:

- full product renders from API

## Hour 2 to 3

- implement trace playback
- add discarded hotspot path
- add Top 3 ranking
- validate schema consistency

Goal:

- visible 5-15 second investigation

## Hour 3 to 4

- replace one or more mocked internals with real evidence
- polish trace summaries
- improve ranking explanations
- stabilize one demo region

Goal:

- one full region works end-to-end

## Rule

Integrate early.

Do not wait for "real" implementations before wiring the system together.
