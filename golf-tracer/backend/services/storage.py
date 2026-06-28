"""Storage abstraction — local filesystem or S3-compatible.

Selected via STORAGE_BACKEND env var: "local" (default) or "s3".
"""
from __future__ import annotations

import shutil
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO

from ..config import get_settings


class BaseStorage(ABC):
    @abstractmethod
    async def save(self, file: BinaryIO, filename: str, prefix: str = "") -> str:
        """Save a file; return the storage path/key."""

    @abstractmethod
    async def get_path(self, storage_path: str) -> Path:
        """Resolve a storage path to a local filesystem Path for CV processing."""

    @abstractmethod
    async def get_url(self, storage_path: str) -> str:
        """Return a URL for downloading the file."""

    @abstractmethod
    async def delete(self, storage_path: str) -> None: ...


class LocalStorage(BaseStorage):
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, file: BinaryIO, filename: str, prefix: str = "") -> str:
        uid = str(uuid.uuid4())
        suffix = Path(filename).suffix
        dest_name = f"{uid}{suffix}"
        dest = self.base_dir / prefix / dest_name
        dest.parent.mkdir(parents=True, exist_ok=True)

        if hasattr(file, "read"):
            content = file.read() if not hasattr(file, "aread") else await file.read()
            dest.write_bytes(content)
        else:
            shutil.copy2(file, dest)

        return str(dest.relative_to(self.base_dir.parent))

    async def get_path(self, storage_path: str) -> Path:
        p = self.base_dir.parent / storage_path
        if not p.exists():
            raise FileNotFoundError(f"Storage file not found: {storage_path}")
        return p

    async def get_url(self, storage_path: str) -> str:
        return f"/storage/{storage_path}"

    async def delete(self, storage_path: str) -> None:
        p = self.base_dir.parent / storage_path
        if p.exists():
            p.unlink()


class S3Storage(BaseStorage):
    def __init__(self) -> None:
        self._settings = get_settings()
        import boto3
        kwargs = dict(
            region_name=self._settings.aws_default_region,
            aws_access_key_id=self._settings.aws_access_key_id,
            aws_secret_access_key=self._settings.aws_secret_access_key,
        )
        if self._settings.s3_endpoint_url:
            kwargs["endpoint_url"] = self._settings.s3_endpoint_url
        self._client = boto3.client("s3", **kwargs)
        self._bucket = self._settings.s3_bucket

    async def save(self, file: BinaryIO, filename: str, prefix: str = "") -> str:
        uid = str(uuid.uuid4())
        suffix = Path(filename).suffix
        key = f"{prefix}/{uid}{suffix}".lstrip("/")
        content = file.read() if hasattr(file, "read") else file
        self._client.put_object(Bucket=self._bucket, Key=key, Body=content)
        return key

    async def get_path(self, storage_path: str) -> Path:
        import tempfile
        tmp = Path(tempfile.mktemp(suffix=Path(storage_path).suffix))
        self._client.download_file(self._bucket, storage_path, str(tmp))
        return tmp

    async def get_url(self, storage_path: str) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": storage_path},
            ExpiresIn=3600,
        )

    async def delete(self, storage_path: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=storage_path)


def get_storage() -> BaseStorage:
    settings = get_settings()
    if settings.storage_backend == "s3":
        return S3Storage()
    return LocalStorage(settings.upload_dir)


def get_export_storage() -> BaseStorage:
    settings = get_settings()
    if settings.storage_backend == "s3":
        return S3Storage()
    return LocalStorage(settings.export_dir)
