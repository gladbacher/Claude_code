from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...db.database import get_db
from ...db.models import Job, TrackingResult, Video
from ...schemas.job import JobCreate, JobResult, JobStatus, TrackingPoint
from ...services.job_queue import queue

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobStatus, status_code=status.HTTP_201_CREATED)
async def create_job(payload: JobCreate, db: AsyncSession = Depends(get_db)) -> JobStatus:
    # Validate video exists
    result = await db.execute(select(Video).where(Video.id == payload.video_id))
    video = result.scalar_one_or_none()
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")

    job = Job(video_id=payload.video_id, sport=payload.sport)
    db.add(job)
    await db.commit()
    await db.refresh(job)

    await queue.enqueue(job.id)

    return JobStatus.model_validate(job)


@router.get("/{job_id}/status", response_model=JobStatus)
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)) -> JobStatus:
    job = await _get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus.model_validate(job)


@router.get("/{job_id}/result", response_model=JobResult)
async def get_job_result(job_id: str, db: AsyncSession = Depends(get_db)) -> JobResult:
    job = await _get_job_with_result(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "done":
        raise HTTPException(status_code=409, detail=f"Job not complete (status: {job.status})")
    if job.tracking_result is None:
        raise HTTPException(status_code=404, detail="No tracking result found")

    tr = job.tracking_result
    tracking_points = [TrackingPoint(**pt) for pt in tr.tracking_points]

    return JobResult(
        job_id=job_id,
        impact_frame=tr.impact_frame,
        fps=tr.fps,
        frame_count=tr.frame_count,
        width=tr.width,
        height=tr.height,
        coverage=tr.coverage,
        tracking_points=tracking_points,
    )


async def _get_job(db: AsyncSession, job_id: str) -> Job | None:
    result = await db.execute(select(Job).where(Job.id == job_id))
    return result.scalar_one_or_none()


async def _get_job_with_result(db: AsyncSession, job_id: str) -> Job | None:
    result = await db.execute(
        select(Job)
        .options(selectinload(Job.tracking_result))
        .where(Job.id == job_id)
    )
    return result.scalar_one_or_none()
