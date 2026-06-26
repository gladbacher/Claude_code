from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class TrackingPoint(BaseModel):
    frame: int
    x: float = Field(ge=0.0, le=1.0, description="Normalized horizontal position")
    y: float = Field(ge=0.0, le=1.0, description="Normalized vertical position")
    confidence: float = Field(ge=0.0, le=1.0)
    is_interpolated: bool = False
    is_manual: bool = False


class JobCreate(BaseModel):
    video_id: str
    sport: Literal["golf", "cricket", "baseball", "tennis", "football"] = "golf"


class JobStatus(BaseModel):
    id: str
    status: str
    progress: float
    progress_message: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobResult(BaseModel):
    job_id: str
    impact_frame: int
    fps: float
    frame_count: int
    width: int
    height: int
    coverage: float
    tracking_points: list[TrackingPoint]

    model_config = {"from_attributes": True}
