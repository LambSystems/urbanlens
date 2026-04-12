# Urban Legend — Agent Orchestrator
# Routes to Anthropic or Gemini based on LLM_PROVIDER config

from ..config import LLM_PROVIDER


async def investigate(prompt, region_context, conversation_history=None, on_step=None):
    if LLM_PROVIDER == "anthropic":
        from .anthropic_loop import investigate_anthropic
        return await investigate_anthropic(prompt, region_context, conversation_history, on_step)
    else:
        from .loop import investigate as investigate_gemini
        return await investigate_gemini(prompt, region_context, conversation_history, on_step)
