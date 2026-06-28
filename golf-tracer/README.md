# Golf Tracer

A production-quality golf ball tracer app similar to SmoothSwing — automatic ball detection, impact detection, flight tracking, and smooth tracer overlay export.

## Features

- **Automatic ball detection** via YOLOv11 (fine-tunable per sport)
- **Impact frame detection** (kinematic + photometric signal fusion)
- **Ball tracking** through motion blur, occlusion, and camera shake
- **Smooth tracer rendering** with glow, fade, and gradient effects
- **Manual corrections** — tap frames to override tracking positions
- **1080p export** with original frame rate preserved
- **Extensible** — add cricket, baseball, tennis, football with one config change

## Architecture

```
mobile/      React Native (Expo) — Android primary
backend/     Python FastAPI + OpenCV + YOLOv11
```

See [docs/architecture.md](docs/architecture.md) for the full system design.

## Quick Start

### Backend (Python 3.12+)

```bash
pip install -r backend/requirements.txt

# Download YOLOv11 nano weights (~6MB, COCO pretrained)
python -m backend.models.download_weights

# Start API server
uvicorn backend.main:app --reload
# API docs: http://localhost:8000/docs
```

### Mobile (Node 18+)

```bash
cd mobile
npm install
npx expo start
# Press 'a' to open Android emulator
```

### Docker (full stack)

```bash
docker-compose up --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/videos` | Upload a swing video |
| POST | `/jobs` | Start CV processing |
| GET | `/jobs/{id}/status` | Poll job progress |
| GET | `/jobs/{id}/result` | Get tracking points |
| GET | `/jobs/{id}/frames/{n}` | Get frame as JPEG |
| PATCH | `/jobs/{id}/corrections` | Apply manual corrections |
| POST | `/jobs/{id}/export` | Render tracer onto video |
| GET | `/exports/{id}/download` | Download exported video |

## CV Pipeline

```
Video → Detect (YOLO) → Impact Detection → Track (ByteTrack) → Smooth (Kalman + Spline) → Render (OpenCV + FFmpeg)
```

See [docs/cv-pipeline.md](docs/cv-pipeline.md) for algorithm details.

## Performance

| Input | GPU Target | CPU Target |
|-------|-----------|-----------|
| 10s 1080p 30fps | ~8s | ~45s |
| 10s 1080p 120fps | ~20s | ~120s |

GPU acceleration via PyTorch CUDA (auto-detected).

## Extending to Other Sports

Change `sport: "cricket" | "baseball" | "tennis" | "football"` in the job creation payload. See [docs/extensibility.md](docs/extensibility.md).

## Model Training

For best accuracy, fine-tune YOLOv11 on a golf-ball dataset. Roboflow has
pre-annotated golf, cricket, baseball, and tennis ball datasets. See [docs/model-training.md](docs/model-training.md).

## License

MIT
