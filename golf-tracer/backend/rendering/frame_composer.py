"""FrameComposer — composites the tracer RGBA overlay onto each BGR video frame."""
from __future__ import annotations

from typing import Iterator

import numpy as np

from .tracer_renderer import TracerRenderer, TracerConfig
from ..pipeline.smoother import TrackPoint


class FrameComposer:
    def __init__(self, tracer_config: TracerConfig) -> None:
        self.renderer = TracerRenderer(tracer_config)
        self.config = tracer_config

    def compose_frame(
        self,
        frame: np.ndarray,
        tracking_points: list[TrackPoint],
        current_frame_idx: int,
        video_width: int,
        video_height: int,
    ) -> np.ndarray:
        """Composite tracer onto a single video frame.

        Args:
            frame: BGR frame (H, W, 3).
            tracking_points: All tracking points for the clip.
            current_frame_idx: Which frame we're compositing.
            video_width, video_height: Original video dimensions.

        Returns:
            BGR frame (H, W, 3) with tracer overlaid.
        """
        import cv2

        # Collect trailing points up to current frame
        trail_start = current_frame_idx - self.config.trail_length
        visible = [
            p for p in tracking_points
            if trail_start <= p.frame <= current_frame_idx
        ]

        if not visible:
            return frame

        # Convert normalized coords → pixel coords
        pixel_points = [
            (p.x * video_width, p.y * video_height)
            for p in visible
        ]

        canvas = self.renderer.render_tracer(pixel_points, (video_width, video_height))

        # Composite: blend RGBA canvas over BGR frame
        return _composite_rgba_over_bgr(frame, canvas)

    def compose_sequence(
        self,
        frames: list[np.ndarray],
        tracking_points: list[TrackPoint],
        start_frame: int,
        video_width: int,
        video_height: int,
    ) -> Iterator[np.ndarray]:
        """Yield composited frames for a sequence."""
        for i, frame in enumerate(frames):
            fi = start_frame + i
            yield self.compose_frame(
                frame, tracking_points, fi, video_width, video_height
            )


def _composite_rgba_over_bgr(bgr: np.ndarray, rgba: np.ndarray) -> np.ndarray:
    """Alpha-composite an RGBA overlay over a BGR frame."""
    import cv2

    alpha = rgba[:, :, 3:4].astype(np.float32) / 255.0
    overlay_bgr = rgba[:, :, :3][:, :, ::-1].astype(np.float32)  # RGB→BGR

    base = bgr.astype(np.float32)
    result = base * (1 - alpha) + overlay_bgr * alpha
    return np.clip(result, 0, 255).astype(np.uint8)
