"""Urban Legend — Agent loop using Anthropic Claude with tool use."""

import base64
import json
from datetime import datetime
from pathlib import Path
from typing import Callable
from uuid import uuid4

import anthropic

from ..config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from ..schemas import ChainOfThoughtStep, ChainOfThoughtStepType, StepStatus
from .prompts import SYSTEM_INSTRUCTION
from .tools import ALL_TOOLS, set_region_context

MAX_TOOL_CALLS = 15

# Build Anthropic tool schemas from our Python functions
def _build_tool_schemas() -> list[dict]:
    """Convert our tool functions into Anthropic tool-use format."""
    schemas = []
    for func in ALL_TOOLS:
        import inspect
        sig = inspect.signature(func)
        properties = {}
        required = []
        for name, param in sig.parameters.items():
            if name in ("self", "ctx"):
                continue
            prop = {"type": "string"}
            if param.annotation == float:
                prop = {"type": "number"}
            elif param.annotation == int:
                prop = {"type": "integer"}
            elif param.annotation == bool:
                prop = {"type": "boolean"}
            # Extract description from docstring Args section
            prop["description"] = name
            properties[name] = prop
            if param.default is inspect.Parameter.empty:
                required.append(name)

        schemas.append({
            "name": func.__name__,
            "description": (func.__doc__ or "").split("\n\n")[0].strip(),
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        })
    return schemas


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


def _load_image_base64(path: str, max_bytes: int = 4_900_000) -> tuple[str, str]:
    """Load image as base64 + media type. Resizes if over max_bytes."""
    from io import BytesIO
    from PIL import Image

    data = Path(path).read_bytes()
    if len(data) <= max_bytes:
        return base64.standard_b64encode(data).decode("utf-8"), "image/jpeg"

    # Resize to fit under limit
    img = Image.open(BytesIO(data))
    quality = 85
    while quality >= 20:
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        if buf.tell() <= max_bytes:
            return base64.standard_b64encode(buf.getvalue()).decode("utf-8"), "image/jpeg"
        quality -= 10
    # Last resort: scale down
    img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=60)
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8"), "image/jpeg"


def _dispatch_tool(name: str, args: dict) -> str:
    """Call one of our tool functions by name.

    Coerces arguments to their annotated types so Claude's JSON output
    (which may send integers as floats or strings) doesn't cause slice errors.
    """
    import inspect
    for func in ALL_TOOLS:
        if func.__name__ == name:
            sig = inspect.signature(func)
            coerced: dict = {}
            for k, v in args.items():
                param = sig.parameters.get(k)
                if param and param.annotation is not inspect.Parameter.empty:
                    try:
                        v = param.annotation(v)
                    except (TypeError, ValueError):
                        pass
                coerced[k] = v
            result = func(**coerced)
            return json.dumps(result)
    return json.dumps({"error": f"Unknown tool: {name}"})


async def investigate_anthropic(
    prompt: str,
    region_context: dict,
    conversation_history: list[dict] | None = None,
    on_step: Callable[[ChainOfThoughtStep], None] | None = None,
) -> dict:
    """Run investigation using Claude with tool use."""
    set_region_context(region_context)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    tools = _build_tool_schemas()
    steps: list[ChainOfThoughtStep] = []

    # Build messages
    messages = []

    # Add conversation history
    if conversation_history:
        for msg in conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Build current user message with images on first prompt
    user_content = []
    if not conversation_history:
        rgb_path = region_context.get("rgb_image_path")
        if rgb_path and Path(rgb_path).exists():
            b64, media = _load_image_base64(rgb_path)
            user_content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": media, "data": b64},
            })

        thermal_path = region_context.get("thermal_image_path")
        if thermal_path and Path(thermal_path).exists():
            b64, media = _load_image_base64(thermal_path)
            user_content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": media, "data": b64},
            })

        center = region_context.get("center", {})
        meta = region_context.get("image_metadata", {})
        context = f"Location: ({center.get('lat', '?')}, {center.get('lng', '?')})\n"
        context += "First image: RGB aerial photo. Second image: thermal infrared map of same area.\n"
        if meta.get("source_pair"):
            context += f"Source: DJI drone, {meta['source_pair'][0]} / {meta['source_pair'][1]}\n"
        context += f"\n{prompt}"
        user_content.append({"type": "text", "text": context})
    else:
        user_content.append({"type": "text", "text": prompt})

    messages.append({"role": "user", "content": user_content})

    # Agentic loop
    iteration = 0
    while iteration < MAX_TOOL_CALLS:
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4096,
            system=SYSTEM_INSTRUCTION,
            tools=tools,
            messages=messages,
        )

        # Process response blocks
        tool_uses = []
        assistant_content = []

        for block in response.content:
            assistant_content.append(block)

            if block.type == "text":
                step = _make_step(ChainOfThoughtStepType.reasoning, block.text)
                steps.append(step)
                if on_step:
                    on_step(step)

            elif block.type == "tool_use":
                step = _make_step(
                    ChainOfThoughtStepType.tool_call,
                    f"Called {block.name}",
                    tool_name=block.name,
                    evidence=block.input if isinstance(block.input, dict) else None,
                )
                steps.append(step)
                if on_step:
                    on_step(step)
                tool_uses.append(block)

        # Add assistant message to conversation
        messages.append({"role": "assistant", "content": assistant_content})

        # If no tool calls, we're done
        if not tool_uses:
            break

        # Execute tools and send results back
        tool_results = []
        for tu in tool_uses:
            result_str = _dispatch_tool(tu.name, tu.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": result_str,
            })

        messages.append({"role": "user", "content": tool_results})
        iteration += 1

    # Extract final answer
    answer_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            answer_text += block.text

    if not answer_text:
        answer_text = "Unable to complete the analysis."

    answer_step = _make_step(ChainOfThoughtStepType.answer, answer_text)
    steps.append(answer_step)
    if on_step:
        on_step(answer_step)

    return {"chain_of_thought": steps, "answer": answer_text}
