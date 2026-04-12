# First 4 Hours

This is the execution order for the team.

## Hour 0 to 1

All together for 10-15 minutes:

- freeze shared contract
- freeze one demo region
- freeze one example prompt and expected answer
- freeze chain of thought step format

Then split:

- Engineer 1 builds UI shell with prompt input and chain of thought panel
- Engineer 2 builds session API and mocked chain of thought response
- Engineer 3 builds hotspot evidence fixtures
- Engineer 4 builds scoring logic

## Hour 1 to 2

- Engineer 2 exposes real session endpoints with mocked chain of thought
- Engineer 1 connects to backend — renders prompt input, chain of thought, and answers
- Engineer 3 improves evidence quality, wires thermal tool
- Engineer 4 plugs scoring into tool dispatch

Goal:

- full product renders from API with chain of thought visible

## Hour 2 to 3

- Wire Gemini into the agent loop — real tool calling
- Chain of thought streams from agent decisions, not mocked sequences
- Add follow-up question support
- Validate schema consistency

Goal:

- user types a prompt, agent investigates live with visible chain of thought

## Hour 3 to 4

- Replace mocked tool internals with real evidence
- Polish chain of thought summaries
- Improve ranking explanations
- Stabilize one demo region with one primary prompt and one follow-up

Goal:

- one full region works end-to-end with real investigation

## Rule

Integrate early.

Do not wait for "real" implementations before wiring the system together.

The mocked chain of thought should look exactly like the real one — same step types, same field names, same streaming behavior. The only difference is where the data comes from.
