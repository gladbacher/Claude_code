from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import get_settings
from ...db.database import get_db
from ...db.models import Export, Job
from ...schemas.export import ExportConfig, ExportStatus
from ...services.export_service import export_service

router = APIRouter(prefix="/jobs", tags=["export"])


@router.post("/{job_id}/export", response_model=ExportStatus, status_code=201)
async def trigger_export(
    job_id: str,
    payload: ExportConfig,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> ExportStatus:
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "done":
        raise HTTPException(status_code=409, detail="Job must be complete before export")

    export = Export(
        job_id=job_id,
        tracer_config=payload.tracer_config.model_dump(),
    )
    db.add(export)
    await db.commit()
    await db.refresh(export)

    background_tasks.add_task(
        export_service.render,
        job_id,
        export.id,
        payload.tracer_config.model_dump(),
    )

    return ExportStatus(
        id=export.id,
        job_id=job_id,
        status=export.status,
        created_at=export.created_at,
    )


@router.get("/{job_id}/exports/{export_id}", response_model=ExportStatus)
async def get_export_status(
    job_id: str,
    export_id: str,
    db: AsyncSession = Depends(get_db),
) -> ExportStatus:
    result = await db.execute(
        select(Export).where(Export.id == export_id, Export.job_id == job_id)
    )
    export = result.scalar_one_or_none()
    if export is None:
        raise HTTPException(status_code=404, detail="Export not found")

    download_url = None
    if export.status == "done" and export.storage_path:
        download_url = f"/exports/{export.id}/download"

    return ExportStatus(
        id=export.id,
        job_id=export.job_id,
        status=export.status,
        download_url=download_url,
        created_at=export.created_at,
    )


exports_router = APIRouter(prefix="/exports", tags=["export"])


@exports_router.get("/{export_id}/download")
async def download_export(
    export_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    settings = get_settings()
    result = await db.execute(select(Export).where(Export.id == export_id))
    export = result.scalar_one_or_none()
    if export is None or export.status != "done":
        raise HTTPException(status_code=404, detail="Export not ready")

    output_path = settings.export_dir / f"{export_id}.mp4"
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Export file not found")

    return FileResponse(
        str(output_path),
        media_type="video/mp4",
        filename=f"golf-tracer-{export_id[:8]}.mp4",
    )
