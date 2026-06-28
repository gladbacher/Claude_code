"""VideoWriter — pipes frames through FFmpeg to produce H.264 output.

Uses subprocess + stdin pipe to avoid keeping all frames in memory.
Supports CRF quality control, original frame rate preservation, and
audio passthrough from the original video.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Generator, Iterator, Optional

import numpy as np


class VideoWriter:
    def __init__(
        self,
        output_path: Path,
        width: int,
        height: int,
        fps: float,
        crf: int = 18,
        preset: str = "fast",
        audio_source: Optional[Path] = None,
    ) -> None:
        self.output_path = Path(output_path)
        self.width = width
        self.height = height
        self.fps = fps
        self.crf = crf
        self.preset = preset
        self.audio_source = audio_source
        self._proc: Optional[subprocess.Popen] = None

    def __enter__(self) -> "VideoWriter":
        self._start()
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def _start(self) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{self.width}x{self.height}",
            "-pix_fmt", "bgr24",
            "-r", str(self.fps),
            "-i", "pipe:0",
        ]

        if self.audio_source:
            cmd += ["-i", str(self.audio_source), "-map", "0:v", "-map", "1:a",
                    "-c:a", "aac", "-b:a", "128k", "-shortest"]
        else:
            cmd += ["-an"]

        cmd += [
            "-vcodec", "libx264",
            "-crf", str(self.crf),
            "-preset", self.preset,
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(self.output_path),
        ]

        self._proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

    def write_frame(self, frame: np.ndarray) -> None:
        if self._proc is None or self._proc.stdin is None:
            raise RuntimeError("VideoWriter not started — use as context manager")
        self._proc.stdin.write(frame.tobytes())

    def write_frames(self, frames: Iterator[np.ndarray]) -> None:
        for frame in frames:
            self.write_frame(frame)

    def close(self) -> None:
        if self._proc is None:
            return
        if self._proc.stdin:
            self._proc.stdin.close()
        _, stderr = self._proc.communicate()
        if self._proc.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {stderr.decode(errors='replace')}")
        self._proc = None


def render_video(
    input_video: Path,
    output_video: Path,
    composer: "FrameComposer",  # type: ignore[name-defined]
    tracking_points: list,
    fps: float,
    width: int,
    height: int,
    on_progress: Optional[callable] = None,
) -> None:
    """High-level helper: read input, composite, write output."""
    import cv2
    from .frame_composer import FrameComposer

    cap = cv2.VideoCapture(str(input_video))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    with VideoWriter(output_video, width, height, fps, audio_source=input_video) as writer:
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            composited = composer.compose_frame(
                frame, tracking_points, frame_idx, width, height
            )
            writer.write_frame(composited)
            frame_idx += 1
            if on_progress and frame_idx % 30 == 0:
                on_progress(frame_idx / max(total, 1), f"Rendering frame {frame_idx}/{total}")

    cap.release()
