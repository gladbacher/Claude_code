# How Golf Tracer works — a beginner's walkthrough

This guide explains the app in plain language. Read it with the code open
side-by-side. Every section tells you which file to look at. Don't worry if
some of it is new — the goal is to understand the *shape* of how a tracer app
works, not to memorize anything.

---

## The big picture

A "golf tracer" is really just three ideas glued together:

1. **Where is the ball in each moment of the clip?** (a list of positions over time)
2. **Draw a smooth line through those positions** (the tracer)
3. **Reveal the line in sync with the video, and save the result** (export)

That's it. Everything in this project is one of those three ideas. Here's the
flow:

```
Load clip → mark/detect ball positions → draw smooth line → reveal + export
            └─ src/detect.js ─┘          └─ src/tracer.js ─┘   └─ src/export.js ─┘
                         all coordinated by src/main.js
```

---

## Key idea #1: a video is just a stack of images

When you play a video, the browser is flipping through still images ("frames")
very fast — usually 30 or 60 per second. The `<video>` element knows the
**current time** (e.g. "1.40 seconds in"), and at any time we can copy the
current frame onto a `<canvas>` and draw on top of it.

In **`src/main.js`**, look at the `render()` function:

```js
ctx.drawImage(video, 0, 0, canvas.width, canvas.height); // paint the frame
drawTracer(...);                                          // paint the tracer on top
```

This runs ~60 times a second (`requestAnimationFrame`). That single canvas —
video frame + tracer — is both what you *see* and what we *record* when
exporting. Keeping them on one canvas is the trick that lets export "just work".

---

## Key idea #2: the ball path is a list of points

We store the ball's path as a simple list. Each entry is:

```js
{ t: 1.40, x: 0.62, y: 0.35 }
```

- `t` is **when** (seconds into the clip).
- `x` and `y` are **where**, but stored as a *fraction* of the frame
  (0 = left/top edge, 1 = right/bottom edge). Storing fractions instead of
  pixels means the path stays correct even if we draw the canvas bigger or
  smaller. This "normalized coordinates" idea is everywhere in graphics.

Two ways to fill this list:

- **By hand:** in `src/main.js`, the `canvas.addEventListener("click", ...)`
  handler converts your click into `{t, x, y}` and adds it. Simple and reliable.
- **Automatically:** `src/detect.js` tries to find the ball for you.

---

## Key idea #3: finding the ball automatically (tracking)

Open **`src/detect.js`**. Real apps use machine-learning models (like YOLO) to
recognize a ball. That's powerful but heavy. We get surprisingly far with two
classic, dependency-free ideas instead.

**1. Motion blobs (not a global average).** Between two frames, the things that
change are the ball, the club, and the body. A naive approach averages *all*
the changed pixels — but then the body and club drag the guess away from the
ball (this was the app's first, unreliable version). Instead we find separate
*blobs* of motion: we threshold the frame difference into on/off pixels, then
run a **flood fill** (`motionBlobs`) to group touching changed pixels into
distinct clusters. Now the ball is its own candidate, separate from the body.

**2. Trajectory following.** A golf ball flies a smooth arc. So once we know
roughly where it is and how fast it's moving, we **predict** where it should be
next (`position + velocity × time`) and pick the blob closest to that
prediction. The body and club create motion too — but not where the ball is
heading, so they fall outside our search window and get ignored. After each
hit we update the velocity (lightly blended with the old one to stay smooth —
a mini "low-pass filter"), and if the ball briefly disappears behind motion
blur we *coast* on the prediction for a few frames.

This is a tiny version of how professional trackers (Kalman filters, ByteTrack)
work: predict, then match. **Seeding** makes it shine — when you click the ball
once or twice first, you're telling the tracker exactly what to chase and which
way it's going, so it locks on reliably. The leap to "real" detection is just
swapping the blob finder for a smarter one; the tracking logic around it stays
the same. That's the payoff of keeping things modular.

---

## Key idea #4: turning points into a smooth line

Open **`src/tracer.js`**. If you just connected the points with straight lines,
the tracer would look jagged. Instead we use a **Catmull-Rom spline** — a
standard way to draw a smooth curve that passes *through* every point. The
function `smoothPath()` converts the points into gentle Bézier curves.

The glow is a cheap, nice-looking trick: we draw the line **twice**:

1. a wide, semi-transparent, blurred stroke (the glow), then
2. a crisp solid stroke on top.

Plus a white dot at the leading tip to read as "the ball".

### Revealing the line over time

We don't draw the whole path at once — it should *grow* as the ball flies. The
`visiblePoints(points, time)` function figures out how much of the path to show
at the current moment: all points we've already passed, plus a moving "tip"
interpolated into the segment we're currently inside. Because `render()` calls
this every frame with the live `video.currentTime`, the line draws itself in
perfect sync with playback. No timers, no manual animation — the video's clock
*is* the animation clock.

---

## Key idea #5: exporting

Open **`src/export.js`**. Browsers can hand a `<canvas>` to a `MediaRecorder`
as a live video stream. So exporting is just:

1. start recording the canvas,
2. play the clip from the start (the render loop keeps painting frame+tracer),
3. stop when it ends and download the recorded `.webm`.

No FFmpeg, no server — the browser does it all.

---

## How `main.js` ties it together

`src/main.js` is the conductor:

- holds the **state** (the points list + tracer style),
- runs the **render loop**,
- connects every **button/slider** to an action,
- calls into `detect.js`, `tracer.js`, and `export.js` at the right moments.

A good way to learn: open `main.js`, pick one button (say, *Undo*), and trace
what it does. Then try a small change (see below).

---

## Try changing something (best way to learn)

Small, safe experiments — edit, save, refresh the browser:

1. **New default color:** in `index.html`, change the color input's
   `value="#ffcc00"` to `#00e5ff`. Refresh — the tracer starts cyan.
2. **Thicker glow:** in `src/tracer.js`, change `ctx.globalAlpha = 0.5` in the
   glow pass to `0.8`. See how the halo intensifies.
3. **Detection sensitivity:** in `src/detect.js`, `const THRESH = 22` decides
   how big a brightness change counts as "motion". Lower it (e.g. `15`) to catch
   fainter movement, raise it to ignore small jitter. Nearby, `MAX_COAST` sets
   how many blurred/hidden frames the tracker will guess through before giving
   up.
4. **More frame-step precision:** in `src/main.js`, change `FPS_GUESS = 30` to
   `60` if your clips are 60fps, for finer stepping.

Break something? Open the browser's **Developer Console** (View → Developer →
JavaScript Console in Chrome) — errors show up there with the file and line.

---

## Where v2 goes from here

This v1 is intentionally simple. Natural next steps, roughly easiest-first:

- **Smarter detection:** swap `detect.js` for a real ball model (e.g. a small
  ML model running in the browser via ONNX/TensorFlow.js, or a Python backend).
- **Impact detection:** auto-find the exact frame the club hits the ball, so
  the tracer starts itself.
- **Smoothing/physics:** fit the path to a realistic projectile arc so a few
  rough points still produce a clean flight.
- **MP4 export & audio**, and presets for cricket/baseball/tennis.
- **The phone app (v2 proper):** wrap this logic in React Native so it runs on
  a phone with the camera.

Each of those is a self-contained upgrade — because the app is split into small
files with clear jobs, you can improve one without rewriting the rest. That's
the real lesson here: good structure makes hard features approachable.
