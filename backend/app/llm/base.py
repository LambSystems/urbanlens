from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class LLMTextResult:
    text: str
    provider: str


class LLMProvider(Protocol):
    name: str

    def generate_text(self, system_prompt: str, user_prompt: str) -> LLMTextResult:
        ...
