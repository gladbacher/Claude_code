#!/usr/bin/env python3
"""Download YOLO model weights on first run.

Usage:
    python -m backend.models.download_weights [--size n|m|l]

For production golf ball detection, fine-tuned weights are needed.
This script downloads the best available fallback: COCO-pretrained YOLOv11
(sports ball = class 32) and the ultralytics default golf model if available.
"""
from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

WEIGHTS_DIR = Path(__file__).parent / "weights"

DOWNLOADS = {
    # Ultralytics releases — publicly available
    "yolo11n.pt": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt",
    "yolo11m.pt": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11m.pt",
}


def download(name: str, url: str, dest: Path) -> None:
    target = dest / name
    if target.exists():
        print(f"  {name} already exists, skipping.")
        return
    print(f"  Downloading {name} ...")
    urllib.request.urlretrieve(url, target)
    print(f"  Saved to {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download YOLO weights")
    parser.add_argument("--size", choices=["n", "m", "l"], default="n")
    parser.add_argument("--all", action="store_true", help="Download all sizes")
    args = parser.parse_args()

    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

    sizes = list(DOWNLOADS.keys()) if args.all else [f"yolo11{args.size}.pt"]
    for name in sizes:
        url = DOWNLOADS.get(name)
        if url:
            download(name, url, WEIGHTS_DIR)
        else:
            print(f"  No download URL for {name}")

    print("\nNote: For best golf ball detection accuracy, fine-tune on a golf")
    print("ball dataset (e.g. Roboflow golf-ball datasets) and place weights")
    print(f"as 'yolo11n-golf.pt' in {WEIGHTS_DIR}")


if __name__ == "__main__":
    main()
