# Team and Contributions

UrbanLens was built by a four-person team for the WashU Google Build with AI hackathon. This page summarizes the project as a team artifact, not a single-person portfolio piece.

The commit history and Devpost notes show work across frontend design, Google Maps capture, backend orchestration, agent/tool behavior, ThermalGen model work, scoring, and portfolio hardening.

## Contributors

### [@tioluwani-enoch](https://github.com/tioluwani-enoch)

Led much of the frontend application work: map-centered UI, side panels, visual analysis flow, and overall user experience. Tioluwani also pushed the idea of using live Google Maps satellite imagery as the primary input, reducing reliance on bulky static datasets and making the demo easier to understand.

Representative areas:

- Google Maps selection and interaction flow
- UI/UX direction and sidebar analysis surfaces
- satellite-to-analysis frontend handoff
- visual presentation of ranked findings and recommendations

### [@GALGALLOR](https://github.com/GALGALLOR)

Owned the ThermalGen/model side of the project: adapting the pre-existing ThermalGen approach for urban environments, improving object-level heat pattern handling, and building preprocessing paths between RGB and thermal imagery.

Representative areas:

- ThermalGen / U-Net model adaptation
- RGB-to-thermal preprocessing and alignment
- model inference integration points
- thermal overlay and satellite/thermal toggling work

### [@shuja-waraich-03](https://github.com/shuja-waraich-03)

Built agent and backend functionality around tool use: prompt/tool updates, backend setup, API work, and the investigation loop that turns a user question into tool-backed analysis.

Representative areas:

- backend setup and API work
- agent loop and tool-calling behavior
- prompt/tool iteration
- live investigation flow and answer generation

### [@postigodev](https://github.com/postigodev)

Worked across backend contracts, scoring/ranking, frontend/backend integration, provider-neutral planning paths, and portfolio hardening after the hackathon. The emphasis was making the system legible, deterministic where it needed to be, and easier to run/review.

Representative areas:

- resource-oriented analysis contracts
- capture upload workflow and backend/frontend API alignment
- hotspot scoring and ranking flow
- provider-neutral LLM and optional voice briefing paths
- deterministic smoke/demo artifacts, setup docs, CI, and repo hygiene

## Shared Engineering Themes

UrbanLens is strongest as a systems project:

- custom model integration through a backend tool boundary
- Google Maps capture feeding reproducible analysis artifacts
- deterministic scoring and ranking instead of LLM-owned prioritization
- provider-neutral follow-up reasoning over stored evidence
- frontend surfaces that make a complex pipeline understandable

## AI-Assisted Development Disclosure

The team used AI-assisted development tools during the hackathon and cleanup process. The repository should be evaluated as a team-built applied-AI system: the important signals are architecture, integration, contracts, visible tradeoffs, and working end-to-end behavior.
