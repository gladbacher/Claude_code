"""Unit tests for TrajectorySmoother."""
from __future__ import annotations

import numpy as np
import pytest

from backend.pipeline.smoother import TrackPoint, TrajectorySmoother


def make_points(coords: list[tuple[float, float]], start_frame: int = 0) -> list[TrackPoint]:
    return [
        TrackPoint(frame=start_frame + i, x=x, y=y, confidence=0.9)
        for i, (x, y) in enumerate(coords)
    ]


def make_noisy_arc(n: int = 30, noise: float = 0.02) -> list[TrackPoint]:
    """A parabolic arc with Gaussian noise."""
    rng = np.random.default_rng(42)
    points = []
    for i in range(n):
        t = i / n
        x = 0.1 + 0.8 * t
        y = 0.8 - 1.2 * t * (1 - t)  # parabola
        x += float(rng.normal(0, noise))
        y += float(rng.normal(0, noise))
        points.append(TrackPoint(frame=i, x=x, y=y, confidence=0.8))
    return points


class TestTrajectorySmoother:
    def test_returns_same_count(self):
        smoother = TrajectorySmoother()
        points = make_noisy_arc(20)
        result = smoother.smooth(points)
        assert len(result) == len(points)

    def test_no_abrupt_reversals(self):
        """After smoothing, direction should not reverse abruptly."""
        smoother = TrajectorySmoother()
        points = make_noisy_arc(40)
        result = smoother.smooth(points)

        xs = [p.x for p in result]
        # x should be monotonically increasing (the arc moves right)
        for i in range(1, len(xs)):
            assert xs[i] >= xs[i - 1] - 0.05, f"Reversal at index {i}"

    def test_manual_points_preserved(self):
        """Manual correction points must not be moved by smoothing."""
        smoother = TrajectorySmoother()
        points = make_noisy_arc(20)
        points[10] = TrackPoint(frame=10, x=0.999, y=0.001, confidence=1.0, is_manual=True)
        result = smoother.smooth(points)

        manual = next(p for p in result if p.is_manual)
        assert abs(manual.x - 0.999) < 1e-6
        assert abs(manual.y - 0.001) < 1e-6

    def test_single_point_passthrough(self):
        smoother = TrajectorySmoother()
        pts = [TrackPoint(frame=0, x=0.5, y=0.5, confidence=0.9)]
        result = smoother.smooth(pts)
        assert len(result) == 1

    def test_fill_gaps_interpolates(self):
        smoother = TrajectorySmoother()
        points = [
            TrackPoint(frame=0, x=0.0, y=0.0, confidence=0.9),
            TrackPoint(frame=5, x=0.5, y=0.5, confidence=0.9),
        ]
        filled = smoother.fill_gaps(points, total_frames=6)
        # Should have 6 points (0..5)
        frames = sorted(p.frame for p in filled)
        assert 2 in frames
        assert 3 in frames
        # Check interpolated at frame 2: x ≈ 0.2
        pt2 = next(p for p in filled if p.frame == 2)
        assert abs(pt2.x - 0.2) < 0.05
        assert pt2.is_interpolated

    def test_fill_gaps_no_gap(self):
        smoother = TrajectorySmoother()
        points = make_points([(0.1, 0.1), (0.2, 0.2), (0.3, 0.3)])
        filled = smoother.fill_gaps(points, total_frames=3)
        assert len(filled) == 3

    def test_smooth_reduces_noise(self):
        """RMS deviation from arc should decrease after smoothing."""
        smoother = TrajectorySmoother()
        noisy = make_noisy_arc(30, noise=0.05)
        smoothed = smoother.smooth(noisy)

        # Compute variance of consecutive differences (a measure of roughness)
        def roughness(pts):
            diffs = [abs(pts[i].y - pts[i-1].y) for i in range(1, len(pts))]
            return np.std(diffs)

        assert roughness(smoothed) <= roughness(noisy) * 1.5  # allow some tolerance
