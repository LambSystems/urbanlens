# UrbanLens Demo
## How To Demo the New Pivot

The new demo should sell one idea clearly:

> this agent can investigate a locality using custom tools, and `ThermalGen` is the special capability that makes the answer deeper than a generic model could provide

---

## 1. Opening Message

Lead with this:

> Most map tools only show you a place. UrbanLens lets you ask questions about a locality, then the agent investigates it using custom tools, including our thermal generation tool.

Do not open with:

- “we built a thermal model”
- “we have a lot of datasets”
- “we use many APIs”

Open with:

- user intent
- agent investigation
- custom tool use

---

## 2. Golden Demo Flow

### Step 1: Select a Locality

Show:

- Google Maps region selection
- the selected bounds and area

Say:

> We start by selecting a real locality in Google Maps. The frontend captures this exact region and sends both the metadata and the screenshot to the backend.

Goal:

- establish a concrete, grounded input

### Step 2: Ask a Useful Question

Good opening prompt:

- `What should we inspect first in this area?`

Alternative prompts:

- `Why does this block look heat-risky?`
- `Where would cooling or shade interventions matter most here?`

Say:

> Now we ask the agent a locality question, not just for a heatmap, but for an investigation.

### Step 3: Show the Agent Call Tools

This is the most important moment.

The trace should make clear that the agent:

1. reads the question
2. understands what kind of evidence is needed
3. calls `ThermalGen`
4. calls at least one supporting tool, ideally `Heat Risk Profiler`
5. reasons over both outputs

Say:

> The agent is deciding which tools it needs. It calls our custom thermal model when heat evidence matters, then compares that with a broader heat-risk analysis.

### Step 4: Show a Supporting Tool

This matters because the transcript made it clear the team wants the product to feel broader than one tool.

The second visible tool should be:

- `Heat Risk Profiler`

What it should appear to do:

- explain why a place is risky in visible-environment terms
- identify likely drivers like exposed roof area, dark surfaces, low shade, or lots of pavement

Say:

> ThermalGen gives us one unique kind of evidence. Our supporting tool explains the likely visible drivers behind that result.

### Step 5: Return a Useful Answer

Show:

- recommendation card
- rationale bullets
- optional Top 3 list

A strong answer looks like:

> This locality’s highest-priority concern is the large exposed roof in the center block. Thermal evidence is elevated, and the heat-risk profile also suggests high exposure from dark roofing and low surrounding shade. This is the best first inspection target.

### Step 6: Ask a Follow-Up

Good follow-up:

- `Why did you choose that roof first?`

This proves context retention and legibility.

---

## 3. Demo Structure in 90–120 Seconds

1. Select region
2. Ask question
3. Watch visible tool-calling
4. Show `ThermalGen`
5. Show `Heat Risk Profiler`
6. Land on recommendation
7. Ask one follow-up

That is enough.

---

## 4. Demo Script

### Opening

> UrbanLens is an agent for localized environmental investigation. Instead of just showing a map, it lets you ask a question about a place and then investigates that locality using custom tools.

### Transition to Input

> We select a region in Google Maps, and the frontend sends both the region metadata and a screenshot of that exact locality to the backend.

### Transition to Agent

> Now the agent decides what tools it needs to answer the question.

### ThermalGen Moment

> This is our standout tool: ThermalGen. It gives the agent custom thermal evidence from the map imagery.

### Supporting Tool Moment

> But the product is not only thermal. The agent also uses a heat-risk profiler to explain the visible environmental drivers behind what it sees.

### Recommendation

> The result is not just a visualization. It is an answer you can act on.

---

## 5. What Judges Should Feel

By the end of the demo, judges should think:

- this is clearly agentic
- the thermal tool is genuinely differentiated
- the second tool makes the product feel broader and more useful
- the answer is grounded in visible evidence

---

## 6. Mistakes To Avoid

- presenting `ThermalGen` as the whole product
- overclaiming physical temperature truth
- making the second tool feel fake or decorative
- ending with “here is a heatmap”
- using too many tools and making the trace unreadable

---

## 7. Final Demo Rule

If time gets tight, preserve this exact sequence:

- select locality
- ask question
- agent calls `ThermalGen`
- agent calls one supporting tool
- answer with recommendation

That is the strongest version of the new pivot.
