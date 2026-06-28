from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .tracer import TracerConfig


class ExportConfig(BaseModel):
    tracer_config: TracerConfig = TracerConfig()


class ExportStatus(BaseModel):
    id: str
    job_id: str
    status: str
    download_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
