"""Impact frame detection.

Identifies the frame where the club strikes the ball using two complementary signals:
  1. Kinematic: longest run of "stationary" detections followed by first large displacement.
  2. Photometric: frame-difference energy spike (motion energy) at the moment of impact.

Returns the frame index of impact, or -1 if not found.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np

from .detector import Detection


@dataclass
class ImpactResult:
    frame_index: int        # -1 if not detected
    confidence: float       # 0.0–1.0
    stationary_end: int     # last frame where ball was stationary
    method: str             # "kinematic" | "photometric" | "combined"


class ImpactDetector:
    def __init__(
        self,
        min_stationary_frames: int = 3,
        stationary_threshold_px: float = 8.0,
        displacement_threshold_px: float = 20.0,
        energy_spike_factor: float = 3.0,
    ) -> None:
        self.min_stationary_frames = min_stationary_frames
        self.stationary_threshold_px = stationary_threshold_px
        self.displacement_threshold_px = displacement_threshold_px
        self.energy_spike_factor = energy_spike_factor

    def find_impact_frame(
        self,
        detections: list[list[Detection]],
        frames: Optional[list[np.ndarray]] = None,
    ) -> ImpactResult:
        kinematic = self._kinematic_impact(detections)
        if frames is not None and len(frames) > 1:
            photo = self._photometric_impact(frames)
        else:
            photo = ImpactResult(-1, 0.0, -1, "photometric")

        return self._combine(kinematic, photo)

    def _kinematic_impact(self, detections: list[list[Detection]]) -> ImpactResult:
        centers = []
        for frame_dets in detections:
            if frame_dets:
                best = max(frame_dets, key=lambda d: d.confidence)
                centers.append(best.center_xy)
            else:
                centers.append(None)

        # Find runs of stationary detections
        best_run_start = -1
        best_run_len = 0
        cur_start = -1
        cur_len = 0

        for i, c in enumerate(centers):
            if c is None:
                cur_start = -1
                cur_len = 0
                continue

            if cur_len == 0:
                cur_start = i
                cur_len = 1
            else:
                prev = centers[i - 1]
                if prev is not None:
                    dist = _euclidean(c, prev)
                    if dist <= self.stationary_threshold_px:
                        cur_len += 1
                    else:
                        if cur_len > best_run_len:
                            best_run_len = cur_len
                            best_run_start = cur_start
                        cur_start = i
                        cur_len = 1

        if cur_len > best_run_len:
            best_run_len = cur_len
            best_run_start = cur_start

        if best_run_len < self.min_stationary_frames or best_run_start < 0:
            return ImpactResult(-1, 0.0, -1, "kinematic")

        stationary_end = best_run_start + best_run_len - 1

        # Search for first large displacement after stationary window
        for i in range(stationary_end + 1, len(centers)):
            if centers[i] is None:
                continue
            ref = centers[stationary_end]
            if ref is None:
                continue
            if _euclidean(centers[i], ref) >= self.displacement_threshold_px:
                conf = min(1.0, best_run_len / 10.0)
                return ImpactResult(i, conf, stationary_end, "kinematic")

        return ImpactResult(-1, 0.0, stationary_end, "kinematic")

    def _photometric_impact(self, frames: list[np.ndarray]) -> ImpactResult:
        import cv2

        energies = []
        for i in range(1, len(frames)):
            prev = cv2.cvtColor(frames[i - 1], cv2.COLOR_BGR2GRAY).astype(np.float32)
            curr = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY).astype(np.float32)
            diff = np.abs(curr - prev)
            energies.append(float(diff.mean()))

        if not energies:
            return ImpactResult(-1, 0.0, -1, "photometric")

        energies_arr = np.array(energies)
        mean_e = energies_arr.mean()
        std_e = energies_arr.std()
        threshold = mean_e + self.energy_spike_factor * std_e

        spike_frames = np.where(energies_arr > threshold)[0]
        if len(spike_frames) == 0:
            return ImpactResult(-1, 0.0, -1, "photometric")

        # First spike is most likely impact
        frame_idx = int(spike_frames[0]) + 1  # +1 because energy[i] = diff(i-1, i)
        conf = min(1.0, (energies_arr[spike_frames[0]] - mean_e) / (std_e + 1e-6) / 5.0)
        return ImpactResult(frame_idx, conf, -1, "photometric")

    def _combine(self, kinematic: ImpactResult, photo: ImpactResult) -> ImpactResult:
        if kinematic.frame_index < 0 and photo.frame_index < 0:
            return ImpactResult(-1, 0.0, -1, "combined")

        if kinematic.frame_index >= 0 and photo.frame_index >= 0:
            # Weighted combination: kinematic is generally more precise
            k_weight, p_weight = 0.7, 0.3
            if abs(kinematic.frame_index - photo.frame_index) <= 5:
                # They agree — high confidence, pick kinematic
                conf = kinematic.confidence * k_weight + photo.confidence * p_weight
                return ImpactResult(kinematic.frame_index, min(1.0, conf * 1.2), kinematic.stationary_end, "combined")
            # Disagree — use higher-confidence one
            if kinematic.confidence >= photo.confidence:
                return ImpactResult(kinematic.frame_index, kinematic.confidence, kinematic.stationary_end, "combined")
            return ImpactResult(photo.frame_index, photo.confidence, kinematic.stationary_end, "combined")

        if kinematic.frame_index >= 0:
            return kinematic
        return photo


def _euclidean(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
