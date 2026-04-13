from __future__ import annotations

import os

from .mock_provider import MockProvider


def get_llm_provider():
    provider = (os.getenv("LLM_PROVIDER") or "mock").strip().lower()
    if provider == "gemini":
        from .gemini_provider import GeminiProvider

        return GeminiProvider()
    if provider == "featherless":
        from .featherless_provider import FeatherlessProvider

        return FeatherlessProvider()
    if provider == "mock":
        return MockProvider()
    if provider == "anthropic":
        try:
            from .anthropic_provider import AnthropicProvider
        except ImportError:
            return MockProvider()
        return AnthropicProvider()
    return MockProvider()
