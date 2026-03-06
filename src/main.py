import logging

from fastapi import FastAPI

from src.config import settings
from src.video_ingestion.router import router as video_router

logging.basicConfig(
    level=logging.DEBUG if settings.app_env == "local" else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="Video Review API",
    description="POC – timecoded, evidence-based coaching feedback for zh-HK teaching videos",
    version="0.1.0",
)

app.include_router(video_router)


@app.get("/health", tags=["infra"])
async def health_check() -> dict:
    """Smoke-test endpoint (Workflow 01 acceptance criteria)."""
    return {"status": "ok", "env": settings.app_env}
