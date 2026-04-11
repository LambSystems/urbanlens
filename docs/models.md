# ThermalGen V2 Models
## Model and Reasoning Stack for the Winning Slice

This document describes the model stack for the hackathon version of ThermalGen.

The guiding rule is:

> models produce evidence, the agent produces decisions

That distinction is what makes the project credible for `Best in Agentic AI`.

---

## 1. Model Philosophy

The hackathon version should avoid a bloated model stack.

The best version is:

- narrow models for perception and context
- explicit scoring for triage
- a constrained orchestrator for decision-making
- a clean planner or explanation layer for output
- tool calls that are motivated by missing evidence

This is more stable, easier to demo, and easier for judges to understand.

---

## 2. Recommended Categories

ThermalGen only needs five model or reasoning categories for the winning slice:

1. thermal evidence
2. perception
3. context comparison
4. orchestrator reasoning
5. ranking and explanation

---

## 3. Thermal Evidence

### Role

The thermal generator is already built and should be treated as stable infrastructure.

### Use in the Hackathon

- align thermal output with RGB
- use it to propose candidate hotspots
- derive heat-related cues for scoring
- expose hotspot-level thermal evidence on demand

### Strategic Rule

Do not treat thermal generation as the headline.

It is a strong upstream component, but the product is the decision layer built on top of it.

In the investigation trace, thermal should look like a tool the agent decided to use.

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

## 6. Orchestrator Reasoning

The orchestrator is the agentic center of the system.

Its job is not to classify images directly.

Its job is to decide:

- what evidence to request next
- whether evidence is sufficient
- whether to discard or escalate
- when to finalize a hotspot

### Recommended Action Space

- `inspect_object`
- `request_thermal_evidence`
- `infer_surface`
- `compare_neighbors`
- `check_consistency`
- `score_hotspot`
- `discard_hotspot`
- `finalize_hotspot`

Keep this space constrained.

The more constrained it is, the more believable and legible the investigation trace becomes.

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
- whether enough evidence was gathered before finalization

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

## 8. Explanation Layer

This layer turns structured evidence into a short explanation for judges and users.

Example:

> This roof is unusually hot relative to nearby roofs and appears to use a dark surface, making it a strong cool-roof retrofit candidate.

This does not need to be fancy. It needs to be clear.

---

## 9. What Should Be Heuristic vs Learned

### Should Be Model-Based

- thermal generation
- object detection or classification
- coarse material inference
- context embeddings if already available
- orchestrator reasoning

### Should Be Heuristic or Deterministic

- hotspot proposal
- severity scoring
- anomaly weighting
- confidence aggregation
- final ranking

This split is ideal for a hackathon because it maximizes stability and explainability.

It also makes the agent trace more legible: learned models produce evidence, deterministic logic turns that evidence into prioritization.

---

## 10. Recommended Output Schema

```json
{
  "hotspot_id": "hs_07",
  "object_type": "commercial roof",
  "object_confidence": 0.88,
  "material_type": "dark membrane roofing",
  "material_confidence": 0.74,
  "severity_score": 0.84,
  "anomaly_score": 0.71,
  "overall_confidence": 0.78,
  "recommended_action": "inspect for cool-roof retrofit",
  "priority_rank": 1,
  "why": [
    "high thermal concentration",
    "large exposed roof area",
    "hotter than nearby similar structures"
  ]
}
```

This schema is enough to drive the UI, the ranking panel, and the final recommendation card.

---

## 11. Final Model Rule

If time gets tight, do not add more models.

Instead, strengthen the visibility of:

- object evidence
- evidence-request decisions
- context comparison
- rejection logic
- ranking logic

Those are the pieces that make the system feel agentic.
