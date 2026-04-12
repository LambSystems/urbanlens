# Engineer 4
## Context, Scoring, and Ranking

Owner:

- neighbor comparison
- consistency checks
- anomaly scoring
- severity scoring
- confidence scoring
- discard logic
- final ranking logic

## Immediate Goal

Turn hotspot evidence into stable, explainable ranking decisions.

## First Hour

1. Define anomaly gate.
2. Define severity score.
3. Define confidence score.
4. Define discard reasons.
5. Define final ranking score.
6. Package outputs so Engineer 2 can plug them into traces and results.

## Core Heuristic

- anomaly filters
- severity orders
- confidence modulates

Gate:

```text
if anomaly_score < anomaly_threshold:
    discard
```

Ranking:

```text
final_rank_score = severity_score * confidence_score
```

## Required Outputs

- `anomaly_score`
- `severity_score`
- `confidence_score`
- `final_rank_score`
- `discard_reason` when applicable
- `why` explanation bullets

## Example Discard Reasons

- expected road heat profile
- not hotter than nearby comparable roofs
- low-confidence signal after investigation

## Handoff to Engineer 2

Provide either:

- pure functions Engineer 2 can call, or
- scored hotspot payloads with exact output fields

## Success Condition

By hour 2, backend can rank hotspots consistently and explain why one was discarded and another became Top 1.
