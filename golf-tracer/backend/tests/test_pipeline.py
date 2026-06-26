"""Integration tests for GolfTracerPipeline.

Uses synthetic video generated in-memory — no real video file needed.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest

from backend.pipeline.pipeline import GolfTracerPipeline, PipelineConfig
from backend.pipeline.smoother import TrackPoint


def _make_synthetic_video(path: Path, n_frames: int = 60, fps: float = 30.0) -> None:
    """Create a minimal MP4 with a golf ball arc using FFmpeg."""
    import subprocess
    import os

    # Create frames as raw BGR
    frames_dir = path.parent / "frames"
    frames_dir.mkdir(exist_ok=True)

    import cv2

    for i in range(n_frames):
        frame = np.zeros((480, 854, 3), dtype=np.uint8)

        if i < 10:
            # Stationary ball
            cv2.circle(frame, (427, 240), 10, (255, 255, 255), -1)
            frame[:] = (30, 100, 30)  # grass
            cv2.circle(frame, (427, 240), 10, (255, 255, 255), -1)
        elif i < 12:
            # Impact blur — empty frame
            frame[:] = (30, 100, 30)
        else:
            # Flight — ball moves right and up
            t = (i - 12) / max(n_frames - 12, 1)
            bx = int(427 + t * 300)
            by = int(240 - 150 * t * (1 - t) * 4)
            r = max(2, 10 - int(t * 7))
            frame[:] = (135, 206, 235)  # sky
            cv2.circle(frame, (bx, by), r, (255, 255, 255), -1)

        cv2.imwrite(str(frames_dir / f"frame_{i:04d}.png"), frame)

    # Encode to MP4
    cmd = [
        "ffmpeg", "-y", "-r", str(fps),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-vcodec", "libx264", "-crf", "23", "-pix_fmt", "yuv420p",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True)

    # Cleanup frame images
    import shutil
    shutil.rmtree(frames_dir, ignore_errors=True)

    if result.returncode != 0:
        pytest.skip(f"FFmpeg not available: {result.stderr.decode()}")


class TestGolfTracerPipeline:
    @pytest.fixture
    def synthetic_video(self, tmp_path):
        video_path = tmp_path / "test_swing.mp4"
        _make_synthetic_video(video_path, n_frames=60, fps=30.0)
        return video_path

    def test_pipeline_runs_without_error(self, synthetic_video):
        config = PipelineConfig(device="cpu")
        pipeline = GolfTracerPipeline(config)
        result = pipeline.process(synthetic_video)
        assert result is not None

    def test_tracking_points_are_normalized(self, synthetic_video):
        config = PipelineConfig(device="cpu")
        pipeline = GolfTracerPipeline(config)
        result = pipeline.process(synthetic_video)

        for pt in result.tracking_points:
            assert 0.0 <= pt.x <= 1.0, f"x={pt.x} out of range"
            assert 0.0 <= pt.y <= 1.0, f"y={pt.y} out of range"

    def test_impact_frame_detected(self, synthetic_video):
        config = PipelineConfig(device="cpu")
        pipeline = GolfTracerPipeline(config)
        result = pipeline.process(synthetic_video)

        # Impact is around frame 10-12 in our synthetic video
        assert 0 <= result.impact_frame <= 20

    def test_tracking_coverage(self, synthetic_video):
        config = PipelineConfig(device="cpu")
        pipeline = GolfTracerPipeline(config)
        result = pipeline.process(synthetic_video)

        # Should have reasonable coverage over the flight portion
        assert result.coverage >= 0.3, f"Coverage too low: {result.coverage}"

    def test_processing_time_reasonable(self, synthetic_video):
        config = PipelineConfig(device="cpu")
        pipeline = GolfTracerPipeline(config)
        result = pipeline.process(synthetic_video)

        # 2-second clip should process quickly on CPU in CI
        assert result.processing_time_s < 120.0

    def test_result_metadata(self, synthetic_video):
        config = PipelineConfig(device="cpu")
        pipeline = GolfTracerPipeline(config)
        result = pipeline.process(synthetic_video)

        assert result.fps > 0
        assert result.frame_count > 0
        assert result.width > 0
        assert result.height > 0

    def test_progress_callback(self, synthetic_video):
        config = PipelineConfig(device="cpu")
        pipeline = GolfTracerPipeline(config)

        progress_values = []
        def on_progress(value, message):
            progress_values.append(value)

        result = pipeline.process(synthetic_video, on_progress=on_progress)
        assert len(progress_values) >= 2
        assert progress_values[-1] == 1.0
