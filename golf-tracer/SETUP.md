# Golf Tracer — Setup Guide

This document records the exact steps to run the Golf Tracer app locally on a Mac,
including all fixes discovered during initial setup. Use this as the authoritative
reference when picking up this project.

---

## Prerequisites

Install these before anything else:

```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python, Node, FFmpeg
brew install python@3.11 node ffmpeg
```

---

## 1. Clone & Branch

```bash
cd ~
git clone https://github.com/gladbacher/Claude_code.git
cd Claude_code
git fetch origin claude/golf-ball-tracer-app-ycpwaj
git checkout claude/golf-ball-tracer-app-ycpwaj
```

---

## 2. Backend Setup

```bash
cd ~/Claude_code/golf-tracer
pip3 install -r backend/requirements.txt
pip3 install aiosqlite        # required for SQLite async — not in requirements.txt yet
```

### Known dependency issues (already fixed in requirements.txt)

- `asyncpg` is commented out — it requires a C compiler and is only needed for PostgreSQL
  production. Local dev uses SQLite, so it can be skipped.
- `torch` and `numpy` use `>=` pins (not `==`) because the original pinned versions
  (torch==2.4.1, numpy==1.26.4) don't support Python 3.13.
- `filterpy` is not in requirements — the codebase has its own Kalman implementation.

### Download model weights

```bash
cd ~/Claude_code/golf-tracer
python3 -m backend.models.download_weights
# Downloads yolo11n.pt (~6MB) to backend/models/weights/
```

### Start the backend

```bash
cd ~/Claude_code/golf-tracer
python3 -m backend.main
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

---

## 3. Mobile App Setup

### Prerequisites

Install **Expo Go** on your phone:
- Android: Google Play Store → "Expo Go"
- iPhone: App Store → "Expo Go"

Make sure your phone and Mac are on the **same WiFi network**.

### Find your Mac's local IP

```bash
ipconfig getifaddr en0
# e.g. 192.168.1.42
```

### Update the API URL

Edit `mobile/src/constants/api.ts` and set the IP from above:

```ts
? 'http://192.168.X.X:8000'  // your Mac's local IP
```

### React version fix (CRITICAL)

The mobile app requires React and react-native-renderer to be on the **exact same version**.
After `npm install`, check which version of `react-native-renderer` was installed:

```bash
cat ~/Claude_code/golf-tracer/mobile/node_modules/react-native-renderer/package.json | grep '"version"'
```

Then pin React to that exact version:

```bash
cd ~/Claude_code/golf-tracer/mobile
npm install react@<version-from-above> --save-exact
```

For example, if react-native-renderer is 19.2.3:

```bash
npm install react@19.2.3 --save-exact
```

### Install and run

```bash
cd ~/Claude_code/golf-tracer/mobile
npm install
npx expo start
```

Scan the QR code shown in the terminal using the **Expo Go app** on your phone
(use the scan button inside Expo Go, not your phone's regular camera app).

### Known issues fixed

| Issue | Fix applied |
|---|---|
| `expo-asset` not found | Added to package.json dependencies |
| `expo-router/entry` as main | Removed; Expo auto-detects `App.tsx` |
| `App.tsx` missing at root | Created `mobile/App.tsx` re-exporting `src/App.tsx` |
| `babel-plugin-module-resolver` crash | Removed from babel.config.js |
| `cardStyle` deprecated | Changed to `contentStyle` in RootNavigator.tsx |
| Asset files missing | Created placeholder PNGs in `mobile/assets/` |
| Expo SDK version mismatch | package.json updated to `expo: "~56.0.0"` |

---

## 4. Running Both Together

Open two terminal tabs:

**Tab 1 — Backend:**
```bash
cd ~/Claude_code/golf-tracer
python3 -m backend.main
```

**Tab 2 — Mobile:**
```bash
cd ~/Claude_code/golf-tracer/mobile
npx expo start
```

---

## 5. Using the App

1. Open Expo Go on your phone and scan the QR code
2. Tap **Import Video** to pick a golf swing video from your camera roll
3. The video is uploaded to the backend and processed (YOLO detection → tracking → smoothing)
4. View the tracer overlay on the result screen
5. Optionally tap **Correct** to manually adjust ball positions
6. Tap **Export** to render and download the final video with tracer

---

## 6. Environment Variables

Copy `.env.example` to `.env` in the `golf-tracer/` directory:

```bash
cp ~/Claude_code/golf-tracer/.env.example ~/Claude_code/golf-tracer/.env
```

Key variables (defaults work for local dev):

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./golf_tracer.db` | SQLite for dev |
| `USE_GPU` | `auto` | Set `false` to force CPU |
| `YOLO_MODEL_SIZE` | `n` | `n`=fast, `m`=accurate |
| `STORAGE_BACKEND` | `local` | `local` or `s3` |

---

## 7. Running Tests

```bash
cd ~/Claude_code/golf-tracer
pip3 install pytest pytest-asyncio pytest-cov httpx
pytest backend/tests/ -v -k "not test_pipeline"   # skip FFmpeg integration tests
pytest backend/tests/ -v                            # all tests (needs FFmpeg)
```

---

## 8. Docker (Alternative to manual setup)

If you have Docker installed, this replaces all the above:

```bash
cd ~/Claude_code/golf-tracer
docker-compose up --build
# Backend at http://localhost:8000
```

---

## Architecture Reminder

```
Video → YOLO detect → Impact detection → ByteTrack → Kalman smooth → Tracer render → FFmpeg export
```

Key files:
- `backend/pipeline/pipeline.py` — CV pipeline orchestrator
- `backend/pipeline/detector.py` — YOLOv11 + Hough fallback
- `backend/rendering/tracer_renderer.py` — gradient/glow tracer
- `mobile/src/screens/ResultScreen.tsx` — video + SVG tracer overlay
- `mobile/src/components/TracerOverlay.tsx` — SVG path synced to playback
