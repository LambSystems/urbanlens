import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# Deploy-safe mode for hosted portfolio demos. It keeps the API contracts
# stable while bypassing live LLM calls and heavy ThermalGen inference.
DEMO_MODE = os.environ.get("DEMO_MODE", "").strip().lower() in {"1", "true", "yes", "on"}

# Provider: "anthropic", "gemini", "featherless", or "mock"
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic")

# Anthropic
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
