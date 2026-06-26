from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VideoMetadata(BaseModel):
    id: str
    filename: str
    fps: Optional[float] = None
    duration_s: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    frame_count: Optional[int] = None
    file_size_bytes: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}
