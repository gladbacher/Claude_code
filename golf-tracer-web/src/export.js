// export.js — record the canvas (video + tracer) into a downloadable file.
//
// Browsers can "capture" a canvas as a live video stream, and MediaRecorder
// can record that stream to a file. So to export, we just:
//   1. start recording the canvas,
//   2. play the clip from the beginning (the render loop keeps painting the
//      video + tracer onto the canvas), and
//   3. stop when the clip ends, then hand back the recorded file.
//
// We export to .webm — the format browsers can record natively without any
// extra tools like FFmpeg.

/** Pick a webm format the current browser can actually record. */
function pickMimeType() {
  const candidates = [
    "video/webm;codecs=vp9",
    "video/webm;codecs=vp8",
    "video/webm",
  ];
  for (const type of candidates) {
    if (window.MediaRecorder && MediaRecorder.isTypeSupported(type)) return type;
  }
  return "video/webm";
}

/**
 * Record the canvas while the clip plays once through.
 *
 * @param canvas  the visible canvas (already being drawn to by the render loop)
 * @param video   the <video> element we play to drive the animation
 * @param onProgress optional callback (0..1)
 * @returns Promise<Blob> the recorded video file
 */
export function exportTracer(canvas, video, onProgress) {
  return new Promise((resolve, reject) => {
    if (!window.MediaRecorder) {
      reject(new Error("This browser can't record video (no MediaRecorder)."));
      return;
    }

    const stream = canvas.captureStream(30); // 30 frames per second
    const recorder = new MediaRecorder(stream, {
      mimeType: pickMimeType(),
      videoBitsPerSecond: 8_000_000,
    });

    const chunks = [];
    recorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) chunks.push(e.data);
    };
    recorder.onstop = () => {
      resolve(new Blob(chunks, { type: "video/webm" }));
    };
    recorder.onerror = (e) => reject(e.error || new Error("Recording failed"));

    const onTime = () => {
      if (onProgress && video.duration) {
        onProgress(Math.min(1, video.currentTime / video.duration));
      }
    };
    const onEnded = () => {
      video.removeEventListener("timeupdate", onTime);
      video.removeEventListener("ended", onEnded);
      // Small delay so the final frame is definitely captured.
      setTimeout(() => recorder.stop(), 120);
    };

    video.addEventListener("timeupdate", onTime);
    video.addEventListener("ended", onEnded);

    // Start fresh from the beginning and roll.
    video.pause();
    video.currentTime = 0;
    video.muted = true;
    recorder.start();
    video.play().catch(reject);
  });
}

/** Trigger a browser download of a recorded Blob. */
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  // Give the download a moment to start before releasing the URL.
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
