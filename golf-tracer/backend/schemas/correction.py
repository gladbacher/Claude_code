from __future__ import annotations

from pydantic import BaseModel, Field


class ManualCorrection(BaseModel):
    frame: int
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)
    delete: bool = False  # if True, remove tracking point at this frame


class CorrectionPatch(BaseModel):
    corrections: list[ManualCorrection]
