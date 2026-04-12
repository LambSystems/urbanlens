# Engineer 4
## Scoring, Ranking, and Answer Strength

Owner:

- anomaly scoring
- severity scoring
- confidence scoring
- discard logic
- final ranking logic
- recommendation strength

## Immediate Goal

Turn multi-tool evidence into stable, explainable decisions.

You are not just scoring heat.
You are scoring the strength of an investigation result.

## Inputs You Should Expect

- thermal evidence from `ThermalGen`
- supporting evidence from `Heat Risk Profiler`
- optional perception cues
- capture quality or evidence-quality hints

## Core Heuristic

- anomaly gates
- severity orders
- confidence modulates

Confidence may include:

- strength of thermal evidence
- agreement with supporting tool
- quality of capture/evidence
- clarity of visible cues

## Required Outputs

- `anomaly_score`
- `severity_score`
- `confidence_score`
- `final_rank_score`
- `discard_reason`
- `why`

## Strong Discard Examples

- thermal concern not supported by broader risk profile
- visible risk factors are weak despite warm appearance
- insufficient evidence to recommend intervention

## Strong Recommendation Examples

- elevated thermal evidence confirmed by visible heat-risk drivers
- repeated or strong concern over a large exposed roof area
- good enough confidence to prioritize inspection or mitigation

## Success Condition

The agent can show why one result mattered, why another was rejected, and why the chosen answer is worth trusting.
