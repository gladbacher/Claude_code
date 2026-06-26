"""Renders the tracer overlay onto the original video and produces the export."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..config import get_settings
from ..db.database import AsyncSessionLocal
from ..db.models import Export, Job, TrackingResult
from ..pipeline.smoother import TrackPoint
from ..rendering.frame_composer import FrameComposer
from ..rendering.tracer_renderer import TracerConfig
from ..rendering.video_writer import render_video
from ..services.storage import get_export_storage, get_storage

log = logging.getLogger(__name__)


class ExportService:
    async def render(self, job_id: str, export_id: str, tracer_config_data: dict) -> None:
        settings = get_settings()

        async with AsyncSessionLocal() as db:
            export = await _get_export(db, export_id)
            job = await _get_job(db, job_id)
            if not export or not job or not job.tracking_result:
                log.error(f"Export {export_id}: missing job or tracking result")
                await _set_export_status(db, export, "error")
                return

            tracking_points = [
                TrackPoint(
                    frame=pt["frame"],
                    x=pt["x"],
                    y=pt["y"],
                    confidence=pt["confidence"],
                    is_interpolated=pt.get("is_interpolated", False),
                    is_manual=pt.get("is_manual", False),
                )
                for pt in job.tracking_result.tracking_points
            ]
            tr = job.tracking_result
            video_storage_path = job.video.storage_path

        try:
            storage = get_storage()
            export_storage = get_export_storage()
            video_path = await storage.get_path(video_storage_path)

            cfg = TracerConfig(**tracer_config_data)
            composer = FrameComposer(cfg)

            output_path = settings.export_dir / f"{export_id}.mp4"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            import asyncio
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: render_video(
                    input_video=video_path,
                    output_video=output_path,
                    composer=composer,
                    tracking_points=tracking_points,
                    fps=tr.fps,
                    width=tr.width,
                    height=tr.height,
                ),
            )

            # Save export file
            with open(output_path, "rb") as f:
                export_key = await export_storage.save(f, f"{export_id}.mp4", prefix="exports")

            async with AsyncSessionLocal() as db:
                exp = await _get_export(db, export_id)
                exp.storage_path = export_key
                exp.status = "done"
                exp.completed_at = datetime.now(timezone.utc)
                await db.commit()

        except Exception as exc:
            log.exception(f"Export {export_id} failed")
            async with AsyncSessionLocal() as db:
                exp = await _get_export(db, export_id)
                if exp:
                    await _set_export_status(db, exp, "error")


async def _get_export(db: AsyncSession, export_id: str) -> Export | None:
    result = await db.execute(select(Export).where(Export.id == export_id))
    return result.scalar_one_or_none()


async def _get_job(db: AsyncSession, job_id: str) -> Job | None:
    result = await db.execute(
        select(Job)
        .options(selectinload(Job.video), selectinload(Job.tracking_result))
        .where(Job.id == job_id)
    )
    return result.scalar_one_or_none()


async def _set_export_status(db: AsyncSession, export: Export, status: str) -> None:
    export.status = status
    if status in ("done", "error"):
        export.completed_at = datetime.now(timezone.utc)
    await db.commit()


export_service = ExportService()
