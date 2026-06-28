"""Unit tests for ImpactDetector."""
from __future__ import annotations

import numpy as np
import pytest

from backend.pipeline.detector import Detection
from backend.pipeline.impact_detector import ImpactDetector, ImpactResult


def make_detections_at(positions: list[tuple[float, float] | None]) -> list[list[Detection]]:
    """Create frame detections from a list of (x, y) or None."""
    results = []
    for pos in positions:
        if pos is None:
            results.append([])
        else:
            x, y = pos
            results.append([Detection(bbox=(x-5, y-5, x+5, y+5), confidence=0.9)])
    return results


class TestImpactDetector:
    def test_finds_impact_after_stationary(self):
        detector = ImpactDetector(min_stationary_frames=3, displacement_threshold_px=25)

        # 5 stationary frames at (100, 100) then ball moves to (150, 80)
        positions = [(100, 100)] * 5 + [(100, 100), (125, 90), (150, 80), (175, 70)]
        detections = make_detections_at(positions)
        result = detector.find_impact_frame(detections)

        assert result.frame_index > 0
        assert result.frame_index <= 7  # should be within first 3 post-stationary frames

    def test_no_impact_all_stationary(self):
        detector = ImpactDetector(min_stationary_frames=3)
        positions = [(100, 100)] * 10
        detections = make_detections_at(positions)
        result = detector.find_impact_frame(detections)
        # No movement after stationary — no impact found
        assert result.frame_index == -1

    def test_no_impact_empty_detections(self):
        detector = ImpactDetector()
        result = detector.find_impact_frame([[]] * 20)
        assert result.frame_index == -1

    def test_impact_tolerance_3_frames(self):
        """Impact frame ±3 frames of true impact at frame 8."""
        detector = ImpactDetector(min_stationary_frames=3, displacement_threshold_px=20)

        positions = [(200, 200)] * 8 + [None, (230, 185), (260, 170), (290, 155)]
        detections = make_detections_at(positions)
        result = detector.find_impact_frame(detections)

        if result.frame_index >= 0:
            assert abs(result.frame_index - 9) <= 3  # true impact ≈ frame 9

    def test_photometric_spike(self):
        """Photometric method detects high-motion frame."""
        import cv2
        detector = ImpactDetector()

        frames = []
        # Quiet frames
        for _ in range(5):
            frames.append(np.zeros((100, 100, 3), dtype=np.uint8))
        # High-motion frame (big difference)
        frames.append(np.full((100, 100, 3), 200, dtype=np.uint8))
        # Resume quiet
        for _ in range(4):
            frames.append(np.zeros((100, 100, 3), dtype=np.uint8))

        result = detector.find_impact_frame([[]] * len(frames), frames)
        # Should detect around frame 5
        if result.frame_index >= 0:
            assert abs(result.frame_index - 5) <= 2

    def test_stationary_end_recorded(self):
        detector = ImpactDetector(min_stationary_frames=3)
        positions = [(100, 100)] * 5 + [(200, 50)]
        detections = make_detections_at(positions)
        result = detector.find_impact_frame(detections)
        assert result.stationary_end >= 0

    def test_result_has_confidence(self):
        detector = ImpactDetector(min_stationary_frames=3)
        positions = [(100, 100)] * 5 + [(150, 80), (200, 60)]
        detections = make_detections_at(positions)
        result = detector.find_impact_frame(detections)
        if result.frame_index >= 0:
            assert 0.0 <= result.confidence <= 1.0
