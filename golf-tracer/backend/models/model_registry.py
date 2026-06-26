"""Singleton model registry — loads and caches YOLO model instances.

Supports sport-specific weight files and automatic GPU/CPU selection.
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Literal, Optional

Sport = Literal["golf", "cricket", "baseball", "tennis", "football"]

_WEIGHT_FILES: dict[str, str] = {
    "golf_n": "yolo11n-golf.pt",
    "golf_m": "yolo11m-golf.pt",
    "golf_l": "yolo11l-golf.pt",
    "cricket_n": "yolo11n-cricket.pt",
    "baseball_n": "yolo11n-baseball.pt",
    "tennis_n": "yolo11n-tennis.pt",
    "football_n": "yolo11n-football.pt",
    # Generic COCO fallback — sports balls are class 32
    "generic_n": "yolo11n.pt",
}


class ModelRegistry:
    _instance: Optional["ModelRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "ModelRegistry":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._cache: dict[str, object] = {}
                cls._instance._weights_dir: Optional[Path] = None
                cls._instance._device: str = "cpu"
        return cls._instance

    def configure(self, weights_dir: Path, device: str = "cpu") -> None:
        self._weights_dir = Path(weights_dir)
        self._device = device

    def get_detector(
        self,
        sport: Sport = "golf",
        model_size: Literal["n", "m", "l", "x"] = "n",
    ):
        from ..pipeline.detector import GolfBallDetector

        cache_key = f"{sport}_{model_size}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        weights_path = self._resolve_weights(sport, model_size)
        detector = GolfBallDetector(
            weights_path=weights_path,
            device=self._device,
        )
        self._cache[cache_key] = detector
        return detector

    def _resolve_weights(self, sport: Sport, size: str) -> Optional[Path]:
        if self._weights_dir is None:
            return None

        # Sport-specific first, then generic fallback
        for key in [f"{sport}_{size}", f"generic_{size}"]:
            filename = _WEIGHT_FILES.get(key)
            if filename:
                path = self._weights_dir / filename
                if path.exists():
                    return path

        return None

    def clear_cache(self) -> None:
        self._cache.clear()


registry = ModelRegistry()
