// main.js — wires the whole app together.
//
// This is the "conductor": it owns the app state, grabs the on-screen
// controls, runs the draw loop, and connects buttons/sliders to actions.
// The heavy lifting lives in the smaller modules:
//   tracer.js  → draws the smooth glowing line
//   detect.js  → the auto-detect (motion) helper
//   export.js  → records the canvas to a video file

import { drawTracer } from "./tracer.js";
import { autoDetect } from "./detect.js";
import { exportTracer, downloadBlob } from "./export.js";

// ----- Grab elements from the page -----
const $ = (id) => document.getElementById(id);

const video = $("video");
const canvas = $("canvas");
const ctx = canvas.getContext("2d");

const dropHint = $("dropHint");
const stage = $("stage");
const fileInput = $("fileInput");

const playBtn = $("playBtn");
const frameBackBtn = $("frameBackBtn");
const frameFwdBtn = $("frameFwdBtn");
const scrubber = $("scrubber");
const timeLabel = $("timeLabel");

const markModeBtn = $("markModeBtn");
const undoBtn = $("undoBtn");
const clearBtn = $("clearBtn");
const pointCount = $("pointCount");
const autoBtn = $("autoBtn");
const autoProgress = $("autoProgress");

const colorInput = $("colorInput");
const widthInput = $("widthInput");
const glowInput = $("glowInput");
const dotInput = $("dotInput");
const widthVal = $("widthVal");
const glowVal = $("glowVal");

const exportBtn = $("exportBtn");
const exportStatus = $("exportStatus");

// ----- App state -----
const state = {
  loaded: false,
  markMode: true,
  points: [], // each: { t (seconds), x, y } with x,y normalized 0..1
  style: {
    color: colorInput.value,
    width: Number(widthInput.value),
    glow: Number(glowInput.value),
    showDot: dotInput.checked,
  },
};

const FPS_GUESS = 30; // used only for the frame-step buttons
const frameStep = 1 / FPS_GUESS;

// ----- The draw loop -----
// Runs ~60x/second. Each tick: paint the current video frame onto the canvas,
// then paint the tracer on top. Because everything lives on one canvas, the
// exporter can record the video and tracer together.
function render() {
  if (state.loaded && video.readyState >= 2) {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    drawTracer(ctx, canvas.width, canvas.height, state.points, video.currentTime, state.style);
  }
  // Keep the scrubber + time readout in sync while playing.
  if (state.loaded) {
    scrubber.value = String(video.currentTime);
    timeLabel.textContent = `${video.currentTime.toFixed(2)}s / ${(video.duration || 0).toFixed(2)}s`;
  }
  requestAnimationFrame(render);
}
requestAnimationFrame(render);

// ----- Loading a video -----
function loadVideoFile(file) {
  if (!file) return;
  const url = URL.createObjectURL(file);
  video.src = url;
  video.onloadedmetadata = () => {
    // Match the canvas to the video's real pixel size so coordinates are simple.
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    scrubber.max = String(video.duration || 0);

    state.loaded = true;
    state.points = [];
    dropHint.style.display = "none";
    enableControls(true);
    updatePointCount();
  };
}

function enableControls(on) {
  [playBtn, frameBackBtn, frameFwdBtn, scrubber, markModeBtn, undoBtn,
   clearBtn, autoBtn, exportBtn].forEach((el) => (el.disabled = !on));
}

fileInput.addEventListener("change", (e) => loadVideoFile(e.target.files[0]));

// Drag & drop onto the stage.
stage.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropHint.classList.add("dragover");
});
stage.addEventListener("dragleave", () => dropHint.classList.remove("dragover"));
stage.addEventListener("drop", (e) => {
  e.preventDefault();
  dropHint.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("video/")) loadVideoFile(file);
});

// ----- Playback controls -----
playBtn.addEventListener("click", () => {
  if (video.paused) video.play();
  else video.pause();
});
video.addEventListener("play", () => (playBtn.textContent = "⏸ Pause"));
video.addEventListener("pause", () => (playBtn.textContent = "▶︎ Play"));

frameBackBtn.addEventListener("click", () => {
  video.pause();
  video.currentTime = Math.max(0, video.currentTime - frameStep);
});
frameFwdBtn.addEventListener("click", () => {
  video.pause();
  video.currentTime = Math.min(video.duration || 0, video.currentTime + frameStep);
});

scrubber.addEventListener("input", () => {
  video.pause();
  video.currentTime = Number(scrubber.value);
});

// ----- Marking the ball -----
markModeBtn.addEventListener("click", () => {
  state.markMode = !state.markMode;
  markModeBtn.textContent = state.markMode ? "🎯 Marking: ON" : "🎯 Marking: OFF";
  markModeBtn.classList.toggle("off", !state.markMode);
});

canvas.addEventListener("click", (e) => {
  if (!state.loaded || !state.markMode) return;
  // Convert the click position into a 0..1 fraction of the frame.
  const rect = canvas.getBoundingClientRect();
  const x = (e.clientX - rect.left) / rect.width;
  const y = (e.clientY - rect.top) / rect.height;
  const t = video.currentTime;

  // If we already have a point very close in time, replace it (re-clicking to
  // fix a position) instead of adding a duplicate.
  const near = state.points.findIndex((p) => Math.abs(p.t - t) < frameStep / 2);
  if (near >= 0) state.points[near] = { t, x, y };
  else state.points.push({ t, x, y });

  updatePointCount();
});

undoBtn.addEventListener("click", () => {
  state.points.pop();
  updatePointCount();
});
clearBtn.addEventListener("click", () => {
  state.points = [];
  updatePointCount();
});
function updatePointCount() {
  pointCount.textContent = `Points: ${state.points.length}`;
}

// ----- Auto-detect (beta) -----
autoBtn.addEventListener("click", async () => {
  autoBtn.disabled = true;
  autoProgress.hidden = false;
  autoProgress.value = 0;
  const wasMark = state.markMode;
  state.markMode = false;
  try {
    const found = await autoDetect(video, (p) => (autoProgress.value = p));
    if (found.length) {
      state.points = found;
      updatePointCount();
    } else {
      alert("Auto-detect didn't find a confident ball path. Try marking by hand.");
    }
  } catch (err) {
    console.error(err);
    alert("Auto-detect failed: " + err.message);
  } finally {
    autoProgress.hidden = true;
    autoBtn.disabled = false;
    state.markMode = wasMark;
    video.currentTime = 0;
  }
});

// ----- Tracer style -----
colorInput.addEventListener("input", () => (state.style.color = colorInput.value));
widthInput.addEventListener("input", () => {
  state.style.width = Number(widthInput.value);
  widthVal.textContent = widthInput.value;
});
glowInput.addEventListener("input", () => {
  state.style.glow = Number(glowInput.value);
  glowVal.textContent = glowInput.value;
});
dotInput.addEventListener("change", () => (state.style.showDot = dotInput.checked));

// ----- Export -----
exportBtn.addEventListener("click", async () => {
  if (state.points.length < 2) {
    alert("Mark at least 2 points first so there's a tracer to export.");
    return;
  }
  exportBtn.disabled = true;
  const wasMark = state.markMode;
  state.markMode = false;
  exportStatus.textContent = "Recording… the clip will play once through.";
  try {
    const blob = await exportTracer(canvas, video, (p) => {
      exportStatus.textContent = `Recording… ${Math.round(p * 100)}%`;
    });
    downloadBlob(blob, "golf-tracer.webm");
    exportStatus.textContent = "Done! Saved golf-tracer.webm to your Downloads.";
  } catch (err) {
    console.error(err);
    exportStatus.textContent = "Export failed: " + err.message;
  } finally {
    video.pause();
    state.markMode = wasMark;
    exportBtn.disabled = false;
  }
});
