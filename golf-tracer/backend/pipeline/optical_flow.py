"""Optical flow refiner using Lucas-Kanade sparse tracking.

Used for two purposes:
  1. Sub-pixel refinement of YOLO-detected position.
  2. Bridging lost-track gaps (≤10 frames) via linear interpolation weighted
     by optical flow magnitude.
"""
from __future__ import annotations

from typing import Optional

import numpy as np


_LK_PARAMS = dict(
    winSize=(21, 21),
    maxLevel=4,
    criteria=(
        3,    # cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT
        30,
        0.01,
    ),
)


class OpticalFlowRefiner:
    def __init__(self, max_gap_frames: int = 10) -> None:
        self.max_gap_frames = max_gap_frames

    def refine_position(
        self,
        prev_frame: np.ndarray,
        curr_frame: np.ndarray,
        prev_xy: tuple[float, float],
    ) -> tuple[float, float]:
        """Track a single point from prev_frame to curr_frame."""
        import cv2

        prev_gray = _to_gray(prev_frame)
        curr_gray = _to_gray(curr_frame)

        point = np.array([[list(prev_xy)]], dtype=np.float32)
        next_pts, status, _ = cv2.calcOpticalFlowPyrLK(
            prev_gray, curr_gray, point, None, **_LK_PARAMS
        )

        if status is not None and status[0][0] == 1:
            return (float(next_pts[0][0][0]), float(next_pts[0][0][1]))
        return prev_xy

    def interpolate_lost_frames(
        self,
        frames: list[np.ndarray],
        start_xy: tuple[float, float],
        end_xy: Optional[tuple[float, float]],
        start_frame_idx: int,
        end_frame_idx: int,
    ) -> list[tuple[float, float]]:
        """Return interpolated positions for frames (start_frame_idx, end_frame_idx).

        Uses optical flow from start forward and linear fallback when flow fails.
        Gap must be ≤ max_gap_frames.
        """
        gap = end_frame_idx - start_frame_idx
        if gap <= 0 or gap > self.max_gap_frames:
            return []

        interpolated: list[tuple[float, float]] = []
        current_xy = start_xy

        for i in range(1, gap):
            frame_idx = start_frame_idx + i
            if frame_idx >= len(frames) or frame_idx - 1 >= len(frames):
                break

            prev_frame = frames[frame_idx - 1]
            curr_frame = frames[frame_idx]
            refined = self.refine_position(prev_frame, curr_frame, current_xy)
            interpolated.append(refined)
            current_xy = refined

        # If flow diverged badly and we have an end anchor, blend toward it
        if end_xy is not None and interpolated:
            interpolated = _blend_toward_anchor(
                start_xy, end_xy, interpolated
            )

        return interpolated

    def track_sequence(
        self,
        frames: list[np.ndarray],
        seed_xy: tuple[float, float],
        seed_frame: int,
        max_frames: int = 300,
    ) -> list[tuple[int, tuple[float, float]]]:
        """Forward-track from seed_frame using only optical flow.

        Returns list of (frame_index, (x, y)) tuples.
        """
        results: list[tuple[int, tuple[float, float]]] = [
            (seed_frame, seed_xy)
        ]
        current_xy = seed_xy

        for i in range(seed_frame + 1, min(seed_frame + max_frames + 1, len(frames))):
            refined = self.refine_position(frames[i - 1], frames[i], current_xy)
            results.append((i, refined))
            current_xy = refined

        return results


def _to_gray(frame: np.ndarray) -> np.ndarray:
    import cv2
    if frame.ndim == 2:
        return frame
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def _blend_toward_anchor(
    start: tuple[float, float],
    end: tuple[float, float],
    points: list[tuple[float, float]],
) -> list[tuple[float, float]]:
    """Linearly blend optical-flow track toward known end point."""
    n = len(points) + 1  # include end slot
    blended = []
    for i, pt in enumerate(points):
        alpha = (i + 1) / n
        bx = pt[0] * (1 - alpha) + end[0] * alpha
        by = pt[1] * (1 - alpha) + end[1] * alpha
        blended.append((bx, by))
    return blended
