from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import get_settings
from ...db.database import get_db
from ...db.models import Video
from ...schemas.video import VideoMetadata
from ...services.storage import get_storage
from ...services.video_service import video_metadata_extractor

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("", response_model=VideoMetadata, status_code=status.HTTP_201_CREATED)
async def upload_video(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
) -> VideoMetadata:
    settings = get_settings()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024

    # Stream-read to check size
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum {settings.max_upload_size_mb} MB.",
        )

    import io
    storage = get_storage()
    storage_path = await storage.save(io.BytesIO(content), file.filename or "video.mp4", prefix="uploads")

    # Extract metadata
    video_path = await storage.get_path(storage_path)
    try:
        meta = video_metadata_extractor.extract(video_path)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not extract video metadata: {exc}",
        )

    video = Video(
        filename=file.filename or "video.mp4",
        storage_path=storage_path,
        fps=meta.get("fps"),
        duration_s=meta.get("duration_s"),
        width=meta.get("width"),
        height=meta.get("height"),
        frame_count=meta.get("frame_count"),
        file_size_bytes=meta.get("file_size_bytes", len(content)),
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)

    return VideoMetadata.model_validate(video)


@router.get("/{video_id}", response_model=VideoMetadata)
async def get_video(video_id: str, db: AsyncSession = Depends(get_db)) -> VideoMetadata:
    from sqlalchemy import select
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoMetadata.model_validate(video)
