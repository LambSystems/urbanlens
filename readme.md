# Urban Legend
## Best-in-Agentic-AI Urban Heat Investigation Agent

Urban Legend is an agentic urban heat investigation system built for the `Best in Agentic AI` track.

Most tools stop at showing heat maps. Urban Legend lets users ask questions about what they see and gets an AI agent to investigate, reason through the evidence step by step, and come back with actionable answers — all with a fully visible chain of thought.

The project is also positioned to make a credible run at `Best Design using v0` by using `v0` to accelerate and polish the most visible UI surfaces around the core agentic flow.

---

## Problem

Urban heat is visible, but not actionable.

Stakeholders can often see that an area is hot, but they still cannot answer:

- Which hotspot matters most?
- What is causing it?
- Is it unusual relative to nearby structures?
- What should we fix first?

Existing tools provide analysis, not decisions. They require users to interpret data themselves.

In Urban Legend, Google Maps is the interaction layer, not the source of truth. The actual evidence comes from scattered drone imagery, a satellite-to-thermal conversion model, and related metadata.

---

## How It Works

1. User selects a region on the map
2. System loads the data context: satellite imagery, thermal overlay, drone sources, location metadata
3. User types a prompt describing what they want to know
4. The agent reads the prompt, examines the available data, and decides what tools to call
5. The agent investigates in a visible chain of thought — each reasoning step and tool call is shown in the UI
6. The agent returns a structured answer with evidence and recommendations
7. User can ask follow-up questions on the same region

The user's prompt drives the investigation. The agent adapts its tool usage and reasoning path based on what the user actually asked.

---

## Why This Is Agentic

Urban Legend is not a one-shot LLM wrapper and not just a thermal visualization pipeline.

It behaves like an agent by:

- interpreting the user's intent from their prompt
- examining available data to understand what evidence exists
- deciding what tools to call and in what order
- gathering evidence step by step with a visible chain of thought
- retrieving and normalizing available drone sources for the selected region
- comparing against context and nearby structures
- rejecting weak findings with evidence-backed reasoning
- returning actionable answers, not just data

The key behavior is not detection. It is **prompt-driven investigation under uncertainty**.

---

## Example Interactions

**User prompt:** "What should I fix first in this area?"

Agent investigates all hotspot candidates, scores them, discards expected heat patterns, ranks survivors, and recommends the top intervention with reasoning.

**User prompt:** "Are there any HVAC issues on these rooftops?"

Agent focuses on mechanical equipment hotspots, checks thermal signatures against expected patterns, and reports findings.

**User prompt:** "Why is the northeast corner so hot?"

Agent examines the specific area, identifies surface materials, compares against nearby structures, and explains the likely cause.

**User follow-up:** "How confident are you about that roof?"

Agent pulls up the source coverage for that hotspot, reports metadata quality, and explains confidence factors.

---

## Core Demo Loop

1. User selects a region on the map
2. System loads satellite imagery, thermal overlay, and source metadata
3. User types a question about the region
4. Agent begins visible investigation — chain of thought streams to the UI
5. Agent calls tools, gathers evidence, reasons through findings
6. Agent returns a structured answer with recommendations
7. User asks follow-up questions to dig deeper

This conversational investigation is the product.

---

## Scope for the Hackathon

We are optimizing for one polished, judge-friendly experience rather than a broad platform.

### Must Have

- one stable demo region
- RGB map layer plus thermal overlay
- analysis region centered around the user click
- region-level source retrieval over scattered drone imagery
- prompt input where the user types their question
- visible chain of thought showing every reasoning step and tool call
- agent tool usage driven by user intent, not a fixed pipeline
- evidence-backed findings with confidence, severity, anomaly
- conversational follow-ups on the same region
- fallback precomputed outputs for live demo reliability

### Should Have

- neighbor comparison
- coarse material or surface inference
- consistency check across nearby crops or tiles
- cached session replay for the demo
- shared schema contract between backend and frontend
- v0-assisted UI generation and polish for the sidebar, chain of thought panel, and recommendation display
- coverage-aware confidence that reflects incomplete source availability

### Explicitly Cut

- multi-region live analysis
- temporal analysis
- intervention simulation
- overly complex model orchestration
- claims of precise physical temperature truth

---

## Architecture at a Glance

Urban Legend is built as a prompt-driven investigation system:

- `Source Retrieval Layer`
  finds drone images and metadata intersecting the selected region
- `Evidence Normalization Layer`
  turns scattered imagery into analysis-ready region evidence
- `Thermal Generation Module`
  satellite-to-thermal conversion model; provides thermal evidence and UI overlay
- `Perception Layer`
  identifies object or surface cues from imagery
- `Context Layer`
  compares hotspots against nearby structures
- `Agent Orchestrator`
  interprets user prompt, decides what tools to call, runs visible chain of thought
- `Scoring Layer`
  anomaly gating, severity ordering, confidence modulation
- `Map-First UI`
  prompt input, chain of thought display, and recommendations — makes the reasoning legible

---

## Current Thermal Model Setup

The RGB-to-thermal model package is centralized at:

```text
backend/app/thermal/hybrid_thermal/
```

Dataset files are expected at:

```text
backend/data/hybrid_thermal/RGB_to_thermal_dataset/
```

Model config is repo-relative:

```text
backend/models/hybrid_thermal/config.yaml
```

The dataset and checkpoints are not committed to Git. They should be shared separately as a zip, for example `UrbanLens_hybrid_thermal_assets.zip` through Google Drive, and unzipped so these paths exist:

```text
backend/data/hybrid_thermal/RGB_to_thermal_dataset/
backend/models/hybrid_thermal/checkpoints/best_psnr.pth
```

After cloning and unzipping the shared data/checkpoint bundle, run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

For quick visual inference, open:

```text
notebooks/hybrid_thermal_inference.ipynb
```

The backend returns both:

- `thermal_image_path`: grayscale model output for pipeline use
- `thermal_preview_path`: autocontrasted orange thermal preview for UI display
- `thermal_preview_url`: browser-loadable preview path served from `/thermal-assets/...`

More implementation notes are in:

```text
docs/hybrid_thermal.md
docs/thermalgen_handoff.md
docs/local_setup.md
```

To keep the normal API fast, live hybrid thermal inference in `/analysis` is controlled by a local backend env flag:

```text
THERMALGEN_ENABLE_LIVE_THERMAL=1
```

Leave it off while developing frontend/agentic UI flows; turn it on when you want the backend to generate and attach one real thermal preview to the analysis response.

---

## Example Output

```json
{
  "prompt": "What should I fix first in this area?",
  "answer": "The commercial roof at the northeast corner is the highest-priority intervention. It shows unusually high heat relative to nearby roofs, with a dark roofing surface that is a strong candidate for cool-roof retrofit.",
  "chain_of_thought": [
    {"tool": "inspect_object", "summary": "Identified commercial roof structure"},
    {"tool": "request_thermal_evidence", "summary": "Thermal intensity 0.87, significantly above regional mean"},
    {"tool": "compare_neighbors", "summary": "Hotter than 83% of nearby comparable roofs"},
    {"tool": "score_hotspot", "summary": "Anomaly: 0.82, Severity: 0.76, Confidence: 0.71"},
    {"tool": "finalize_hotspot", "summary": "Passed anomaly gate — recommended for intervention"}
  ],
  "top_recommendation": {
    "hotspot_type": "commercial roof",
    "severity": 0.84,
    "anomaly": 0.71,
    "confidence": 0.78,
    "recommended_action": "cool-roof retrofit",
    "priority_rank": 1
  }
}
```

---

## Demo Story

The demo is designed around one message:

> Ask a question about urban heat. Watch the agent investigate. Get an answer you can act on.

The winning moment is when the user types a question, the agent visibly reasons through the evidence — calling tools, comparing structures, rejecting weak signals — and returns an actionable recommendation with full transparency.

That is the proof that the system is agentic.

---

## Team Strategy

This scope is designed for a 4-engineer team with strong implementation support from Codex and Claude Code.

- Engineer 1: frontend, map, prompt input, chain of thought UI, recommendations
- Engineer 2: backend, agent orchestrator, API, session management
- Engineer 3: perception, hotspot evidence, thermal integration
- Engineer 4: context, scoring, ranking, confidence

The goal is not maximum feature count.

The goal is the most convincing prompt-driven investigation slice of an urban heat agent.

---

## Strategic Framing

Urban Legend should be presented as:

> an agentic urban heat investigation system where users ask questions and the agent investigates with visible reasoning to deliver actionable recommendations

Not as:

- a thermal image generator
- a generic geospatial analytics dashboard
- a chatbot wrapper over an API

Primary users:

- city councils
- facilities and campus operations teams
- sustainability planners

---

## Core Insight

The future of geospatial AI is not better maps.

It is agents that investigate what you ask about and tell you what to do next.
