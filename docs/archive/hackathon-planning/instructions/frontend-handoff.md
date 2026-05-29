# Frontend Handoff
## Backend Fields To Consume Right Now

This file is the fast integration handoff for Engineer 1.

Use it together with:

- [frontend/lib/api.ts](/C:/Users/akuma/repos/thermalgen/frontend/lib/api.ts)
- [backend/API_EXAMPLES.md](/C:/Users/akuma/repos/thermalgen/backend/API_EXAMPLES.md)

---

## Canonical Endpoints

- `POST /analysis/from-capture-upload`
- `GET /analysis/{region_id}`
- `GET /analysis/{region_id}/events`
- `POST /analysis/{region_id}/questions`
- `POST /analysis/{region_id}/voice-briefing`

---

## Region Fields

Use these from `analysis.region`:

- `display_name`
  use as the sidebar header title
- `center`
  use for map recentering if needed
- `coverage_score`
  optional support metric
- `summary`
  use for small stats like candidates / discarded / finalized

Recommended usage:

- top of sidebar:
  - region title = `display_name`
  - subtitle = area or quick status

---

## Hotspot Fields

Use these from each `hotspot`:

- `display_name`
  human-readable hotspot label
- `status_label`
  badge like `Recommended` or `Discarded`
- `sidebar_summary`
  primary hotspot copy
- `evidence_highlights`
  bullet list under the summary
- `tool_signals`
  compact badges showing which tools contributed
- `surface_temperature_c`
  numeric display
- `ambient_delta_c`
  numeric display
- `anomaly_score`
- `severity_score`
- `confidence_score`
- `final_rank_score`
- `recommended_action`
- `discard_reason`
- `priority_rank`
- `is_top_ranked`

Recommended usage:

### Ranking Card

- `display_name`
- `status_label`
- temperature metrics
- score bars

### Selected Hotspot Sidebar

- `display_name`
- `status_label`
- `sidebar_summary`
- `tool_signals`
- `evidence_highlights`
- recommendation or discard reason

---

## Planner Fields

Use these from `POST /analysis/{region_id}/questions`:

- `answer_title`
  planner panel title
- `answer_sections`
  bullets or short stacked paragraphs
- `answer`
  full detailed text
- `referenced_hotspot_ids`
  optional highlight hook

Recommended usage:

- title = `answer_title`
- body = `answer_sections`
- expandable detail = `answer`

Do not render only the raw `answer` if you can help it.
The structured fields are there to make the UI cleaner.

---

## Voice Briefing Fields

Use these from `POST /analysis/{region_id}/voice-briefing`:

- `audio_url`
  if present, play audio
- `summary_text`
  fallback text or transcript
- `provider`
  optional small debug label

Recommended usage:

- button: `Play briefing`
- if `audio_url` exists, play it
- if not, show `summary_text`

Voice is optional polish, not the hero interaction.

---

## UX Rules

- `sidebar_summary` is the hero text for a hotspot
- `answer_title + answer_sections` are the hero content for planner
- `tool_signals` should be visible fast
- map remains the anchor
- follow-up Q&A remains secondary to analysis

---

## Visual Priority

1. map and selected locality
2. analysis state
3. top recommendation
4. selected hotspot details
5. planner follow-up panel
6. optional voice briefing

If the UI gets crowded, preserve that order.
