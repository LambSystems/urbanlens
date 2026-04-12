from fastapi import FastAPI

from .routes import router


app = FastAPI(
    title="ThermalGen API",
    version="0.1.0",
    description="Hackathon MVP backend for agentic urban heat triage.",
)

app.include_router(router)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
