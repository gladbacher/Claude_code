# Golf Tracer — System Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Mobile App (React Native / Expo)                           │
│  Android primary target                                      │
│  ┌──────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐ │
│  │ Record / │  │Processing │  │  Result   │  │  Export  │ │
│  │ Import   │→ │  Screen   │→ │  Screen   │→ │  Screen  │ │
│  └──────────┘  └───────────┘  └───────────┘  └──────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS / REST API
┌─────────────────────▼───────────────────────────────────────┐
│  FastAPI Backend                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ API Layer: /videos  /jobs  /frames  /corrections      │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │ CV Pipeline                                           │   │
│  │  Detector → ImpactDetector → Tracker → Smoother      │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │ Rendering                                             │   │
│  │  TracerRenderer → FrameComposer → VideoWriter/FFmpeg  │   │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  Storage: LocalStorage (dev) / S3-compatible (prod)         │
│  Database: SQLite (dev) / PostgreSQL (prod)                  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Upload**: Mobile uploads video → stored on backend → metadata extracted
2. **Job creation**: Client creates a job referencing the video ID
3. **Processing**: Background worker runs the CV pipeline:
   - Extract frames in batches of 30
   - Detect ball in each frame (YOLO)
   - Find impact frame (kinematic + photometric signals)
   - Track ball post-impact (ByteTrack + optical flow bridge)
   - Smooth trajectory (Kalman + spline)
   - Store tracking points in DB
4. **Polling**: Mobile polls `/jobs/{id}/status` every 2s
5. **Result**: When done, client fetches `/jobs/{id}/result` (TrackingPoint[])
6. **Overlay**: Mobile renders SVG tracer overlay synced to video playback
7. **Corrections**: User can tap frames to override tracking positions
8. **Export**: Backend renders tracer onto video frames via FFmpeg

## Component Contracts

### TracerConfig (shared between backend and mobile)

```json
{
  "color": "#FF6B00",
  "thickness": 4,
  "opacity": 0.85,
  "glow_radius": 8,
  "glow_opacity": 0.4,
  "trail_length": 30,
  "fade_tail": true,
  "fade_exponent": 2.0
}
```

### TrackingPoint (normalized coordinates)

```json
{
  "frame": 142,
  "x": 0.612,
  "y": 0.234,
  "confidence": 0.92,
  "is_interpolated": false,
  "is_manual": false
}
```
