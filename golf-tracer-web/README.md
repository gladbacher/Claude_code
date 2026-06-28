# ⛳ Golf Tracer (Web)

Trace a golf shot right in your browser. Load a swing clip, mark the ball as it
flies, and a smooth glowing tracer draws on top — then export it as a video.

This is the **v1, beginner-friendly web version**. There is **nothing to install**:
no Python, no Expo, no phone, no FFmpeg, no model downloads. Just plain
HTML/CSS/JavaScript and one command to serve it.

> A native phone app is planned for **v2**. This web version exists so you can
> get something working in minutes and understand how the pieces fit together
> before adding the harder stuff.

---

## Run it (Mac)

You need a tiny local web server because the app is split into JavaScript
modules (browsers block those when you open a file directly). Your Mac already
has Python, which can serve files in one line.

```bash
cd golf-tracer-web
python3 -m http.server 8000
```

Then open **http://localhost:8000** in your browser (Chrome works best).

To stop the server later, press `Ctrl + C` in the terminal.

---

## How to use it

1. **Load video** — click *Choose video* and pick a short golf swing clip
   (a few seconds, ball clearly visible). Or drag a file onto the black area.
2. **Mark the ball** — *Marking* is ON by default. Pause near impact, then use
   the ⏭ frame button and **click on the ball** every few frames as it flies.
   Each click drops a point; the tracer connects them with a smooth curve.
   - Got a point wrong? Click the right spot at the same moment to fix it, or
     use **Undo** / **Clear**.
   - Want a head start? Click the ball once or twice just after impact, then
     open **Auto-detect helper** → it tracks the ball through the rest of the
     flight from your marks. Tidy up any stray points by clicking.
3. **Style it** — pick the tracer color, thickness, and glow.
4. **Export** — click *Export video*. The clip plays once while it records,
   then downloads `golf-tracer.webm` to your Downloads folder.

---

## What's in here

```
golf-tracer-web/
├── index.html      The page layout (buttons, sliders, the canvas)
├── styles.css      All the styling (one file, plain CSS)
├── src/
│   ├── main.js     Wires everything together + the draw loop
│   ├── tracer.js   Turns points into a smooth glowing line
│   ├── detect.js   The auto-detect (motion) helper
│   └── export.js   Records the canvas to a video file
├── README.md       You are here
└── LEARN.md        A friendly walkthrough of HOW it all works
```

New to this? Read **[LEARN.md](LEARN.md)** — it explains each part in plain
language and points you at exactly which file to open.

---

## Tips for a good trace

- **Shorter clips are easier.** Trim to just the shot if you can.
- **Mark more points through the curve** of the flight — straight sections need
  fewer, the bending part needs more.
- The exported file is `.webm`. It plays in Chrome/Firefox and most modern
  players. (Converting to `.mp4` is a v2 nice-to-have.)

## Known limits (honest list)

- Auto-detect works best when you **seed it** — click the ball once or twice at
  the start of the flight, then run it and it tracks the rest. With no seed it
  guesses blindly and can be fooled by the club or body. It's still classic
  computer vision, not a trained model, so treat it as a strong first pass.
- Frame stepping assumes ~30 fps. If your clip is 60/120 fps the steps are just
  a little coarse; clicking still works perfectly.
- Export has no audio (not needed for a tracer) and produces `.webm`.

These are all deliberate v1 simplifications — see LEARN.md for how we'd grow
past them.
