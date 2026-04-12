import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# Provider: "anthropic" or "gemini"
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic")

# Anthropic
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

DATA_DIR = Path(__file__).parent / "data"
RGB_IMAGE_PATH = DATA_DIR / "475.JPG"
THERMAL_IMAGE_PATH = DATA_DIR / "475 (1).JPG"
TRAIN_TEST_SPLIT_PATH = DATA_DIR / "train_test_split.json"
