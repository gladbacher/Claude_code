"""Shared pytest fixtures for Golf Tracer backend tests."""
from __future__ import annotations

import asyncio
import io
from pathlib import Path
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Use in-memory SQLite for tests
TEST_DB_URL = "sqlite+aiosqlite://"


@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture
def sample_frame() -> np.ndarray:
    """A 1080p BGR frame with a white circle simulating a golf ball."""
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    frame[:] = (30, 120, 30)  # grass green background
    import cv2
    cv2.circle(frame, (960, 540), 12, (255, 255, 255), -1)  # white ball
    return frame


@pytest.fixture
def sample_frames_stationary(sample_frame) -> list[np.ndarray]:
    """10 frames with a stationary ball at (960, 540)."""
    import cv2
    frames = []
    for _ in range(10):
        f = sample_frame.copy()
        frames.append(f)
    return frames


@pytest.fixture
def sample_frames_with_impact(sample_frame) -> list[np.ndarray]:
    """20 frames: 8 stationary, 1 impact blur, 11 flight."""
    import cv2
    frames = []

    # Stationary frames (ball at 960, 540)
    for i in range(8):
        f = np.zeros((1080, 1920, 3), dtype=np.uint8)
        f[:] = (30, 120, 30)
        cv2.circle(f, (960, 540), 12, (255, 255, 255), -1)
        frames.append(f)

    # Impact frame (motion blur — no clear ball)
    frames.append(np.zeros((1080, 1920, 3), dtype=np.uint8))

    # Flight frames (ball moves right and up)
    for i in range(11):
        f = np.zeros((1080, 1920, 3), dtype=np.uint8)
        f[:] = (135, 206, 235)  # sky blue
        bx = 960 + (i + 1) * 30
        by = 540 - (i + 1) * 15
        cv2.circle(f, (bx, by), max(3, 12 - i), (255, 255, 255), -1)
        frames.append(f)

    return frames


@pytest.fixture
def mock_detector():
    """Detector that returns pre-scripted detections."""
    from backend.pipeline.detector import Detection, GolfBallDetector
    detector = MagicMock(spec=GolfBallDetector)

    def detect_frame(frame, confidence_override=None):
        import cv2
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(
            cv2.GaussianBlur(gray, (9, 9), 2),
            cv2.HOUGH_GRADIENT, 1, 20,
            param1=50, param2=20, minRadius=2, maxRadius=50,
        )
        if circles is None:
            return []
        circles = np.round(circles[0]).astype(int)
        return [
            Detection(bbox=(c[0]-c[2], c[1]-c[2], c[0]+c[2], c[1]+c[2]), confidence=0.9)
            for c in circles
        ]

    detector.detect_frame.side_effect = detect_frame
    detector.detect_batch.side_effect = lambda frames, **kw: [detect_frame(f) for f in frames]
    return detector


@pytest_asyncio.fixture
async def async_client():
    """Async HTTP test client with in-memory DB."""
    import os
    os.environ["DATABASE_URL"] = TEST_DB_URL

    from backend.main import create_app
    from backend.db.database import create_tables

    app = create_app()
    await create_tables()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
