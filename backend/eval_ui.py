"""Urban Legend — Streamlit evaluation UI."""

import json
import requests
import streamlit as st

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Urban Legend Eval", layout="wide")
st.title("Urban Legend — Agent Evaluation")

# Sidebar: session management + images
with st.sidebar:
    st.header("Session")

    if "session_id" not in st.session_state:
        st.session_state.session_id = None
        st.session_state.messages = []

    col1, col2 = st.columns(2)
    lat = col1.number_input("Lat", value=38.627, format="%.4f")
    lng = col2.number_input("Lng", value=-90.1994, format="%.4f")
    radius = st.number_input("Radius (m)", value=120, min_value=1, max_value=1000)

    if st.button("New Session", type="primary", use_container_width=True):
        r = requests.post(f"{API_BASE}/session", json={
            "center": {"lat": lat, "lng": lng},
            "radius_m": radius,
        })
        if r.status_code == 200:
            st.session_state.session_id = r.json()["session_id"]
            st.session_state.messages = []
            st.success(f"Session: {st.session_state.session_id}")
        else:
            st.error(f"Failed: {r.text}")

    if st.session_state.session_id:
        st.caption(f"Active: `{st.session_state.session_id}`")

    st.divider()
    st.header("Reference Images")
    try:
        from app.config import RGB_IMAGE_PATH, THERMAL_IMAGE_PATH
        if RGB_IMAGE_PATH.exists():
            st.image(str(RGB_IMAGE_PATH), caption="RGB Aerial", use_container_width=True)
        if THERMAL_IMAGE_PATH.exists():
            st.image(str(THERMAL_IMAGE_PATH), caption="Thermal Map", use_container_width=True)
    except Exception:
        st.caption("Start API server to load images")

# Main area: chat
if not st.session_state.session_id:
    st.info("Create a session in the sidebar to start.")
    st.stop()

# Render conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and msg.get("chain_of_thought"):
            with st.expander("Chain of Thought", expanded=False):
                for step in msg["chain_of_thought"]:
                    stype = step["step_type"]
                    tool = step.get("tool_name") or ""
                    summary = step["summary"]

                    if stype == "tool_call":
                        st.markdown(f"🔧 **{tool}**")
                        if step.get("evidence"):
                            st.json(step["evidence"])
                    elif stype == "reasoning":
                        st.markdown(f"💭 {summary[:200]}")
                    elif stype == "answer":
                        st.markdown(f"✅ Final answer")

# Chat input
if prompt := st.chat_input("Ask about urban sustainability..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Investigating..."):
            r = requests.post(
                f"{API_BASE}/session/{st.session_state.session_id}/prompt",
                json={"prompt": prompt},
                timeout=120,
            )

        if r.status_code == 200:
            data = r.json()
            answer = data["answer"]
            chain = data.get("chain_of_thought", [])
            tools_used = [s.get("tool_name") for s in chain if s["step_type"] == "tool_call"]

            st.markdown(answer)

            # Show chain of thought
            if chain:
                with st.expander(f"Chain of Thought ({len(chain)} steps, tools: {tools_used})", expanded=True):
                    for step in chain:
                        stype = step["step_type"]
                        tool = step.get("tool_name") or ""
                        summary = step["summary"]

                        if stype == "tool_call":
                            st.markdown(f"🔧 **{tool}**")
                            if step.get("evidence"):
                                st.json(step["evidence"])
                        elif stype == "reasoning":
                            st.markdown(f"💭 {summary[:300]}")
                        elif stype == "answer":
                            st.markdown("✅ **Final answer generated**")

            # Save to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "chain_of_thought": chain,
            })
        else:
            error = r.json().get("detail", r.text)
            st.error(f"Error: {error}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Error: {error}",
            })
