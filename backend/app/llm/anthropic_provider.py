from __future__ import annotations

import os
import base64

try:
    import anthropic
except ImportError:  # Optional provider dependency for local mock-only runs.
    anthropic = None

from .base import LLMTextResult


class AnthropicProvider:
    name = "anthropic"

    def generate_text(self, system_prompt: str, user_prompt: str) -> LLMTextResult:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or anthropic is None:
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

    def classify_hotspot_image(self, image_bytes: bytes, mime_type: str, prompt: str) -> dict:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or anthropic is None:
            return {"text": "", "provider": self.name}

        model = os.getenv("ANTHROPIC_VISION_MODEL", "claude-sonnet-4-20250514")

        try:
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model=model,
                max_tokens=400,
                system="You classify satellite hotspot crops and return strict JSON only.",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": mime_type,
                                    "data": base64.b64encode(image_bytes).decode("utf-8"),
                                },
                            },
                        ],
                    }
                ],
            )
            text = ""
            if message.content:
                blocks: list[str] = []
                for block in message.content:
                    block_text = getattr(block, "text", None)
                    if block_text:
                        blocks.append(block_text)
                text = "\n".join(blocks).strip()
            return {"text": text, "provider": self.name}
        except Exception:
            return {"text": "", "provider": self.name}
