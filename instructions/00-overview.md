# UrbanLens Build Specs

This folder is the implementation guide for the current pivot.

Read in this order:

1. `00-overview.md`
2. `01-shared-contract.md`
3. your engineer-specific file

This is the full hackathon MVP, not the long-term platform vision.

---

## Product Canon

UrbanLens is:

> an agent for localized environmental investigation

The user selects a place, the frontend captures that locality, and the backend agent investigates it using internal tools.

`ThermalGen` is the standout custom tool inside the system.

The system should not be framed as:

- a standalone thermal generator
- a generic map chatbot
- a broad “ask anything about the world” assistant

---

## Winning Loop

`select locality -> send capture -> agent calls tools -> visible reasoning -> grounded answer`

If work does not strengthen that flow, cut it.

---

## Primary Target

- `Best in Agentic AI`

## Secondary Target

- `Best Design using v0`

---

## Stack

- `Anthropic` as default LLM right now
- `Gemini` supported through `LLMProvider` if it stabilizes
- `Google Maps API`
- `Python + FastAPI`
- `React + TypeScript`
- `ThermalGen`
- `v0` for selected UI surfaces only

---

## Non-Negotiables

- the product is the agent, not the thermal model alone
- `ThermalGen` must appear as a real tool call
- the agent should also use at least one supporting tool
- input should be capture-based from the frontend
- the output should be analysis-first, not chat-first
- follow-up questions happen on top of an existing analysis
- ranking should remain deterministic and explainable

Do not reopen product-scope debates during implementation unless they directly block the winning loop.
