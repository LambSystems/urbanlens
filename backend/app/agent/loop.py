"""UrbanLens agent loop using Google ADK."""

from datetime import datetime
from pathlib import Path
from typing import Callable
from uuid import uuid4

from google.adk import Agent, Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google import genai
from google.genai import types

from ..config import GEMINI_API_KEY, GEMINI_MODEL
from ..schemas import ChainOfThoughtStep, ChainOfThoughtStepType, StepStatus
from .prompts import SYSTEM_INSTRUCTION
from .tools import ALL_TOOLS, set_region_context

import os
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

_session_service = InMemorySessionService()

# Cache uploaded file URIs so we only upload once
_uploaded_files: dict[str, str] = {}


def _upload_image(path: str) -> str:
    """Upload an image to Gemini File API and return the URI. Cached."""
    if path in _uploaded_files:
        return _uploaded_files[path]

    client = genai.Client(api_key=GEMINI_API_KEY)
    uploaded = client.files.upload(file=Path(path))
    uri = uploaded.uri
    _uploaded_files[path] = uri
    return uri


def _make_step(
    step_type: ChainOfThoughtStepType,
    summary: str,
    tool_name: str | None = None,
    status: StepStatus = StepStatus.completed,
    evidence: dict | None = None,
) -> ChainOfThoughtStep:
    return ChainOfThoughtStep(
        step_id=f"cot_{uuid4().hex[:6]}",
        step_type=step_type,
        tool_name=tool_name,
        status=status,
        summary=summary,
        evidence=evidence,
        timestamp=datetime.now(),
    )


def _build_agent() -> Agent:
    return Agent(
        name="urban_legend",
        model=GEMINI_MODEL,
        instruction=SYSTEM_INSTRUCTION,
        tools=ALL_TOOLS,
    )


def _build_message(prompt: str, region_context: dict, include_images: bool) -> types.Content:
    """Build a user message. Uses Gemini File API URIs for images (avoids bytes serialization)."""
    parts = []

    if include_images:
        rgb_path = region_context.get("rgb_image_path")
        if rgb_path and Path(rgb_path).exists():
            uri = _upload_image(rgb_path)
            parts.append(types.Part.from_uri(file_uri=uri, mime_type="image/jpeg"))

        thermal_path = region_context.get("thermal_image_path")
        if thermal_path and Path(thermal_path).exists():
            uri = _upload_image(thermal_path)
            parts.append(types.Part.from_uri(file_uri=uri, mime_type="image/jpeg"))

        center = region_context.get("center", {})
        meta = region_context.get("image_metadata", {})
        context_lines = [
            f"Location context: ({center.get('lat', '?')}, {center.get('lng', '?')})",
            "You also have an RGB aerial photo and a thermal infrared map of this area available above.",
            "Use them if they're relevant to the question — otherwise just answer with your tools and knowledge.",
        ]
        if meta.get("source_pair"):
            context_lines.append(f"Image source: DJI drone, {meta['source_pair'][0]} / {meta['source_pair'][1]}")

        parts.append(types.Part.from_text(text="\n".join(context_lines) + f"\n\n{prompt}"))
    else:
        parts.append(types.Part.from_text(text=prompt))

    return types.Content(role="user", parts=parts)


async def investigate(
    prompt: str,
    region_context: dict,
    conversation_history: list[dict] | None = None,
    on_step: Callable[[ChainOfThoughtStep], None] | None = None,
) -> dict:
    """Run a prompt-driven investigation using Google ADK."""
    set_region_context(region_context)

    agent = _build_agent()
    runner = Runner(
        agent=agent,
        app_name="urban_legend",
        session_service=_session_service,
    )

    user_id = f"user_{uuid4().hex[:8]}"
    session_id = region_context.get("_adk_session_id")

    if session_id is None:
        session = _session_service.create_session(
            app_name="urban_legend",
            user_id=user_id,
        )
        session_id = session.id
        region_context["_adk_session_id"] = session_id
        region_context["_adk_user_id"] = user_id
        include_images = True
    else:
        user_id = region_context.get("_adk_user_id", user_id)
        include_images = False

    message = _build_message(prompt, region_context, include_images)
    steps: list[ChainOfThoughtStep] = []

    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            if event.get_function_calls():
                for fc in event.get_function_calls():
                    safe_args = None
                    if fc.args:
                        safe_args = {
                            k: v for k, v in fc.args.items()
                            if isinstance(v, (str, int, float, bool, list, dict, type(None)))
                        }
                    step = _make_step(
                        ChainOfThoughtStepType.tool_call,
                        f"Called {fc.name}",
                        tool_name=fc.name,
                        evidence=safe_args,
                    )
                    steps.append(step)
                    if on_step:
                        on_step(step)

            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text and event.author == "urban_legend":
                        if event.is_final_response():
                            step = _make_step(ChainOfThoughtStepType.answer, part.text)
                        else:
                            step = _make_step(ChainOfThoughtStepType.reasoning, part.text)
                        steps.append(step)
                        if on_step:
                            on_step(step)

    except Exception as e:
        error_step = _make_step(
            ChainOfThoughtStepType.answer,
            f"Error: {str(e)}",
            status=StepStatus.error,
        )
        steps.append(error_step)
        if on_step:
            on_step(error_step)
        return {"chain_of_thought": steps, "answer": f"An error occurred: {str(e)}"}

    # Extract final answer
    answer_text = ""
    for step in reversed(steps):
        if step.step_type == ChainOfThoughtStepType.answer:
            answer_text = step.summary
            break
    if not answer_text:
        for step in reversed(steps):
            if step.step_type == ChainOfThoughtStepType.reasoning:
                answer_text = step.summary
                break
    if not answer_text:
        answer_text = "Unable to complete the analysis."

    return {"chain_of_thought": steps, "answer": answer_text}
