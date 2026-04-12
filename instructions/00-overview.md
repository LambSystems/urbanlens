# ThermalGen Build Specs

This folder is the implementation guide for the 21-hour hackathon build.

Read these in order:

1. `00-overview.md`
2. `01-shared-contract.md`
3. your engineer-specific file

Core rule:

`one region -> 3-5 hotspots -> one visible investigation trace -> one justified discard -> Top 3 ranking -> final recommendation`

If work does not improve that flow, cut it.

Primary target:

- `Best in Agentic AI`

Secondary target:

- `Best Design using v0`

Stack:

- Gemini
- Google Maps API
- Python + FastAPI
- React + TypeScript
- v0 for selected UI surfaces only

Known assets:

- thermal image generator already exists
- datasets already exist, though Saint Louis-specific data is still under research
- real evidence is expected to come from scattered drone imagery, not a perfectly tiled map source

Non-negotiables:

- analysis is over a region around a click, not a single object
- Google Maps is the UI layer, not the ground-truth evidence layer
- trace vocabulary is fixed
- trace routes are semivariable
- anomaly gates
- severity orders
- confidence modulates
- visible playback lasts about 5 to 15 seconds

Do not reopen product-scope debates during implementation unless something blocks the core flow.
