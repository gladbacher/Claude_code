// detect.js — a simple "auto-detect" helper (beta).
//
// Real golf apps use machine-learning models (like YOLO) to find the ball.
// That's powerful but heavy to set up. For a first version we use a classic,
// dependency-free computer-vision trick instead: MOTION DETECTION.
//
// Idea: the ball is usually the thing that MOVES the most between two frames.
// So we step through the clip, compare each frame to the previous one, and
// guess the ball is wherever the biggest visual change happened.
//
// It won't be perfect (a swinging club or moving body also create motion),
// which is why it's a "starting point" you clean up by clicking. But it shows
// the core concept that all trackers build on: frame differencing.

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

/** Convert an RGBA frame to a simple grayscale brightness array. */
function toGray(imageData) {
  const { data, width, height } = imageData;
  const gray = new Float32Array(width * height);
  for (let i = 0; i < gray.length; i++) {
    const r = data[i * 4];
    const g = data[i * 4 + 1];
    const b = data[i * 4 + 2];
    gray[i] = 0.299 * r + 0.587 * g + 0.114 * b; // standard luminance
  }
  return gray;
}

/**
 * Run motion-based detection across the whole clip.
 *
 * @param video        the <video> element (will be seeked around)
 * @param onProgress   optional callback (0..1) for a progress bar
 * @returns array of normalized points {t, x, y} — one per frame where motion
 *          was confidently found.
 */
export async function autoDetect(video, onProgress) {
  const duration = video.duration;
  if (!duration || !isFinite(duration)) return [];

  // Work on a small copy of each frame — faster and less noisy.
  const W = 240;
  const H = Math.max(1, Math.round((video.videoHeight / video.videoWidth) * W));
  const work = document.createElement("canvas");
  work.width = W;
  work.height = H;
  const wctx = work.getContext("2d", { willReadFrequently: true });

  // Sample at most ~150 frames so very long clips don't take forever.
  const maxSamples = 150;
  const step = Math.max(1 / 60, duration / maxSamples);

  const wasPaused = video.paused;
  video.pause();

  let prevGray = null;
  const points = [];

  for (let t = 0; t < duration; t += step) {
    await seekTo(video, t);
    wctx.drawImage(video, 0, 0, W, H);
    const gray = toGray(wctx.getImageData(0, 0, W, H));

    if (prevGray) {
      // Find where the biggest brightness change happened.
      let maxDiff = 0;
      let sumX = 0, sumY = 0, sumW = 0;
      for (let y = 0; y < H; y++) {
        for (let x = 0; x < W; x++) {
          const i = y * W + x;
          const d = Math.abs(gray[i] - prevGray[i]);
          if (d > 25) {
            // Weight each changed pixel by how much it changed.
            sumX += x * d;
            sumY += y * d;
            sumW += d;
            if (d > maxDiff) maxDiff = d;
          }
        }
      }
      // Only keep frames with a clear, confident motion blob.
      if (sumW > 0 && maxDiff > 40) {
        points.push({
          t,
          x: (sumX / sumW) / W, // normalize back to 0..1
          y: (sumY / sumW) / H,
        });
      }
    }

    prevGray = gray;
    if (onProgress) onProgress(Math.min(1, t / duration));
  }

  if (onProgress) onProgress(1);
  if (!wasPaused) video.play();
  return points;
}
