from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .base import LLMTextResult


class FeatherlessProvider:
    name = "featherless"
    base_url = "https://api.featherless.ai/v1/chat/completions"

    def generate_text(self, system_prompt: str, user_prompt: str) -> LLMTextResult:
        api_key = os.getenv("FEATHERLESS_API_KEY")
        if not api_key:
            return LLMTextResult(text="", provider=self.name)

        model = os.getenv("FEATHERLESS_MODEL", "Qwen/Qwen2.5-7B-Instruct")
        referer = os.getenv("FEATHERLESS_HTTP_REFERER", "https://urbanlens.local")
        title = os.getenv("FEATHERLESS_X_TITLE", "UrbanLens")
        timeout_s = float(os.getenv("FEATHERLESS_TIMEOUT_S", "20"))

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 220,
        }
        data = json.dumps(payload).encode("utf-8")

        request = Request(
            self.base_url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": referer,
                "X-Title": title,
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=timeout_s) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError):
            return LLMTextResult(text="", provider=self.name)

        text = ""
        choices = body.get("choices") or []
        if choices:
            message = choices[0].get("message") or {}
            text = str(message.get("content") or "").strip()

        return LLMTextResult(text=text, provider=self.name)
