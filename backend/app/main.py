from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

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

data_dir = Path(__file__).resolve().parents[1] / "data"
if data_dir.exists():
    app.mount("/data", StaticFiles(directory=str(data_dir)), name="data")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
