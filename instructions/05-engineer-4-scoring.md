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

Engineer 4 has more freedom than Engineer 1, but it is not unlimited freedom.

The freedom is in:

- how to combine signals
- how to shape rationale
- how to tune discard thresholds

The constraints are:

- output fields must stay stable
- ranking must stay explainable
- the result must support demo storytelling

## Inputs You Should Expect

- thermal evidence from `ThermalGen`
- supporting evidence from `Heat Risk Profiler`
- optional perception cues
- capture quality or evidence-quality hints

You should not assume:

- perfect physical truth
- calibrated real-world temperatures
- unlimited metadata

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

Those field names are the contract. Do not reopen them casually.

## Practical Freedom Guidance

Good areas to explore:

- making confidence reflect agreement between ThermalGen and Heat Risk Profiler
- tuning severity so the top recommendation tells a clean story
- improving `why` bullets so the answer sounds grounded and useful

Bad areas to explore:

- inventing extra score families no one will display
- adding hidden complexity that the agent cannot explain
- changing ranking philosophy every hour

## Strong Discard Examples

- thermal concern not supported by broader risk profile
- visible risk factors are weak despite warm appearance
- insufficient evidence to recommend intervention

## Strong Recommendation Examples

- elevated thermal evidence confirmed by visible heat-risk drivers
- repeated or strong concern over a large exposed roof area
- good enough confidence to prioritize inspection or mitigation

## Golden Demo Requirement

Scoring should preserve a narratively clean result:

- one clearly strong top finding
- one believable discard
- one or two secondary findings at most

If the scores produce a confusing story, fix the scores or seeds.

## Success Condition

The agent can show why one result mattered, why another was rejected, and why the chosen answer is worth trusting.
