"""Trajectory smoother: Kalman filter → cubic spline.

Two-pass smoothing:
  1. Kalman forward pass: eliminates detection noise while preserving physics.
  2. Cubic spline interpolation: produces smooth curves even with sparse points.

The result is a trajectory that looks natural for a golf ball flight arc.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class TrackPoint:
    frame: int
    x: float
    y: float
    confidence: float
    is_interpolated: bool = False
    is_manual: bool = False


class TrajectorySmoother:
    def __init__(
        self,
        process_noise: float = 1.0,
        measurement_noise: float = 10.0,
        smoothing_factor: float = 0.5,
    ) -> None:
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
        self.smoothing_factor = smoothing_factor

    def smooth(self, points: list[TrackPoint]) -> list[TrackPoint]:
        if len(points) < 2:
            return points

        # Split into manual (locked) and auto points
        manual_indices = {p.frame: p for p in points if p.is_manual}

        # Kalman pass over all points
        kalman_pts = self._kalman_smooth(points)

        # Spline pass for sub-frame smoothness
        smoothed = self._spline_smooth(kalman_pts)

        # Reapply manual overrides (they should not be modified)
        for i, pt in enumerate(smoothed):
            if pt.frame in manual_indices:
                smoothed[i] = manual_indices[pt.frame]

        return smoothed

    def _kalman_smooth(self, points: list[TrackPoint]) -> list[TrackPoint]:
        xs = np.array([p.x for p in points], dtype=np.float64)
        ys = np.array([p.y for p in points], dtype=np.float64)

        xs_smooth = self._kalman_1d(xs)
        ys_smooth = self._kalman_1d(ys)

        return [
            TrackPoint(
                frame=p.frame,
                x=float(xs_smooth[i]),
                y=float(ys_smooth[i]),
                confidence=p.confidence,
                is_interpolated=p.is_interpolated,
                is_manual=p.is_manual,
            )
            for i, p in enumerate(points)
        ]

    def _kalman_1d(self, measurements: np.ndarray) -> np.ndarray:
        n = len(measurements)
        x = measurements[0]
        v = 0.0
        P = np.array([[100.0, 0.0], [0.0, 100.0]])
        F = np.array([[1.0, 1.0], [0.0, 1.0]])
        H = np.array([[1.0, 0.0]])
        Q = np.eye(2) * self.process_noise
        R = np.array([[self.measurement_noise]])

        state = np.array([x, v])
        result = np.zeros(n)

        for i, z in enumerate(measurements):
            # Predict
            state = F @ state
            P = F @ P @ F.T + Q

            # Update
            S = H @ P @ H.T + R
            K = P @ H.T @ np.linalg.inv(S)
            state = state + K @ (np.array([z]) - H @ state)
            P = (np.eye(2) - K @ H) @ P
            result[i] = state[0]

        return result

    def _spline_smooth(self, points: list[TrackPoint]) -> list[TrackPoint]:
        if len(points) < 4:
            return points

        try:
            from scipy.interpolate import UnivariateSpline

            frames = np.array([p.frame for p in points], dtype=np.float64)
            xs = np.array([p.x for p in points], dtype=np.float64)
            ys = np.array([p.y for p in points], dtype=np.float64)

            s = self.smoothing_factor * len(frames)
            spline_x = UnivariateSpline(frames, xs, s=s, k=min(3, len(frames) - 1))
            spline_y = UnivariateSpline(frames, ys, s=s, k=min(3, len(frames) - 1))

            return [
                TrackPoint(
                    frame=p.frame,
                    x=float(spline_x(p.frame)),
                    y=float(spline_y(p.frame)),
                    confidence=p.confidence,
                    is_interpolated=p.is_interpolated,
                    is_manual=p.is_manual,
                )
                for p in points
            ]
        except Exception:
            return points

    def fill_gaps(
        self, points: list[TrackPoint], total_frames: int
    ) -> list[TrackPoint]:
        """Linearly interpolate missing frames between tracked points."""
        if not points:
            return points

        by_frame = {p.frame: p for p in points}
        all_frames = sorted(by_frame)
        filled = list(points)

        for i in range(len(all_frames) - 1):
            f0 = all_frames[i]
            f1 = all_frames[i + 1]
            if f1 - f0 <= 1:
                continue

            p0 = by_frame[f0]
            p1 = by_frame[f1]
            for f in range(f0 + 1, f1):
                alpha = (f - f0) / (f1 - f0)
                filled.append(
                    TrackPoint(
                        frame=f,
                        x=p0.x + alpha * (p1.x - p0.x),
                        y=p0.y + alpha * (p1.y - p0.y),
                        confidence=min(p0.confidence, p1.confidence) * 0.7,
                        is_interpolated=True,
                    )
                )

        return sorted(filled, key=lambda p: p.frame)
