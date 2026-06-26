from __future__ import annotations

from pydantic import BaseModel, Field


class TracerConfig(BaseModel):
    color: str = "#FF6B00"
    thickness: int = Field(default=4, ge=1, le=20)
    opacity: float = Field(default=0.85, ge=0.0, le=1.0)
    glow_radius: int = Field(default=8, ge=0, le=40)
    glow_opacity: float = Field(default=0.4, ge=0.0, le=1.0)
    trail_length: int = Field(default=30, ge=1, le=300)
    fade_tail: bool = True
    fade_exponent: float = Field(default=2.0, ge=0.5, le=5.0)
