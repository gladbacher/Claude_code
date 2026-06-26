# Computer Vision Pipeline

## Detection

**Primary**: YOLOv11 (ultralytics) trained/fine-tuned on golf ball dataset.  
**Fallback**: Hough circle transform (OpenCV) — used in CI and when no YOLO weights are present.

### Why full-resolution inference?

Golf balls are 42.67mm in diameter. At typical filming distance (10–20m), a 4K frame shows the ball at 30–100px; a 1080p frame shows it at 8–25px. Downscaling to 640×640 (standard YOLO input) would reduce a 20px ball to 7px — below the reliable detection threshold. We pass the full 1080p (or 4K) frame and rely on YOLOv11's stride-32 minimum object size.

### Two-stage detection

For each frame after impact detection:
1. Full-frame detect at confidence 0.4 → candidate list
2. If candidates exist, crop ROI (±80px around best candidate) and re-detect at 0.6 confidence

## Impact Detection

Two complementary signals, weighted combination:

| Signal | Method | Weight |
|--------|--------|--------|
| Kinematic | Longest stationary run → first large displacement | 0.7 |
| Photometric | Frame-difference energy spike | 0.3 |

If both signals agree (within 5 frames): boost confidence × 1.2

## Tracking

**ByteTrack** (lightweight pure-Python implementation):
- Constant-velocity Kalman filter per track
- IoU + Euclidean distance Hungarian matching
- Tracks confirmed after 2 consecutive hits

**Optical flow bridge**:
- When track is lost for ≤5 frames, Lucas-Kanade pyramid flow bridges the gap
- For gap >5 frames, track is considered lost (optical flow diverges at high speed)
- `is_interpolated=True` marks bridged points

## Smoothing

1. **Kalman 1D filter** on x and y independently (forward pass only)
2. **Cubic spline** (`scipy.interpolate.UnivariateSpline`) over Kalman output
3. **Manual points** (`is_manual=True`) are locked — smoothing skips them

## Performance Targets

| Input | Target | GPU | CPU |
|-------|--------|-----|-----|
| 1080p 30fps 10s | <20s | ~8s | ~45s |
| 1080p 120fps 10s | <45s | ~20s | ~120s |
| 4K 60fps 10s | <60s | ~30s | OOM risk |

For 4K: batch size 30 frames keeps peak memory under 8GB (30 × 4K BGR ≈ 750MB).
