"""Golf ball detector backed by YOLOv11 (ultralytics).

Two-stage strategy:
  1. Full-frame inference at low confidence to catch blurred / small balls.
  2. ROI crop around predicted location at higher confidence for sub-pixel accuracy.

The detector runs at full input resolution — downscaling loses the 5-10px
ball signal that is critical post-impact.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, Sequence

import numpy as np


@dataclass
class Detection:
    bbox: tuple[float, float, float, float]  # x1, y1, x2, y2 (absolute pixels)
    confidence: float
    class_id: int = 0

    @property
    def center_xy(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    @property
    def area(self) -> float:
        x1, y1, x2, y2 = self.bbox
        return max(0.0, x2 - x1) * max(0.0, y2 - y1)


class BaseDetector(ABC):
    @abstractmethod
    def detect_frame(
        self,
        frame: np.ndarray,
        confidence_override: Optional[float] = None,
    ) -> list[Detection]:
        ...

    def detect_batch(
        self,
        frames: list[np.ndarray],
        confidence_override: Optional[float] = None,
    ) -> list[list[Detection]]:
        return [self.detect_frame(f, confidence_override) for f in frames]


class GolfBallDetector(BaseDetector):
    """YOLOv11-based golf ball detector.

    Falls back to a heuristic Hough-circle detector when YOLO weights are
    unavailable (useful for CPU-only CI environments without model download).
    """

    def __init__(
        self,
        weights_path: Optional[Path] = None,
        device: str = "cpu",
        confidence: float = 0.4,
        impact_confidence: float = 0.2,
        roi_expand_ratio: float = 2.0,
    ) -> None:
        self.confidence = confidence
        self.impact_confidence = impact_confidence
        self.roi_expand_ratio = roi_expand_ratio
        self.device = device
        self._model = None

        if weights_path and Path(weights_path).exists():
            self._load_yolo(weights_path)

    def _load_yolo(self, weights_path: Path) -> None:
        try:
            from ultralytics import YOLO
            self._model = YOLO(str(weights_path))
            self._model.to(self.device)
        except Exception as exc:
            print(f"[Detector] Failed to load YOLO weights: {exc}. Using fallback.")
            self._model = None

    def detect_frame(
        self,
        frame: np.ndarray,
        confidence_override: Optional[float] = None,
    ) -> list[Detection]:
        conf = confidence_override if confidence_override is not None else self.confidence

        if self._model is not None:
            return self._yolo_detect(frame, conf)
        return self._heuristic_detect(frame, conf)

    def detect_batch(
        self,
        frames: list[np.ndarray],
        confidence_override: Optional[float] = None,
    ) -> list[list[Detection]]:
        conf = confidence_override if confidence_override is not None else self.confidence

        if self._model is not None:
            return self._yolo_batch(frames, conf)
        return [self._heuristic_detect(f, conf) for f in frames]

    def detect_with_roi_refinement(
        self,
        frame: np.ndarray,
        prev_center: tuple[float, float],
        search_radius: int = 80,
        confidence_override: Optional[float] = None,
    ) -> list[Detection]:
        """Two-stage: broad detect → ROI refine around predicted location."""
        conf = confidence_override if confidence_override is not None else self.confidence

        # Stage 1: full-frame low-confidence sweep
        candidates = self.detect_frame(frame, conf * 0.6)

        # Stage 2: crop ROI and re-detect at higher confidence
        h, w = frame.shape[:2]
        cx, cy = prev_center
        x1 = max(0, int(cx - search_radius))
        y1 = max(0, int(cy - search_radius))
        x2 = min(w, int(cx + search_radius))
        y2 = min(h, int(cy + search_radius))

        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            return candidates

        roi_detections = self.detect_frame(roi, conf)
        # Translate ROI-relative coordinates back to full-frame
        for det in roi_detections:
            bx1, by1, bx2, by2 = det.bbox
            det.bbox = (bx1 + x1, by1 + y1, bx2 + x1, by2 + y1)

        # Merge and deduplicate, preferring ROI detections (more accurate)
        return roi_detections if roi_detections else candidates

    def _yolo_detect(self, frame: np.ndarray, conf: float) -> list[Detection]:
        results = self._model.predict(
            frame,
            conf=conf,
            imgsz=max(frame.shape[:2]),
            verbose=False,
            device=self.device,
        )
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                xyxy = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                cls = int(box.cls[0].cpu().numpy())
                detections.append(
                    Detection(
                        bbox=(float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])),
                        confidence=confidence,
                        class_id=cls,
                    )
                )
        return detections

    def _yolo_batch(self, frames: list[np.ndarray], conf: float) -> list[list[Detection]]:
        results = self._model.predict(
            frames,
            conf=conf,
            imgsz=max(max(f.shape[:2]) for f in frames),
            verbose=False,
            device=self.device,
        )
        batch_detections = []
        for result in results:
            frame_dets = []
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    xyxy = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    cls = int(box.cls[0].cpu().numpy())
                    frame_dets.append(
                        Detection(
                            bbox=(float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])),
                            confidence=confidence,
                            class_id=cls,
                        )
                    )
            batch_detections.append(frame_dets)
        return batch_detections

    def _heuristic_detect(self, frame: np.ndarray, conf: float) -> list[Detection]:
        """Hough-circle fallback when no YOLO model is loaded."""
        import cv2

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)

        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=20,
            param1=50,
            param2=30,
            minRadius=3,
            maxRadius=50,
        )

        detections = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype(int)
            for cx, cy, r in circles:
                detections.append(
                    Detection(
                        bbox=(cx - r, cy - r, cx + r, cy + r),
                        confidence=0.5,
                        class_id=0,
                    )
                )
        return detections
