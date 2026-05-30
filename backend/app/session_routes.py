from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from .agent import investigate
from .config import DEMO_MODE
from .demo_data import build_demo_investigation_response
from .schemas import (
    CreateSessionRequest,
    InvestigationResponse,
    Session,
    SessionMessage,
    SessionStatus,
    UserPromptRequest,
)
from .session_store import session_store

session_router = APIRouter(prefix="/session", tags=["session"])


@session_router.post("", response_model=Session)
def create_session(payload: CreateSessionRequest) -> Session:
    return session_store.create_session(payload.center, payload.radius_m)


@session_router.get("/{session_id}", response_model=Session)
def get_session(session_id: str) -> Session:
    try:
        return session_store.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")


@session_router.get("/{session_id}/messages", response_model=list[SessionMessage])
def get_messages(session_id: str) -> list[SessionMessage]:
    try:
        return session_store.get_messages(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")


@session_router.post("/{session_id}/prompt", response_model=InvestigationResponse)
async def send_prompt(session_id: str, payload: UserPromptRequest) -> InvestigationResponse:
    try:
        session_store.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

    region_context = session_store.get_region_context(session_id)

    # Save user message
    session_store.finalize_message(session_id, "user", payload.prompt)

    # Build conversation history from prior messages
    messages = session_store.get_messages(session_id)
    history = None
    if len(messages) > 1:  # more than just the current user message
        history = [{"role": m.role, "content": m.content} for m in messages[:-1]]

    # Run investigation
    session_store.set_status(session_id, SessionStatus.investigating)

    if DEMO_MODE:
        response = build_demo_investigation_response(session_id, payload.prompt)
        for step in response.chain_of_thought:
            session_store.append_chain_step(session_id, step)
        session_store.finalize_message(
            session_id,
            "assistant",
            response.answer,
            chain_of_thought=response.chain_of_thought,
        )
        session_store.set_status(session_id, SessionStatus.answered)
        return response

    try:
        result = await investigate(
            prompt=payload.prompt,
            region_context=region_context,
            conversation_history=history,
            on_step=lambda step: session_store.append_chain_step(session_id, step),
        )
    except Exception as e:
        session_store.set_status(session_id, SessionStatus.answered)
        raise HTTPException(status_code=500, detail=f"Investigation error: {str(e)}")

    # Save assistant response
    session_store.finalize_message(
        session_id,
        "assistant",
        result["answer"],
        chain_of_thought=result["chain_of_thought"],
    )
    session_store.set_status(session_id, SessionStatus.answered)

    return InvestigationResponse(
        session_id=session_id,
        prompt=payload.prompt,
        chain_of_thought=result["chain_of_thought"],
        answer=result["answer"],
    )


@session_router.post("/{session_id}/prompt/stream")
async def send_prompt_stream(session_id: str, payload: UserPromptRequest):
    """SSE streaming endpoint — chain of thought steps arrive as they happen."""
    try:
        session_store.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

    region_context = session_store.get_region_context(session_id)

    session_store.finalize_message(session_id, "user", payload.prompt)

    messages = session_store.get_messages(session_id)
    history = None
    if len(messages) > 1:
        history = [{"role": m.role, "content": m.content} for m in messages[:-1]]

    session_store.set_status(session_id, SessionStatus.investigating)

    if DEMO_MODE:
        response = build_demo_investigation_response(session_id, payload.prompt)

        async def demo_event_generator():
            for step in response.chain_of_thought:
                session_store.append_chain_step(session_id, step)
                yield {"event": "step", "data": step.model_dump_json()}
            session_store.finalize_message(
                session_id,
                "assistant",
                response.answer,
                chain_of_thought=response.chain_of_thought,
            )
            session_store.set_status(session_id, SessionStatus.answered)
            yield {
                "event": "done",
                "data": json.dumps({
                    "session_id": session_id,
                    "prompt": payload.prompt,
                    "answer": response.answer,
                }),
            }

        return EventSourceResponse(demo_event_generator())

    queue: asyncio.Queue = asyncio.Queue()

    def on_step(step):
        queue.put_nowait(step)

    async def event_generator():
        task = asyncio.create_task(
            investigate(
                prompt=payload.prompt,
                region_context=region_context,
                conversation_history=history,
                on_step=on_step,
            )
        )

        while not task.done():
            try:
                step = await asyncio.wait_for(queue.get(), timeout=0.5)
                yield {"event": "step", "data": step.model_dump_json()}
            except asyncio.TimeoutError:
                yield {"event": "ping", "data": ""}

        # Drain remaining
        while not queue.empty():
            step = queue.get_nowait()
            yield {"event": "step", "data": step.model_dump_json()}

        result = task.result()

        session_store.finalize_message(
            session_id,
            "assistant",
            result["answer"],
            chain_of_thought=result["chain_of_thought"],
        )
        session_store.set_status(session_id, SessionStatus.answered)

        yield {
            "event": "done",
            "data": json.dumps({
                "session_id": session_id,
                "prompt": payload.prompt,
                "answer": result["answer"],
            }),
        }

    return EventSourceResponse(event_generator())


@session_router.get("/{session_id}/chain-of-thought")
def get_live_chain(session_id: str):
    """Poll current chain of thought steps during an active investigation."""
    try:
        steps = session_store.get_live_chain(session_id)
        return {"steps": [s.model_dump() for s in steps]}
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
