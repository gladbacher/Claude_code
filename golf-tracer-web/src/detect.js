// detect.js — auto-detect the ball by TRACKING it, not just spotting motion.
//
// Real golf apps use machine-learning models (like YOLO) to find the ball.
// That's powerful but heavy to set up. Here we use classic, dependency-free
// computer vision that's still genuinely good — and easy to read.
//
// Two ideas do all the work:
//
//   1) MOTION BLOBS. Between two frames, the things that change are the ball,
//      the club, and the body. We don't average them all together (that was the
//      old, unreliable approach). Instead we find separate "blobs" of motion
//      (connected clusters of changed pixels) and treat each as a candidate.
//
//   2) TRAJECTORY FOLLOWING. A golf ball flies a smooth arc. So once we know
//      roughly where it is and how fast it's moving, we can PREDICT where it'll
//      be next and pick the blob closest to that prediction. The body and club
//      create motion too — but not where the ball is heading, so they get
//      rejected automatically.
//
// Best results come from SEEDING: you click the ball once or twice at the start
// of the flight, and the tracker follows it from there. Seeding tells us what
// we're chasing and which way it's going — a huge reliability boost.

// ---------- small geometry helpers ----------
const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);

/** Seek the video to a time and wait until that frame is actually ready. */
function seekTo(video, time) {
  return new Promise((resolve) => {
    const onSeeked = () => {
      video.removeEventListener("seeked", onSeeked);
      resolve();
    };
    video.addEventListener("seeked", onSeeked);
    video.currentTime = time;
  });
}

/** Grab the current frame as a grayscale brightness array (0..255). */
function grayFrame(video, wctx, W, H) {
  wctx.drawImage(video, 0, 0, W, H);
  const { data } = wctx.getImageData(0, 0, W, H);
  const gray = new Float32Array(W * H);
  for (let i = 0; i < gray.length; i++) {
    gray[i] = 0.299 * data[i * 4] + 0.587 * data[i * 4 + 1] + 0.114 * data[i * 4 + 2];
  }
  return gray;
}

/**
 * Find blobs of motion between two grayscale frames.
 *
 * We threshold the per-pixel brightness change into an on/off mask, then run a
 * flood fill ("connected components") to group touching changed pixels into
 * separate blobs. For each blob we record its size and center.
 *
 * @returns array of { x, y (pixels), area, motion } — one per blob.
 */
function motionBlobs(gray, prev, W, H, threshold) {
  const N = W * H;
  const mask = new Uint8Array(N);
  const diff = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    const d = Math.abs(gray[i] - prev[i]);
    if (d > threshold) {
      mask[i] = 1;
      diff[i] = d;
    }
  }

  const visited = new Uint8Array(N);
  const blobs = [];
  const stack = [];

  for (let start = 0; start < N; start++) {
    if (!mask[start] || visited[start]) continue;
    // Flood fill this blob (4-connected) without recursion.
    stack.length = 0;
    stack.push(start);
    visited[start] = 1;
    let area = 0, sumX = 0, sumY = 0, motion = 0;

    while (stack.length) {
      const i = stack.pop();
      const x = i % W;
      const y = (i / W) | 0;
      area++;
      sumX += x;
      sumY += y;
      motion += diff[i];
      // visit the 4 neighbors
      if (x > 0 && mask[i - 1] && !visited[i - 1]) { visited[i - 1] = 1; stack.push(i - 1); }
      if (x < W - 1 && mask[i + 1] && !visited[i + 1]) { visited[i + 1] = 1; stack.push(i + 1); }
      if (y > 0 && mask[i - W] && !visited[i - W]) { visited[i - W] = 1; stack.push(i - W); }
      if (y < H - 1 && mask[i + W] && !visited[i + W]) { visited[i + W] = 1; stack.push(i + W); }
    }
    if (area >= 2) blobs.push({ x: sumX / area, y: sumY / area, area, motion });
  }
  return blobs;
}

/**
 * Track the ball across the clip.
 *
 * @param video      the <video> element (will be seeked around)
 * @param options.seeds  user-marked points {t,x,y} (normalized). 1+ recommended.
 * @param options.onProgress  callback (0..1) for the progress bar
 * @returns array of normalized points {t,x,y} forming the ball path.
 */
export async function autoDetect(video, options = {}) {
  const { seeds = [], onProgress } = options;
  const duration = video.duration;
  if (!duration || !isFinite(duration)) return [];

  // Work on a downscaled copy of each frame: faster, and small noise averages out.
  const W = 320;
  const H = Math.max(1, Math.round((video.videoHeight / video.videoWidth) * W));
  const work = document.createElement("canvas");
  work.width = W;
  work.height = H;
  const wctx = work.getContext("2d", { willReadFrequently: true });

  // Sample up to ~240 frames so even longer clips finish quickly.
  const step = Math.max(1 / 120, duration / 240);
  const THRESH = 22;               // brightness change that counts as "motion"
  const MAX_COAST = 6;             // frames we'll keep predicting through an occlusion
  const MAX_BALL_AREA = 260;       // blobs bigger than this are likely body/club

  const wasPaused = video.paused;
  video.pause();

  // ----- decide where tracking starts -----
  const sorted = [...seeds].sort((a, b) => a.t - b.t);
  const track = sorted.slice();    // keep the user's seed points
  let pos = null;                  // current ball position (normalized)
  let vel = { x: 0, y: 0 };        // velocity (normalized units per second)
  let startT = 0;

  if (sorted.length >= 1) {
    const last = sorted[sorted.length - 1];
    pos = { x: last.x, y: last.y };
    startT = last.t;
    if (sorted.length >= 2) {
      const prev = sorted[sorted.length - 2];
      const dt = last.t - prev.t || step;
      vel = { x: (last.x - prev.x) / dt, y: (last.y - prev.y) / dt };
    }
  }

  // Baseline frame to diff against.
  await seekTo(video, startT);
  let prevGray = grayFrame(video, wctx, W, H);
  let missed = 0;

  for (let t = startT + step; t < duration; t += step) {
    await seekTo(video, t);
    const gray = grayFrame(video, wctx, W, H);
    const blobs = motionBlobs(gray, prevGray, W, H, THRESH);
    prevGray = gray;

    // Normalize blob centers to 0..1.
    const cands = blobs.map((b) => ({ x: b.x / W, y: b.y / H, area: b.area, motion: b.motion }));

    if (pos) {
      // ----- SEEDED / TRACKING mode: follow the predicted arc -----
      const dt = step;
      const predict = { x: pos.x + vel.x * dt, y: pos.y + vel.y * dt };
      const speed = Math.hypot(vel.x, vel.y);
      const acquiring = speed < 1e-6;           // single seed → don't know direction yet
      // Search window grows with speed; wide while still "acquiring".
      const radius = acquiring ? 0.22 : Math.min(0.35, Math.max(0.07, speed * dt * 2 + 0.05));

      let best = null, bestScore = Infinity;
      for (const c of cands) {
        const d = dist(c, predict);
        if (d > radius) continue;               // gate: ignore motion far from the arc
        // Prefer the candidate closest to the prediction, nudging toward small,
        // compact blobs (the ball) over large ones (body/club).
        const areaPenalty = c.area > MAX_BALL_AREA ? 0.02 : 0;
        const score = d + c.area * 0.00015 + areaPenalty;
        if (score < bestScore) { bestScore = score; best = c; }
      }

      if (best) {
        const measVel = { x: (best.x - pos.x) / dt, y: (best.y - pos.y) / dt };
        // Blend new velocity with old to stay smooth (a light "low-pass filter").
        vel = acquiring
          ? measVel
          : { x: 0.6 * measVel.x + 0.4 * vel.x, y: 0.6 * measVel.y + 0.4 * vel.y };
        pos = { x: best.x, y: best.y };
        missed = 0;
        track.push({ t, x: pos.x, y: pos.y });
      } else {
        // Lost it this frame (motion blur / occlusion): coast on the prediction,
        // but don't record a point — the tracer interpolates across the gap.
        pos = predict;
        missed++;
        if (missed > MAX_COAST) break;
      }

      // Ball has left the frame — we're done.
      if (pos.x < -0.03 || pos.x > 1.03 || pos.y < -0.03 || pos.y > 1.03) break;
    } else {
      // ----- BLIND mode (no seeds): weaker fallback -----
      // Pick the most energetic *small, compact* blob as a ball guess. This is
      // far less reliable than seeding — marking the ball once is much better.
      const ballish = cands
        .filter((c) => c.area <= MAX_BALL_AREA && c.motion > THRESH * 4)
        .sort((a, b) => b.motion - a.motion)[0];
      if (ballish) track.push({ t, x: ballish.x, y: ballish.y });
    }

    if (onProgress) onProgress(Math.min(1, t / duration));
  }

  if (onProgress) onProgress(1);
  if (!wasPaused) video.play();
  // Return points sorted by time so the tracer reads cleanly.
  return track.sort((a, b) => a.t - b.t);
}
