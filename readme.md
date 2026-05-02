# UrbanLens
## Agentic Urban Explorer — Investigate Any Locality With AI

UrbanLens is an **Agentic Urban Explorer** built for the Google Build with AI Hackathon (`Best in Agentic AI` track).

Select any Location. Ask a question. The agent goes out, pulls live environmental data, analyzes thermal imagery, and comes back with grounded findings you can act on.

---

## How It Works

```
User selects a locality on the map
        ↓
"How walkable is this area in summer heat?"
        ↓
Agent decides what to investigate:
  🔧 get_weather_current → 92°F, UV index 8, humidity 65%
  🔧 get_air_quality → AQI 42 (Good), PM2.5 at 8 µg/m³
  🔧 get_walkability_score → Score 62, 4 parks, 12 transit stops
  🔧 estimate_surface_temperature → sidewalks at 135°F, shade areas at 85°F
  🔧 get_land_use → 78% impervious, 18% tree canopy
        ↓
Agent synthesizes findings into an actionable answer
with full chain of thought visible in the UI
```

Every tool call, every reasoning step, every piece of evidence — visible in real time.

---

## What it does

- **Explores** — pulls live data from real APIs (weather, air quality, land use, elevation)
- **Decides** — chooses which tools to call based on what the user actually asked
- **Investigates** — gathers evidence step by step with visible chain of thought
- **Reasons** — cross-references multiple data sources to build a complete picture
- **Answers** — returns specific, grounded findings with real numbers
- **Remembers** — follow-up questions build on prior investigation

Different questions trigger different tool combinations. The agent adapts its investigation to match what you need to know.

---

## Agent Tools (12 Live Instruments)

### Environmental Sensors (Live APIs, no keys needed)
| Tool | What it does | Source |
|---|---|---|
| `get_weather_current` | Temperature, humidity, wind, UV, cloud cover | Open-Meteo |
| `get_air_quality` | AQI, PM2.5, PM10, ozone, NO2 levels | Open-Meteo |
| `get_ndvi_estimate` | Vegetation health and green cover % | Open-Meteo + OSM |
| `get_historical_temperature_comparison` | Is today hotter than the 5-year average? | Open-Meteo Archive |

### Terrain Mapping (Live from OpenStreetMap)
| Tool | What it does | Source |
|---|---|---|
| `get_land_use` | Buildings, roads, green spaces, impervious surface % | OSM Overpass |
| `get_walkability_score` | Amenities, transit, parks, pedestrian paths, comfort | OSM Overpass |
| `get_elevation_profile` | Elevation, drainage risk, heat trapping assessment | Open-Meteo |
| `get_flood_risk` | Composite risk from elevation + surfaces + water + rain | Open-Meteo + OSM |

### Analysis Instruments
| Tool | What it does | Source |
|---|---|---|
| `get_solar_potential` | Rooftop solar estimate — generation, cost, payback, CO2 | Calculated from live solar data |
| `estimate_surface_temperature` | How hot do different materials get (asphalt, roof, grass) | EPA/DOE research data |
| `estimate_intervention_impact` | Cost, savings, CO2 reduction for cool roofs, trees, etc. | EPA/DOE/GSA data |
| `lookup_image_metadata` | Drone imagery dataset info (671 DJI thermal+visual pairs) | Local dataset |

### Custom Tools (Internal)
| Tool | What it does |
|---|---|
| `generate_thermal_overlay` | Run ThermalGen on captured satellite imagery |
| `propose_capture_hotspots` | Identify heat hotspot candidates from thermal evidence |
| `analyze_heat_risk` | Estimate structural heat-risk drivers for a location |

---

## Chain of Thought — Fully Visible

Every investigation streams its reasoning to the UI in real time:

```
💭 User wants to know about heat resilience. I'll check current conditions and land cover.
🔧 get_weather_current → 92°F, feels like 97°F, UV index 8
🔧 get_land_use → 23 buildings, 78% impervious, 3 green spaces
🔧 get_air_quality → AQI 42 (Good), ozone slightly elevated
💭 High temperature with low green cover. Let me check what interventions would help.
🔧 estimate_intervention_impact("cool roof", 15000) → $52,500, saves 15% energy
🔧 estimate_intervention_impact("tree planting", 10000) → $15,000, 50yr lifespan
✅ Final answer with ranked recommendations grounded in live data
```

Not a canned animation — these are the agent's actual reasoning steps as they happen.

---

## Thermal Vision

UrbanLens has a unique capability most agents don't: **ThermalGen**.

When aerial RGB and thermal infrared images are available, the agent can visually compare them to identify which structures generate the most heat. The thermal evidence grounds sustainability recommendations in what the data actually shows.

- RGB aerial photo → what's there (buildings, roads, vegetation)
- Thermal infrared map → what's hot (bright = high heat, dark = cool)
- Agent decides when to reference thermal imagery based on the question

Thermal is evidence the agent uses when relevant — not a forced analysis on every prompt.

---

## Example Interactions

**"What should we fix first here?"**
→ Agent checks weather, scans land use, estimates surface temps, costs out interventions, ranks by impact

**"Is this area walkable in summer?"**
→ Agent checks walkability score, current temperature, shade availability, air quality, comfort features

**"Should we put solar on these rooftops?"**
→ Agent checks solar radiation, estimates system size and generation, calculates payback and CO2 offset

**"What's the flood risk here?"**
→ Agent checks elevation, impervious surfaces, nearby water, recent precipitation, computes composite risk

**"How does today compare to historical temps?"**
→ Agent pulls current temperature and compares to 5-year average for this exact date

---

## Architecture

```
Frontend (Next.js + Google Maps)
  → User selects region, types question
  → Streams chain of thought in real time
  → Displays answer with tool evidence

Backend (FastAPI + Google ADK / Anthropic)
  → Session management + conversation history
  → Agent orchestrator dispatches to tools
  → Tools call live APIs (Open-Meteo, OpenStreetMap)
  → ThermalGen produces thermal evidence from imagery
  → Returns structured response with chain of thought

LLM Providers (swappable):
  → Anthropic Claude (primary — reliable tool use)
  → Google Gemini via ADK (secondary)
  → Featherless AI (open-model path — Qwen 7B)
```

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind, Radix UI, Framer Motion |
| Map | Google Maps API with region capture |
| Backend | Python, FastAPI, Pydantic |
| Agent | Google ADK / Anthropic Claude with tool use |
| LLM Providers | Anthropic, Gemini, Featherless (provider-neutral) |
| Live Data | Open-Meteo (weather, AQI, solar), OpenStreetMap Overpass (land use, amenities) |
| Thermal | ThermalGen — custom satellite-to-thermal inference |
| Voice | ElevenLabs (optional demo layer) |
| UI Polish | v0 for selected surfaces |

---

## Running Locally

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Add your API key to backend/.env
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Configure `backend/.env`:
```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Team

4-engineer team with AI-assisted development (Claude Code + Codex).

- Engineer 1: Frontend, map capture, chain of thought UI
- Engineer 2: Backend, agent orchestrator, session management
- Engineer 3: ThermalGen, perception, evidence pipeline
- Engineer 4: Tools, scoring, live API integrations

---

## The Pitch

> Point at a place. Ask a question. Watch the agent investigate with real data. Get an answer you can act on.

That's UrbanLens.
