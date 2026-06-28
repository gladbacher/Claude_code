"""API tests for /videos endpoints."""
from __future__ import annotations

import io
import os

import pytest
import pytest_asyncio

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite://")


@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_upload_video_too_large(async_client):
    """Files over the limit should return 413."""
    import os
    os.environ["MAX_UPLOAD_SIZE_MB"] = "0"  # Force 0 MB limit

    # Reset settings cache so the new env var is picked up
    from backend.config import get_settings
    get_settings.cache_clear()

    # 1 byte should now exceed the limit
    response = await async_client.post(
        "/videos",
        files={"file": ("test.mp4", io.BytesIO(b"x"), "video/mp4")},
    )
    assert response.status_code == 413

    os.environ["MAX_UPLOAD_SIZE_MB"] = "500"
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_get_video_not_found(async_client):
    response = await async_client.get("/videos/nonexistent-id")
    assert response.status_code == 404
