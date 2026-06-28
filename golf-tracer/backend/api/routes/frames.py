from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...db.database import get_db
from ...db.models import Job
from ...services.storage import get_storage
from ...services.video_service import video_metadata_extractor

router = APIRouter(prefix="/jobs", tags=["frames"])


@router.get("/{job_id}/frames/{frame_index}")
async def get_frame(
    job_id: str,
    frame_index: int,
    db: AsyncSession = Depends(get_db),
) -> Response:
    result = await db.execute(
        select(Job).options(selectinload(Job.video)).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    if job is None or job.video is None:
        raise HTTPException(status_code=404, detail="Job or video not found")

    storage = get_storage()
    video_path = await storage.get_path(job.video.storage_path)

    try:
        jpeg_bytes = video_metadata_extractor.extract_frame_jpeg(video_path, frame_index)
    except (ValueError, Exception) as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return Response(content=jpeg_bytes, media_type="image/jpeg")
