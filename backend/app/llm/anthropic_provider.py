from __future__ import annotations

import os

import anthropic

from .base import LLMTextResult


class AnthropicProvider:
    name = "anthropic"

    def generate_text(self, system_prompt: str, user_prompt: str) -> LLMTextResult:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return LLMTextResult(text="", provider=self.name)

        model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

        try:
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model=model,
                max_tokens=512,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = message.content[0].text if message.content else ""
            return LLMTextResult(text=text.strip(), provider=self.name)
        except Exception:
            return LLMTextResult(text="", provider=self.name)
