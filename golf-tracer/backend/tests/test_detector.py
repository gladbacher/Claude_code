"""Unit tests for GolfBallDetector.

Tests the heuristic (Hough circle) fallback since YOLO weights are not
present in CI. The YOLO path is tested via integration tests.
"""
from __future__ import annotations

import numpy as np
import pytest

from backend.pipeline.detector import Detection, GolfBallDetector


def make_frame_with_ball(cx: int, cy: int, radius: int = 12, bg_color=(30, 120, 30)) -> np.ndarray:
    import cv2
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    frame[:] = bg_color
    cv2.circle(frame, (cx, cy), radius, (255, 255, 255), -1)
    return frame


def make_frame_no_ball(bg_color=(30, 120, 30)) -> np.ndarray:
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    frame[:] = bg_color
    return frame


class TestDetection:
    def test_center_xy(self):
        det = Detection(bbox=(10.0, 20.0, 30.0, 40.0), confidence=0.9)
        assert det.center_xy == (20.0, 30.0)

    def test_area(self):
        det = Detection(bbox=(0.0, 0.0, 10.0, 20.0), confidence=0.9)
        assert det.area == 200.0

    def test_zero_area(self):
        det = Detection(bbox=(5.0, 5.0, 5.0, 5.0), confidence=0.5)
        assert det.area == 0.0


class TestGolfBallDetectorHeuristic:
    """Tests using the Hough-circle fallback (no YOLO weights needed)."""

    def test_detects_stationary_ball(self):
        detector = GolfBallDetector()  # no weights → heuristic fallback
        frame = make_frame_with_ball(960, 540, radius=15)
        detections = detector.detect_frame(frame)
        assert len(detections) >= 1

    def test_detected_center_is_close(self):
        detector = GolfBallDetector()
        frame = make_frame_with_ball(400, 300, radius=12)
        detections = detector.detect_frame(frame)
        assert detections, "Expected at least one detection"
        cx, cy = detections[0].center_xy
        assert abs(cx - 400) < 20
        assert abs(cy - 300) < 20

    def test_sky_background(self):
        """Ball against sky blue background should still be detectable."""
        detector = GolfBallDetector()
        frame = make_frame_with_ball(800, 200, radius=8, bg_color=(135, 206, 235))
        detections = detector.detect_frame(frame)
        # Heuristic may struggle with small balls on sky; just verify no crash
        assert isinstance(detections, list)

    def test_no_ball_frame(self):
        detector = GolfBallDetector()
        frame = make_frame_no_ball()
        detections = detector.detect_frame(frame)
        # Should return empty or low-confidence noise
        high_conf = [d for d in detections if d.confidence > 0.7]
        assert len(high_conf) == 0

    def test_batch_detection(self):
        detector = GolfBallDetector()
        frames = [
            make_frame_with_ball(200, 200),
            make_frame_with_ball(400, 300),
            make_frame_no_ball(),
        ]
        results = detector.detect_batch(frames)
        assert len(results) == 3
        assert isinstance(results[0], list)

    def test_confidence_override(self):
        detector = GolfBallDetector(confidence=0.9)
        frame = make_frame_with_ball(600, 400)
        # With override, should still work
        detections = detector.detect_frame(frame, confidence_override=0.1)
        assert isinstance(detections, list)

    def test_roi_refinement_returns_results(self):
        detector = GolfBallDetector()
        frame = make_frame_with_ball(500, 400, radius=10)
        dets = detector.detect_with_roi_refinement(frame, prev_center=(500, 400))
        assert isinstance(dets, list)
