"""Golf Tracer API — FastAPI application factory."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db.database import create_tables
from .db import models as _models  # noqa: F401 — ensures models are registered
from .models.model_registry import registry
from .services.job_queue import queue
from .services.pipeline_service import pipeline_service
from .api.routes import videos, jobs, frames, corrections, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    # Create DB tables (idempotent)
    await create_tables()

    # Configure model registry
    registry.configure(settings.models_dir, device=settings.device)

    # Start job queue workers
    queue.set_handler(pipeline_service.run)
    await queue.start(num_workers=settings.max_concurrent_jobs)

    yield

    # Shutdown
    await queue.stop()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Golf Tracer API",
        description="Automatic golf ball detection, tracking, and tracer rendering.",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(videos.router)
    app.include_router(jobs.router)
    app.include_router(frames.router)
    app.include_router(corrections.router)
    app.include_router(export.router)
    app.include_router(export.exports_router)

    @app.get("/health")
    async def health():
        return {"status": "ok", "device": settings.device}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
