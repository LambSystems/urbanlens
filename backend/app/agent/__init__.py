from ..config import LLM_PROVIDER


async def investigate(prompt, region_context, conversation_history=None, on_step=None):
    if LLM_PROVIDER == "anthropic":
        from .anthropic_loop import investigate_anthropic

        return await investigate_anthropic(prompt, region_context, conversation_history, on_step)
    if LLM_PROVIDER == "gemini":
        from .loop import investigate as investigate_gemini

        return await investigate_gemini(prompt, region_context, conversation_history, on_step)
    raise ValueError(
        f"Unsupported session agent provider '{LLM_PROVIDER}'. "
        "Session mode currently supports 'anthropic' or 'gemini'."
    )
