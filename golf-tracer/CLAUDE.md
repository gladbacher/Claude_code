# Golf Tracer — CLAUDE.md

## Project Structure

```
backend/     Python/FastAPI backend + CV pipeline
mobile/      React Native (Expo) Android app
docs/        Architecture and algorithm docs
```

## Running the Backend

```bash
cd golf-tracer

# Install deps
pip install -r backend/requirements-dev.txt

# Download default YOLO weights (nano, CPU)
python -m backend.models.download_weights

# Start server
python -m backend.main
# → http://localhost:8000/docs
```

## Running Tests

```bash
# All backend tests
pytest backend/tests/ -v --cov=backend

# Specific test file
pytest backend/tests/test_pipeline.py -v

# Skip integration tests (needs FFmpeg)
pytest backend/tests/ -v -k "not test_pipeline"
```

## Running with Docker

```bash
docker-compose up --build
# Backend at http://localhost:8000
```

## Running the Mobile App

```bash
cd mobile
npm install
npx expo start
# Press 'a' for Android emulator
```

## Key Files

- `backend/pipeline/pipeline.py` — CV pipeline orchestrator
- `backend/pipeline/detector.py` — YOLO + Hough fallback
- `backend/rendering/tracer_renderer.py` — tracer drawing
- `backend/main.py` — FastAPI app factory
- `mobile/src/screens/ResultScreen.tsx` — video + tracer overlay
- `mobile/src/components/TracerOverlay.tsx` — SVG tracer

## Environment Variables

Copy `.env.example` to `.env` and configure. Key vars:

- `DATABASE_URL` — defaults to SQLite for dev
- `USE_GPU` — `auto | true | false`
- `YOLO_MODEL_SIZE` — `n | m | l` (nano is fastest)
- `STORAGE_BACKEND` — `local | s3`
