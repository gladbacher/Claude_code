"""GolfTracerPipeline — top-level CV orchestrator.

Reads video in batches of 30 frames (memory-safe even for 4K), runs:
  detect → impact detect → track → smooth → return PipelineResult
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Literal, Optional

import numpy as np

from .detector import GolfBallDetector, Detection
from .impact_detector import ImpactDetector, ImpactResult
from .tracker import BallTracker, TrackState, TrackStatus
from .smoother import TrajectorySmoother, TrackPoint
from .optical_flow import OpticalFlowRefiner


@dataclass
class PipelineConfig:
    sport: Literal["golf", "cricket", "baseball", "tennis", "football"] = "golf"
    weights_path: Optional[Path] = None
    device: str = "cpu"
    confidence: float = 0.4
    impact_confidence: float = 0.2
    batch_size: int = 30
    max_track_frames: int = 600   # 5 seconds @ 120fps
    smoothing_factor: float = 0.5
    min_stationary_frames: int = 3
    displacement_threshold_px: float = 20.0


@dataclass
class PipelineResult:
    tracking_points: list[TrackPoint]
    impact_frame: int
    fps: float
    frame_count: int
    width: int
    height: int
    processing_time_s: float
    coverage: float  # fraction of post-impact frames with tracking data

    @property
    def impact_time_s(self) -> float:
        return self.impact_frame / max(self.fps, 1.0)


ProgressCallback = Callable[[float, str], None]


class GolfTracerPipeline:
    def __init__(self, config: Optional[PipelineConfig] = None) -> None:
        self.config = config or PipelineConfig()
        self._detector = GolfBallDetector(
            weights_path=self.config.weights_path,
            device=self.config.device,
            confidence=self.config.confidence,
            impact_confidence=self.config.impact_confidence,
        )
        self._impact_detector = ImpactDetector(
            min_stationary_frames=self.config.min_stationary_frames,
            displacement_threshold_px=self.config.displacement_threshold_px,
        )
        self._tracker = BallTracker()
        self._smoother = TrajectorySmoother(
            smoothing_factor=self.config.smoothing_factor
        )
        self._flow = OpticalFlowRefiner()

    def process(
        self,
        video_path: Path,
        on_progress: Optional[ProgressCallback] = None,
    ) -> PipelineResult:
        import cv2

        t0 = time.monotonic()
        video_path = Path(video_path)

        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

        _progress(on_progress, 0.02, "Extracting frames")

        # Phase 1: read all frames in batches and detect
        all_detections: list[list[Detection]] = []
        all_frames: list[np.ndarray] = []

        cap = cv2.VideoCapture(str(video_path))
        batch: list[np.ndarray] = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            batch.append(frame)
            frame_idx += 1

            if len(batch) >= self.config.batch_size:
                dets = self._detector.detect_batch(batch)
                all_detections.extend(dets)
                all_frames.extend(batch)
                batch = []
                progress = 0.02 + 0.3 * (frame_idx / max(total_frames, 1))
                _progress(on_progress, progress, f"Detecting frame {frame_idx}/{total_frames}")

        if batch:
            dets = self._detector.detect_batch(batch)
            all_detections.extend(dets)
            all_frames.extend(batch)

        cap.release()
        actual_frame_count = len(all_frames)

        _progress(on_progress, 0.35, "Detecting impact")

        # Phase 2: find impact frame
        # Use photometric only on first 300 frames to avoid memory pressure
        sample_frames = all_frames[:300] if len(all_frames) > 300 else all_frames
        impact_result = self._impact_detector.find_impact_frame(
            all_detections[:len(sample_frames)],
            sample_frames,
        )

        impact_frame = impact_result.frame_index
        if impact_frame < 0:
            # Fall back: first frame where we get a detection
            for fi, dets in enumerate(all_detections):
                if dets:
                    impact_frame = fi
                    break

        impact_frame = max(0, impact_frame)
        _progress(on_progress, 0.40, f"Impact at frame {impact_frame}")

        # Phase 3: track from impact onward
        self._tracker.reset()
        track_points: list[TrackPoint] = []
        track_end = min(actual_frame_count, impact_frame + self.config.max_track_frames)

        for fi in range(impact_frame, track_end):
            # Lower confidence near impact to catch motion-blurred ball
            near_impact = abs(fi - impact_frame) <= 5
            conf_override = self.config.impact_confidence if near_impact else None

            frame_dets = all_detections[fi]
            if conf_override is not None:
                # Re-detect with lower threshold near impact
                frame_dets = self._detector.detect_frame(
                    all_frames[fi], conf_override
                )

            state = self._tracker.update(frame_dets, all_frames[fi], fi)

            if state.center_xy[0] >= 0:
                h_norm = height if height > 0 else 1
                w_norm = width if width > 0 else 1
                track_points.append(
                    TrackPoint(
                        frame=fi,
                        x=state.center_xy[0] / w_norm,
                        y=state.center_xy[1] / h_norm,
                        confidence=state.confidence,
                        is_interpolated=state.is_interpolated,
                    )
                )

            progress = 0.40 + 0.40 * ((fi - impact_frame) / max(track_end - impact_frame, 1))
            if fi % 30 == 0:
                _progress(on_progress, progress, f"Tracking frame {fi}")

        _progress(on_progress, 0.82, "Smoothing trajectory")

        # Phase 4: fill gaps then smooth
        filled = self._smoother.fill_gaps(track_points, actual_frame_count)
        smoothed = self._smoother.smooth(filled)

        total_post_impact = track_end - impact_frame
        coverage = len(smoothed) / max(total_post_impact, 1)

        elapsed = time.monotonic() - t0
        _progress(on_progress, 1.0, f"Done in {elapsed:.1f}s — {len(smoothed)} tracking points")

        return PipelineResult(
            tracking_points=smoothed,
            impact_frame=impact_frame,
            fps=fps,
            frame_count=actual_frame_count,
            width=width,
            height=height,
            processing_time_s=elapsed,
            coverage=coverage,
        )


def _progress(cb: Optional[ProgressCallback], value: float, message: str) -> None:
    if cb:
        cb(value, message)
