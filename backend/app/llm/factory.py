from __future__ import annotations

import os

from .anthropic_provider import AnthropicProvider
from .featherless_provider import FeatherlessProvider
from .gemini_provider import GeminiProvider
from .mock_provider import MockProvider


def get_llm_provider():
    provider = (os.getenv("LLM_PROVIDER") or "anthropic").strip().lower()
    if provider == "gemini":
        return GeminiProvider()
    if provider == "featherless":
        return FeatherlessProvider()
    if provider == "mock":
        return MockProvider()
    return AnthropicProvider()
