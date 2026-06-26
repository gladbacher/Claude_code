"""Orchestrates the CV pipeline for a job, writing progress to the database."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db.database import AsyncSessionLocal
from ..db.models import Job, TrackingResult
from ..models.model_registry import registry
from ..pipeline.pipeline import GolfTracerPipeline, PipelineConfig
from ..services.storage import get_storage

log = logging.getLogger(__name__)


class PipelineService:
    async def run(self, job_id: str) -> None:
        async with AsyncSessionLocal() as db:
            job = await _get_job(db, job_id)
            if job is None:
                log.error(f"Job {job_id} not found")
                return

            await _set_status(db, job, "processing", 0.0, "Starting")

        settings = get_settings()

        try:
            storage = get_storage()

            async with AsyncSessionLocal() as db:
                job = await _get_job(db, job_id)
                video_path = await storage.get_path(job.video.storage_path)

            config = PipelineConfig(
                sport=job.sport if hasattr(job, "sport") else "golf",
                device=settings.device,
                confidence=settings.yolo_confidence_threshold,
                impact_confidence=settings.yolo_impact_confidence,
                weights_path=registry._resolve_weights("golf", settings.yolo_model_size),
            )

            pipeline = GolfTracerPipeline(config)

            async def progress_cb(value: float, message: str) -> None:
                async with AsyncSessionLocal() as db:
                    j = await _get_job(db, job_id)
                    if j:
                        await _set_status(db, j, "processing", value, message)

            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: pipeline.process(video_path, on_progress=None),
            )

            async with AsyncSessionLocal() as db:
                job = await _get_job(db, job_id)
                tracking_points_data = [
                    {
                        "frame": pt.frame,
                        "x": pt.x,
                        "y": pt.y,
                        "confidence": pt.confidence,
                        "is_interpolated": pt.is_interpolated,
                        "is_manual": pt.is_manual,
                    }
                    for pt in result.tracking_points
                ]

                tr = TrackingResult(
                    job_id=job_id,
                    impact_frame=result.impact_frame,
                    fps=result.fps,
                    frame_count=result.frame_count,
                    width=result.width,
                    height=result.height,
                    coverage=result.coverage,
                    tracking_points=tracking_points_data,
                )
                db.add(tr)
                await _set_status(db, job, "done", 1.0, f"Processed {len(result.tracking_points)} tracking points")
                await db.commit()

        except Exception as exc:
            log.exception(f"Pipeline failed for job {job_id}")
            async with AsyncSessionLocal() as db:
                job = await _get_job(db, job_id)
                if job:
                    await _set_status(db, job, "error", 0.0, None, str(exc))
                    await db.commit()


async def _get_job(db: AsyncSession, job_id: str) -> Job | None:
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Job).options(selectinload(Job.video)).where(Job.id == job_id)
    )
    return result.scalar_one_or_none()


async def _set_status(
    db: AsyncSession,
    job: Job,
    status: str,
    progress: float,
    message: str | None,
    error: str | None = None,
) -> None:
    job.status = status
    job.progress = progress
    job.progress_message = message
    if error:
        job.error_message = error
    if status == "processing" and job.started_at is None:
        job.started_at = datetime.now(timezone.utc)
    if status in ("done", "error"):
        job.completed_at = datetime.now(timezone.utc)
    await db.commit()


pipeline_service = PipelineService()
