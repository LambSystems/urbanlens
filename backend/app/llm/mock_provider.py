from __future__ import annotations

from .base import LLMTextResult


class MockProvider:
    name = "mock"

    def generate_text(self, system_prompt: str, user_prompt: str) -> LLMTextResult:
        del system_prompt
        return LLMTextResult(
            text=f"Mock provider response for: {user_prompt}",
            provider=self.name,
        )
