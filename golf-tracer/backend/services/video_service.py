"""Video metadata extraction via FFprobe and frame utilities."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Optional

import numpy as np


class VideoMetadataExtractor:
    def extract(self, video_path: Path) -> dict:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-show_format",
            str(video_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFprobe failed: {result.stderr}")

        data = json.loads(result.stdout)
        video_stream = next(
            (s for s in data.get("streams", []) if s.get("codec_type") == "video"),
            None,
        )

        if video_stream is None:
            raise ValueError("No video stream found")

        fps = _parse_fps(video_stream.get("r_frame_rate", "30/1"))
        duration = float(data.get("format", {}).get("duration", 0))
        width = int(video_stream.get("width", 0))
        height = int(video_stream.get("height", 0))
        frame_count = int(video_stream.get("nb_frames", 0))
        if frame_count == 0 and duration > 0 and fps > 0:
            frame_count = int(duration * fps)

        fmt = data.get("format", {})
        file_size = int(fmt.get("size", 0))

        return {
            "fps": fps,
            "duration_s": duration,
            "width": width,
            "height": height,
            "frame_count": frame_count,
            "file_size_bytes": file_size,
        }

    def extract_frame(self, video_path: Path, frame_index: int) -> np.ndarray:
        import cv2
        cap = cv2.VideoCapture(str(video_path))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise ValueError(f"Could not extract frame {frame_index}")
        return frame

    def extract_frame_jpeg(
        self, video_path: Path, frame_index: int, quality: int = 85
    ) -> bytes:
        import cv2
        frame = self.extract_frame(video_path, frame_index)
        _, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        return encoded.tobytes()


def _parse_fps(fps_str: str) -> float:
    try:
        if "/" in fps_str:
            num, den = fps_str.split("/")
            return float(num) / float(den) if float(den) != 0 else 30.0
        return float(fps_str)
    except Exception:
        return 30.0


video_metadata_extractor = VideoMetadataExtractor()
