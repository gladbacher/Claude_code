# Adding New Sports

The detector, tracker, and renderer implement abstract base classes. Adding a
new sport requires three changes:

## 1. Add weights to model registry

In `backend/models/model_registry.py`:
```python
_WEIGHT_FILES = {
    ...
    "cricket_n": "yolo11n-cricket.pt",
    "cricket_m": "yolo11m-cricket.pt",
}
```

Train or fine-tune YOLO on a cricket ball dataset (Roboflow has pre-labelled
datasets for cricket, baseball, tennis, and football).

## 2. Tune ImpactDetector heuristics per sport

In `backend/pipeline/impact_detector.py`, pass sport-specific settings:
```python
# Cricket — slower ball, more stationary frames before release
cricket_detector = ImpactDetector(
    min_stationary_frames=5,
    displacement_threshold_px=15.0,
)

# Baseball — fast pitch, very short stationary window
baseball_detector = ImpactDetector(
    min_stationary_frames=2,
    displacement_threshold_px=30.0,
)
```

## 3. Register via PipelineConfig.sport

`GolfTracerPipeline` already reads `config.sport` and passes it to
`ModelRegistry.get_detector(sport, model_size)`. No other changes needed.

## Zero-change components

- `BallTracker` — sport-agnostic, works for any round object
- `TrajectorySmoother` — sport-agnostic
- `TracerRenderer` — sport-agnostic
- All API routes — sport-agnostic (sport is a field in JobCreate)
- All mobile screens — sport-agnostic
