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
- coverage-aware confidence logic

## Immediate Goal

Turn hotspot evidence into stable, explainable scoring and ranking decisions that the agent can use during investigation.

## First Hour

1. Define anomaly gate.
2. Define severity score.
3. Define confidence score.
4. Define discard reasons.
5. Define final ranking score.
6. Package outputs so Engineer 2 can plug them into the agent tool dispatch.

## Core Heuristic

- anomaly filters
- severity orders
- confidence modulates

Confidence should include source coverage quality, not just model certainty.

Confidence should also be penalized when metadata quality or geolocation certainty is weak.

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
- lower confidence when source coverage is partial or weak

## Example Discard Reasons

- expected road heat profile
- not hotter than nearby comparable roofs
- low-confidence signal after investigation

## How Your Code Gets Called

The agent orchestrator calls your code through tools:

- `compare_neighbors` -> `scoring/context.py`
- `check_consistency` -> `scoring/context.py`
- `score_hotspot` -> `scoring/ranker.py` (which calls anomaly, severity, confidence)

When the user asks a question and the agent decides it needs scoring or context comparison, it calls your functions. Your output appears as a chain of thought step in the UI.

## Handoff to Engineer 2

Provide either:

- pure functions Engineer 2 can call from the tool registry, or
- scored hotspot payloads with exact output fields

## Success Condition

By hour 2, the agent can call your scoring tools during investigation and get back real scores that drive discard/finalize decisions. The chain of thought shows why one hotspot was discarded and another became Top 1.
