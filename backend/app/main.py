from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import router
from .session_routes import session_router


app = FastAPI(
    title="UrbanLens API",
    version="0.3.0",
    description="Agentic locality investigation backend with analysis and session flows.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(session_router)

data_dir = Path(__file__).resolve().parents[1] / "data"
if data_dir.exists():
    app.mount("/data", StaticFiles(directory=str(data_dir)), name="data")

thermal_assets_dir = data_dir / "hybrid_thermal"
if thermal_assets_dir.exists():
    app.mount("/thermal-assets", StaticFiles(directory=str(thermal_assets_dir)), name="thermal-assets")

captures_dir = data_dir / "captures"
captures_dir.mkdir(parents=True, exist_ok=True)
app.mount("/captures", StaticFiles(directory=str(captures_dir)), name="captures")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}