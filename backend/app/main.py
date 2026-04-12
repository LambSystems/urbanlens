from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import router


app = FastAPI(
    title="UrbanLens API",
    version="0.3.0",
    description="Agentic locality investigation backend with analysis and session flows.",
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

data_dir = Path(__file__).resolve().parents[1] / "data"
if data_dir.exists():
    app.mount("/data", StaticFiles(directory=str(data_dir)), name="data")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
