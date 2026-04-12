from __future__ import annotations

import os

from .base import LLMTextResult


class FeatherlessProvider:
    name = "featherless"

    def generate_text(self, system_prompt: str, user_prompt: str) -> LLMTextResult:
        del system_prompt
        api_key = os.getenv("FEATHERLESS_API_KEY")
        if not api_key:
            return LLMTextResult(text="", provider=self.name)

        del user_prompt
        return LLMTextResult(text="", provider=self.name)
