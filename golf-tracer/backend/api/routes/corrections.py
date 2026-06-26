from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...db.database import get_db
from ...db.models import Job, TrackingResult
from ...schemas.correction import CorrectionPatch
from ...schemas.job import JobResult, TrackingPoint

router = APIRouter(prefix="/jobs", tags=["corrections"])


@router.patch("/{job_id}/corrections", response_model=JobResult)
async def patch_corrections(
    job_id: str,
    payload: CorrectionPatch,
    db: AsyncSession = Depends(get_db),
) -> JobResult:
    result = await db.execute(
        select(Job)
        .options(selectinload(Job.tracking_result))
        .where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.tracking_result is None:
        raise HTTPException(status_code=404, detail="No tracking result to correct")

    tr = job.tracking_result
    points_by_frame: dict[int, dict] = {
        pt["frame"]: pt for pt in tr.tracking_points
    }

    for correction in payload.corrections:
        if correction.delete:
            points_by_frame.pop(correction.frame, None)
        else:
            points_by_frame[correction.frame] = {
                "frame": correction.frame,
                "x": correction.x,
                "y": correction.y,
                "confidence": 1.0,
                "is_interpolated": False,
                "is_manual": True,
            }

    tr.tracking_points = sorted(points_by_frame.values(), key=lambda p: p["frame"])
    await db.commit()

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
