"""Unit tests for BallTracker."""
from __future__ import annotations

import numpy as np
import pytest

from backend.pipeline.detector import Detection
from backend.pipeline.tracker import BallTracker, TrackStatus


def make_frame(color=(30, 120, 30)) -> np.ndarray:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:] = color
    return frame


def make_detection(x: float, y: float, r: float = 5, conf: float = 0.9) -> Detection:
    return Detection(bbox=(x-r, y-r, x+r, y+r), confidence=conf)


class TestBallTracker:
    def test_initializes_track_on_first_detection(self):
        tracker = BallTracker()
        frame = make_frame()
        det = make_detection(50, 50)
        state = tracker.update([det], frame, 0)
        assert state.track_id >= 0

    def test_tracks_moving_ball(self):
        tracker = BallTracker()
        frame = make_frame()

        positions = [(50 + i*3, 50 - i*2) for i in range(10)]
        states = []
        for fi, (x, y) in enumerate(positions):
            state = tracker.update([make_detection(x, y)], frame, fi)
            states.append(state)

        # All frames should have valid tracks
        valid = [s for s in states if s.track_id >= 0]
        assert len(valid) >= 8

    def test_interpolates_short_gap(self):
        """Track should survive ≤5 frame gap via optical flow."""
        tracker = BallTracker(max_lost_frames=5)
        frame = make_frame()

        # Track for 5 frames
        for fi in range(5):
            tracker.update([make_detection(50 + fi*3, 50)], frame, fi)

        # Gap of 3 frames (no detections)
        gap_states = []
        for fi in range(5, 8):
            state = tracker.update([], frame, fi)
            gap_states.append(state)

        # At least some gap states should be interpolated, not fully lost
        interpolated = [s for s in gap_states if s.is_interpolated or s.track_id >= 0]
        assert len(interpolated) >= 1

    def test_track_id_consistent(self):
        tracker = BallTracker()
        frame = make_frame()

        track_ids = set()
        for fi in range(10):
            x = 50 + fi * 2
            state = tracker.update([make_detection(x, 50)], frame, fi)
            if state.track_id >= 0:
                track_ids.add(state.track_id)

        # Should be mostly one track (maybe 2 if re-acquired)
        assert len(track_ids) <= 2

    def test_reset_clears_state(self):
        tracker = BallTracker()
        frame = make_frame()
        tracker.update([make_detection(50, 50)], frame, 0)
        tracker.reset()

        state = tracker.update([make_detection(50, 50)], frame, 0)
        assert state.track_id == 1  # fresh counter after reset

    def test_no_detection_returns_lost_state(self):
        tracker = BallTracker(max_lost_frames=0)
        frame = make_frame()
        state = tracker.update([], frame, 0)
        assert state.track_id == -1

    def test_confidence_drops_when_interpolating(self):
        tracker = BallTracker(max_lost_frames=5)
        frame = make_frame()

        for fi in range(5):
            tracker.update([make_detection(50, 50)], frame, fi)

        # One gap frame
        lost_state = tracker.update([], frame, 5)
        # If interpolated, confidence should be less than 1.0
        if lost_state.is_interpolated:
            assert lost_state.confidence < 1.0
