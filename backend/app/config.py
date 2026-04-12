import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from backend/ directory
load_dotenv(Path(__file__).parent.parent / ".env")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

DATA_DIR = Path(__file__).parent / "data"
RGB_IMAGE_PATH = DATA_DIR / "475.JPG"
THERMAL_IMAGE_PATH = DATA_DIR / "475 (1).JPG"
TRAIN_TEST_SPLIT_PATH = DATA_DIR / "train_test_split.json"
