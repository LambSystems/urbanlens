from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

BACKEND_ROOT = Path(__file__).resolve().parents[1]
THERMAL_ASSET_ROOT = BACKEND_ROOT / "data" / "hybrid_thermal"
THERMAL_ASSET_ROOT.mkdir(parents=True, exist_ok=True)

try:
    from dotenv import load_dotenv

    load_dotenv(BACKEND_ROOT / ".env")
except ImportError:
    pass

from .routes import router


app = FastAPI(
    title="ThermalGen API",
    version="0.1.0",
    description="Hackathon MVP backend for agentic urban heat triage.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.mount("/thermal-assets", StaticFiles(directory=THERMAL_ASSET_ROOT), name="thermal_assets")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
