# Urban Legend Models
## Model and Reasoning Stack for the Winning Slice

This document describes the model stack for the hackathon version of Urban Legend.

The guiding rule is:

> models produce evidence, the agent produces decisions driven by the user's question

That distinction is what makes the project credible for `Best in Agentic AI`.

---

## 1. Model Philosophy

The hackathon version should avoid a bloated model stack.

The best version is:

- narrow models for perception and context
- explicit scoring for triage
- a prompt-driven orchestrator that interprets the user's question and decides what tools to call
- visible chain of thought for every investigation
- tool calls that are motivated by what the user asked and what evidence is missing

This is more stable, easier to demo, and easier for judges to understand.

---

## 2. Recommended Categories

Urban Legend only needs five model or reasoning categories for the winning slice:

1. thermal evidence (satellite-to-thermal conversion model)
2. perception (object and surface classification)
3. context comparison (neighbor analysis)
4. orchestrator reasoning (Gemini — interprets prompt, picks tools, produces chain of thought)
5. answer generation (structured response with recommendations)

---

## 3. Thermal Evidence

### Role

<<<<<<< Updated upstream
The satellite-to-thermal conversion model is already built and should be treated as stable infrastructure.
=======
The thermal generator is already built and should be treated as stable infrastructure.
In this repo, that generator is the `hybrid_thermal` model integrated under `backend/app/thermal/hybrid_thermal`.
>>>>>>> Stashed changes

### Use in the Hackathon

- convert satellite imagery to thermal representation
- provide the thermal image for UI overlay display
- extract thermal data for the analysis pipeline
- expose hotspot-level thermal evidence when the agent requests it

### Strategic Rule

Do not treat thermal generation as the headline.

It is a strong upstream component, but the product is the prompt-driven investigation built on top of it.

In the chain of thought, thermal should look like a tool the agent decided to consult because it needed heat evidence to answer the user's question.

See `docs/hybrid_thermal.md` for the canonical folder layout and local artifact rules.

---

## 4. Perception Models

Perception turns a hotspot crop into structured evidence.

### 4.1 Object Detection or Classification

Purpose:

- identify whether the hotspot is a roof, road, parking lot, vegetation edge, HVAC area, or another coarse class

Output:

- object label
- confidence

### 4.2 Surface or Material Inference

Purpose:

- estimate a coarse material class relevant to intervention logic

Examples:

- dark roof
- reflective roof
- asphalt
- concrete
- vegetation

Output:

- material class
- confidence

### 4.3 Hotspot Feature Extraction

Purpose:

- summarize area, intensity, contrast, and other simple hotspot signals

This can be mostly heuristic.

Output:

- structured hotspot features used by the scorer

---

## 5. Context Comparison

Urban heat only becomes actionable when interpreted relative to context.

### Purpose

- compare the hotspot to nearby similar structures
- determine whether it is expected or anomalous
- check whether the signal is consistent across nearby crops or related images

### Possible Inputs

- embeddings
- nearby region stats
- metadata such as land use or urban type

### Output

- neighbor comparison summary
- anomaly evidence

This is one of the strongest differentiators in the project.

---

## 6. Orchestrator Reasoning (Gemini)

The orchestrator is the agentic center of the system.

Its job is not to classify images directly.

Its job is to:

- interpret the user's prompt to understand what they are asking
- examine the available data context for the region
- decide what tools to call and in what order to answer the question
- execute tools and gather evidence
- reason over the evidence and decide if more is needed
- produce a structured answer with the full chain of thought visible

### Prompt-Driven Behavior

The agent's investigation path is determined by the user's question, not by a fixed pipeline. Different questions lead to different tool usage patterns.

Example:

- "What should I fix first?" -> agent scans all hotspots, scores them, ranks them
- "Are there HVAC issues?" -> agent focuses on mechanical equipment hotspots
- "Why is this corner hot?" -> agent examines a specific area, identifies causes

### Available Tools

- `inspect_object`
- `request_thermal_evidence`
- `infer_surface`
- `compare_neighbors`
- `check_consistency`
- `score_hotspot`
- `discard_hotspot`
- `finalize_hotspot`
- `list_hotspot_candidates`
- `get_region_summary`
- `lookup_location`

Keep this space constrained.

The more constrained it is, the more believable and legible the chain of thought becomes.

### Conversational Context

The agent maintains session context across follow-up questions. It can reference prior chain of thought and findings when answering follow-ups.

---

## 7. Scoring and Ranking

Not every important component needs to be learned.

For the hackathon, these should be explicit and explainable.

### 7.1 Severity Score

Inputs:

- thermal intensity
- hotspot area
- surface cues

Output:

- severity score from 0 to 1

### 7.2 Anomaly Score

Inputs:

- hotspot features
- context comparison
- local baseline
- optional nearby consistency signals

Output:

- anomaly score from 0 to 1

### 7.3 Confidence Score

Inputs:

- perception confidence
- context strength
- consistency of evidence
- source coverage quality
- whether enough evidence was gathered

Output:

- overall confidence score from 0 to 1

### 7.4 Ranker

Inputs:

- severity
- anomaly
- confidence
- intervention category

Output:

- Top 3 ranked hotspots

This should be deterministic for the hackathon.

---

## 8. Answer Generation

This layer turns the agent's investigation into a structured response to the user's prompt.

The answer should:

- directly address what the user asked
- reference specific hotspots and evidence gathered during chain of thought
- include ranked recommendations when the question calls for prioritization
- cite confidence and coverage factors when relevant

Example:

> This roof is unusually hot relative to nearby roofs and appears to use a dark surface, making it a strong cool-roof retrofit candidate. I checked 12 comparable roofs in the area and this one ranks in the 83rd percentile for heat intensity.

This does not need to be fancy. It needs to be clear and grounded in the evidence the agent gathered.

---

## 9. What Should Be Heuristic vs Learned

### Should Be Model-Based

- thermal generation (satellite-to-thermal conversion)
- object detection or classification
- coarse material inference
- context embeddings if already available
- orchestrator reasoning (Gemini)

### Should Be Heuristic or Deterministic

- hotspot proposal
- severity scoring
- anomaly weighting
- confidence aggregation
- final ranking

This split is ideal for a hackathon because it maximizes stability and explainability.

It also makes the chain of thought more legible: learned models produce evidence, deterministic logic turns that evidence into prioritization.

---

## 10. Recommended Output Schema

```json
{
  "prompt": "What should I fix first in this area?",
  "chain_of_thought": [
    {"step_type": "reasoning", "summary": "User wants prioritized interventions. Scanning all candidates."},
    {"step_type": "tool_call", "tool_name": "inspect_object", "summary": "Identified commercial roof"},
    {"step_type": "tool_call", "tool_name": "request_thermal_evidence", "summary": "Intensity 0.87"},
    {"step_type": "tool_call", "tool_name": "score_hotspot", "summary": "Anomaly: 0.82, Severity: 0.76"}
  ],
  "answer": "The commercial roof at the northeast corner is the highest-priority intervention...",
  "top_recommendation": {
    "hotspot_id": "hs_07",
    "object_type": "commercial roof",
    "severity_score": 0.84,
    "anomaly_score": 0.71,
    "overall_confidence": 0.78,
    "recommended_action": "cool-roof retrofit",
    "priority_rank": 1,
    "why": [
      "high thermal concentration",
      "large exposed roof area",
      "hotter than nearby similar structures"
    ]
  }
}
```

---

## 11. Final Model Rule

If time gets tight, do not add more models.

Instead, strengthen the visibility of:

- the agent interpreting the user's question
- evidence-request decisions in the chain of thought
- context comparison
- rejection logic
- the final answer with clear reasoning

Those are the pieces that make the system feel agentic.
