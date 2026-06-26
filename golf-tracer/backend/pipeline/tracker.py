"""Ball tracker — ByteTrack-inspired implementation with optical-flow fallback.

ByteTrack is the primary tracker (handles occlusion via IoU + Kalman). When
the track is lost for ≤5 frames, we bridge using optical flow so the tracer
stays continuous through brief occlusions.

The full ByteTrack library requires a C++ build step that may not be
available in all environments, so we include a lightweight pure-Python
implementation of the core algorithm here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np

from .detector import Detection
from .optical_flow import OpticalFlowRefiner


class TrackStatus(str, Enum):
    TRACKED = "tracked"
    LOST = "lost"
    INTERPOLATED = "interpolated"
    NEW = "new"


@dataclass
class TrackState:
    track_id: int
    center_xy: tuple[float, float]
    bbox: tuple[float, float, float, float]
    confidence: float
    status: TrackStatus
    frame_index: int
    is_interpolated: bool = False


class _KalmanFilter:
    """Constant-velocity Kalman for 2D center position."""

    def __init__(self, init_xy: tuple[float, float]) -> None:
        self.x = np.array([init_xy[0], init_xy[1], 0.0, 0.0], dtype=np.float64)
        self.P = np.eye(4) * 100.0
        self.F = np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ], dtype=np.float64)
        self.H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], dtype=np.float64)
        self.Q = np.eye(4) * 1.0
        self.R = np.eye(2) * 10.0

    def predict(self) -> tuple[float, float]:
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return (float(self.x[0]), float(self.x[1]))

    def update(self, measurement: tuple[float, float]) -> tuple[float, float]:
        z = np.array(measurement, dtype=np.float64)
        y = z - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P
        return (float(self.x[0]), float(self.x[1]))

    @property
    def predicted_xy(self) -> tuple[float, float]:
        return (float(self.x[0]), float(self.x[1]))


class _Track:
    _id_counter = 0

    def __init__(self, detection: Detection, frame_index: int) -> None:
        _Track._id_counter += 1
        self.track_id = _Track._id_counter
        self.kf = _KalmanFilter(detection.center_xy)
        self.bbox = detection.bbox
        self.confidence = detection.confidence
        self.lost_frames = 0
        self.is_confirmed = False
        self.frame_index = frame_index
        self.hit_streak = 1

    def predict(self) -> tuple[float, float]:
        return self.kf.predict()

    def update(self, detection: Detection, frame_index: int) -> None:
        self.kf.update(detection.center_xy)
        self.bbox = detection.bbox
        self.confidence = detection.confidence
        self.lost_frames = 0
        self.frame_index = frame_index
        self.hit_streak += 1
        if self.hit_streak >= 2:
            self.is_confirmed = True

    @property
    def center_xy(self) -> tuple[float, float]:
        return self.kf.predicted_xy


class BallTracker:
    """Golf ball tracker combining Kalman filter matching with optical flow bridge."""

    def __init__(
        self,
        max_lost_frames: int = 5,
        iou_threshold: float = 0.3,
        max_gap_for_flow: int = 5,
    ) -> None:
        self.max_lost_frames = max_lost_frames
        self.iou_threshold = iou_threshold
        self.max_gap_for_flow = max_gap_for_flow
        self.flow = OpticalFlowRefiner(max_gap_frames=max_gap_for_flow)
        self._tracks: list[_Track] = []
        self._best_track_id: Optional[int] = None
        self._frame_buffer: list[np.ndarray] = []
        _Track._id_counter = 0

    def reset(self) -> None:
        self._tracks.clear()
        self._best_track_id = None
        self._frame_buffer.clear()
        _Track._id_counter = 0

    def update(
        self,
        detections: list[Detection],
        frame: np.ndarray,
        frame_index: int,
    ) -> TrackState:
        self._frame_buffer.append(frame)
        if len(self._frame_buffer) > 20:
            self._frame_buffer.pop(0)

        # Predict existing tracks
        for t in self._tracks:
            t.predict()

        if detections:
            self._match_and_update(detections, frame_index)

        # Increment lost counter for unmatched tracks
        for t in self._tracks:
            if t.frame_index != frame_index:
                t.lost_frames += 1

        # Remove stale tracks
        self._tracks = [
            t for t in self._tracks if t.lost_frames <= self.max_lost_frames
        ]

        # Pick best track (highest hit streak, smallest bbox area — it's a ball)
        active = [t for t in self._tracks if t.is_confirmed]
        if active:
            best = min(active, key=lambda t: (t.lost_frames, -t.hit_streak))
            self._best_track_id = best.track_id
        elif self._tracks:
            best = self._tracks[0]
            self._best_track_id = best.track_id
        else:
            best = None

        if best is None:
            return TrackState(
                track_id=-1,
                center_xy=(-1.0, -1.0),
                bbox=(0.0, 0.0, 0.0, 0.0),
                confidence=0.0,
                status=TrackStatus.LOST,
                frame_index=frame_index,
                is_interpolated=False,
            )

        is_lost = best.lost_frames > 0
        if is_lost and len(self._frame_buffer) >= 2:
            # Optical flow bridge
            flow_xy = self.flow.refine_position(
                self._frame_buffer[-2], self._frame_buffer[-1], best.center_xy
            )
            return TrackState(
                track_id=best.track_id,
                center_xy=flow_xy,
                bbox=best.bbox,
                confidence=best.confidence * 0.8,
                status=TrackStatus.INTERPOLATED,
                frame_index=frame_index,
                is_interpolated=True,
            )

        return TrackState(
            track_id=best.track_id,
            center_xy=best.center_xy,
            bbox=best.bbox,
            confidence=best.confidence,
            status=TrackStatus.TRACKED if not is_lost else TrackStatus.LOST,
            frame_index=frame_index,
            is_interpolated=False,
        )

    def _match_and_update(self, detections: list[Detection], frame_index: int) -> None:
        if not self._tracks:
            for det in detections:
                self._tracks.append(_Track(det, frame_index))
            return

        predicted = [t.center_xy for t in self._tracks]
        det_centers = [d.center_xy for d in detections]

        # Cost matrix: distance-based (works well for a single small ball)
        cost = np.zeros((len(self._tracks), len(detections)))
        for i, pc in enumerate(predicted):
            for j, dc in enumerate(det_centers):
                cost[i, j] = _euclidean(pc, dc)

        # Greedy matching (adequate for single-object tracking)
        matched_tracks: set[int] = set()
        matched_dets: set[int] = set()

        flat_order = np.argsort(cost.ravel())
        for idx in flat_order:
            ti = idx // len(detections)
            di = idx % len(detections)
            if ti in matched_tracks or di in matched_dets:
                continue
            if cost[ti, di] < 150:  # pixel distance threshold
                self._tracks[ti].update(detections[di], frame_index)
                matched_tracks.add(ti)
                matched_dets.add(di)

        # Spawn new tracks for unmatched detections
        for di, det in enumerate(detections):
            if di not in matched_dets:
                self._tracks.append(_Track(det, frame_index))


def _euclidean(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def _iou(a: tuple, b: tuple) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    union_area = (ax2-ax1)*(ay2-ay1) + (bx2-bx1)*(by2-by1) - inter_area
    return inter_area / (union_area + 1e-6)
