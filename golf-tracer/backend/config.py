from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite+aiosqlite:///./golf_tracer.db"

    # Storage
    storage_backend: Literal["local", "s3"] = "local"
    upload_dir: Path = Path("./uploads")
    export_dir: Path = Path("./exports")
    max_upload_size_mb: int = 500

    # S3 (when storage_backend=s3)
    s3_bucket: str = "golf-tracer-videos"
    s3_endpoint_url: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_default_region: str = "us-east-1"

    # CV / Model
    use_gpu: Literal["auto", "true", "false"] = "auto"
    yolo_model_size: Literal["n", "m", "l", "x"] = "n"
    yolo_confidence_threshold: float = 0.4
    yolo_impact_confidence: float = 0.2
    models_dir: Path = Path("./models/weights")

    # API
    cors_origins: list[str] = ["http://localhost:8081", "exp://localhost:8081"]
    max_concurrent_jobs: int = 2

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def device(self) -> str:
        if self.use_gpu == "false":
            return "cpu"
        if self.use_gpu == "true":
            return "cuda"
        # auto
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"


@lru_cache
def get_settings() -> Settings:
    return Settings()
