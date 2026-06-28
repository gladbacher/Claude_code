# Model Training Guide

## Fine-tuning YOLOv11 for Golf Ball Detection

### Why fine-tune?

The COCO-pretrained YOLOv11 can detect "sports balls" (class 32) but performs
poorly on small golf balls in flight (< 20px) and balls against complex
backgrounds (sky, trees, indoor simulators).

### Dataset

Recommended sources:
- **Roboflow Universe**: search "golf ball" — several datasets available
- **Golf Vision**: public datasets with flight video annotations
- **Custom capture**: record 100+ swings, annotate with CVAT or Label Studio

Target: 2,000+ annotated frames covering:
- Ball on tee (stationary)
- Ball at impact (motion blur acceptable)
- Ball in flight at various sizes (5–50px)
- Various backgrounds: fairway, sky, trees, indoor

### Training script

```python
from ultralytics import YOLO

model = YOLO("yolo11n.pt")  # start from pretrained

results = model.train(
    data="golf_ball_dataset.yaml",
    epochs=100,
    imgsz=1280,          # high res for small ball detection
    batch=8,
    name="golf_ball_n",
    device="cuda",
    patience=20,
    augment=True,        # includes mosaic, mixup, color jitter
    hsv_h=0.02,
    hsv_s=0.5,
    hsv_v=0.4,
    fliplr=0.5,
    scale=0.9,
)

# Export to ONNX for faster inference
model.export(format="onnx", imgsz=1280)
```

### Dataset YAML

```yaml
path: ./golf_ball_dataset
train: images/train
val: images/val
test: images/test

names:
  0: golf_ball
```

### After training

Place weights at:
```
backend/models/weights/yolo11n-golf.pt
```

The `ModelRegistry` will automatically prefer the sport-specific weights over
the generic COCO fallback.

### Evaluation targets

| Metric | Target |
|--------|--------|
| mAP@0.5 | ≥ 0.85 |
| Recall (in-flight frames) | ≥ 0.80 |
| Recall (stationary) | ≥ 0.95 |
| Inference time (1080p, GPU) | < 15ms |
