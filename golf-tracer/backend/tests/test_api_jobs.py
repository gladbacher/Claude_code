"""API tests for /jobs endpoints."""
from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite://")


@pytest.mark.asyncio
async def test_create_job_video_not_found(async_client):
    response = await async_client.post(
        "/jobs",
        json={"video_id": "nonexistent-video-id"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_status_not_found(async_client):
    response = await async_client.get("/jobs/nonexistent-id/status")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_result_not_found(async_client):
    response = await async_client.get("/jobs/nonexistent-id/result")
    assert response.status_code == 404
