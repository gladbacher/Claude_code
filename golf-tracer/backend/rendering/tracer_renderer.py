"""TracerRenderer — draws a smooth, glowing tracer line onto an RGBA canvas.

Features:
  - Gradient color along the trail (solid head → transparent tail)
  - Gaussian glow effect via cv2.GaussianBlur on a separate mask
  - Configurable trail length, fade curve, thickness, and opacity
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class TracerConfig:
    color: str = "#FF6B00"          # Hex color for the tracer head
    thickness: int = 4              # Base line thickness in pixels (at 1080p)
    opacity: float = 0.85           # Overall opacity 0.0–1.0
    glow_radius: int = 8            # Gaussian blur radius for glow (0 = no glow)
    trail_length: int = 30          # Number of historical frames to draw
    fade_tail: bool = True          # Whether to fade the tail to transparent
    fade_exponent: float = 2.0      # Power curve for tail fade (2.0 = quadratic)
    glow_opacity: float = 0.4       # Secondary glow layer opacity

    @property
    def color_bgr(self) -> tuple[int, int, int]:
        hex_str = self.color.lstrip("#")
        r, g, b = (int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        return (b, g, r)  # OpenCV uses BGR

    @property
    def color_rgb(self) -> tuple[int, int, int]:
        hex_str = self.color.lstrip("#")
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


class TracerRenderer:
    def __init__(self, config: Optional[TracerConfig] = None) -> None:
        self.config = config or TracerConfig()

    def render_tracer(
        self,
        points: list[tuple[float, float]],
        canvas_size: tuple[int, int],
    ) -> np.ndarray:
        """Draw tracer onto a transparent RGBA canvas.

        Args:
            points: List of (x, y) pixel coordinates in drawing order,
                    index 0 is oldest (tail), last is newest (head).
            canvas_size: (width, height) of the output canvas.

        Returns:
            RGBA numpy array (H, W, 4) with the tracer drawn.
        """
        import cv2

        W, H = canvas_size
        canvas = np.zeros((H, W, 4), dtype=np.uint8)

        if len(points) < 2:
            if len(points) == 1:
                cx, cy = int(points[0][0]), int(points[0][1])
                r = self.config.thickness + 2
                alpha = int(255 * self.config.opacity)
                b, g, rc = self.config.color_bgr
                cv2.circle(canvas, (cx, cy), r, (b, g, rc, alpha), -1)
            return canvas

        cfg = self.config
        n = len(points)

        # Glow layer: draw thick blurred version first
        if cfg.glow_radius > 0:
            glow_layer = np.zeros((H, W, 4), dtype=np.uint8)
            for i in range(1, n):
                alpha_frac = self._fade_alpha(i, n)
                alpha_val = int(255 * cfg.glow_opacity * alpha_frac)
                if alpha_val < 5:
                    continue
                pt1 = (int(points[i - 1][0]), int(points[i - 1][1]))
                pt2 = (int(points[i][0]), int(points[i][1]))
                b, g, rc = cfg.color_bgr
                cv2.line(glow_layer, pt1, pt2, (b, g, rc, alpha_val), cfg.thickness * 3)

            blur_size = cfg.glow_radius * 2 + 1
            glow_blurred = cv2.GaussianBlur(glow_layer, (blur_size, blur_size), cfg.glow_radius)
            canvas = _alpha_composite(canvas, glow_blurred)

        # Main tracer line
        for i in range(1, n):
            alpha_frac = self._fade_alpha(i, n)
            alpha_val = int(255 * cfg.opacity * alpha_frac)
            if alpha_val < 5:
                continue

            pt1 = (int(points[i - 1][0]), int(points[i - 1][1]))
            pt2 = (int(points[i][0]), int(points[i][1]))
            b, g, rc = cfg.color_bgr

            # Slightly thicker toward head
            thickness = max(1, int(cfg.thickness * (0.5 + 0.5 * (i / n))))
            seg = np.zeros((H, W, 4), dtype=np.uint8)
            cv2.line(seg, pt1, pt2, (b, g, rc, alpha_val), thickness, cv2.LINE_AA)
            canvas = _alpha_composite(canvas, seg)

        # Ball dot at the head
        head = points[-1]
        hx, hy = int(head[0]), int(head[1])
        head_r = cfg.thickness + 3
        head_alpha = int(255 * cfg.opacity)
        b, g, rc = cfg.color_bgr
        cv2.circle(canvas, (hx, hy), head_r, (b, g, rc, head_alpha), -1, cv2.LINE_AA)

        return canvas

    def _fade_alpha(self, segment_index: int, total_segments: int) -> float:
        """Return opacity multiplier for a segment (0.0 = tail, 1.0 = head)."""
        if not self.config.fade_tail:
            return 1.0
        t = segment_index / max(total_segments - 1, 1)
        return t ** (1.0 / self.config.fade_exponent)


def _alpha_composite(base: np.ndarray, overlay: np.ndarray) -> np.ndarray:
    """Alpha-composite overlay onto base (both RGBA uint8)."""
    base_f = base.astype(np.float32) / 255.0
    ov_f = overlay.astype(np.float32) / 255.0

    ov_a = ov_f[:, :, 3:4]
    base_a = base_f[:, :, 3:4]

    out_a = ov_a + base_a * (1 - ov_a)
    with np.errstate(invalid="ignore", divide="ignore"):
        out_rgb = np.where(
            out_a > 0,
            (ov_f[:, :, :3] * ov_a + base_f[:, :, :3] * base_a * (1 - ov_a)) / np.where(out_a > 0, out_a, 1),
            0,
        )

    result = np.clip(
        np.concatenate([out_rgb, out_a], axis=2) * 255, 0, 255
    ).astype(np.uint8)
    return result
