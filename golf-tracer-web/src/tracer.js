// tracer.js — turns a list of ball positions into a smooth, glowing line.
//
// Points are stored "normalized" (x and y are 0..1, a fraction of the frame
// width/height). That way they stay correct no matter what size we draw the
// canvas. Each point also has a time `t` (in seconds) — the moment in the clip
// when the ball was at that spot.
//
// The two exported functions are pure drawing helpers: give them points + a
// time + a style, and they paint the tracer. No DOM, no global state.

/** Linear interpolation between two points by a fraction f (0..1). */
function lerpPoint(a, b, f) {
  return { x: a.x + (b.x - a.x) * f, y: a.y + (b.y - a.y) * f };
}

/**
 * Work out which part of the path should be visible at a given time.
 * The line "grows" with the clip: fully drawn between points we've already
 * passed, and partially drawn into the segment we're currently inside.
 *
 * @returns array of normalized {x,y} points to draw (may be empty).
 */
export function visiblePoints(points, time) {
  if (points.length === 0) return [];
  const sorted = [...points].sort((a, b) => a.t - b.t);

  const visible = [];
  for (const p of sorted) {
    if (p.t <= time) visible.push(p);
    else break; // sorted by time, so we can stop early
  }

  // Add a moving "tip" between the last passed point and the next one.
  const lastIdx = visible.length - 1;
  const next = sorted[lastIdx + 1];
  if (visible.length >= 1 && next) {
    const a = sorted[lastIdx];
    const span = next.t - a.t;
    const f = span > 0 ? Math.min(1, Math.max(0, (time - a.t) / span)) : 0;
    visible.push(lerpPoint(a, next, f));
  }
  return visible;
}

/**
 * Build a smooth Path2D through the given pixel points using a Catmull-Rom
 * spline (converted to cubic Bézier segments). This is what makes the tracer
 * curve gracefully instead of looking like connected straight lines.
 */
function smoothPath(pts) {
  const path = new Path2D();
  if (pts.length === 0) return path;
  path.moveTo(pts[0].x, pts[0].y);
  if (pts.length === 1) return path;

  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] || pts[i];
    const p1 = pts[i];
    const p2 = pts[i + 1];
    const p3 = pts[i + 2] || p2;
    // Catmull-Rom → Bézier control points (tension 1/6 is the standard).
    const c1x = p1.x + (p2.x - p0.x) / 6;
    const c1y = p1.y + (p2.y - p0.y) / 6;
    const c2x = p2.x - (p3.x - p1.x) / 6;
    const c2y = p2.y - (p3.y - p1.y) / 6;
    path.bezierCurveTo(c1x, c1y, c2x, c2y, p2.x, p2.y);
  }
  return path;
}

/**
 * Draw the tracer onto a canvas context.
 *
 * @param ctx    canvas 2D context
 * @param w,h    canvas pixel size (used to convert normalized → pixels)
 * @param points all marked ball positions ({t,x,y} normalized)
 * @param time   current clip time in seconds
 * @param style  { color, width, glow, showDot }
 */
export function drawTracer(ctx, w, h, points, time, style) {
  const norm = visiblePoints(points, time);
  if (norm.length === 0) return;

  // Convert normalized points to pixel coordinates for this canvas size.
  const pts = norm.map((p) => ({ x: p.x * w, y: p.y * h }));

  ctx.save();
  ctx.lineCap = "round";
  ctx.lineJoin = "round";

  if (pts.length >= 2) {
    const path = smoothPath(pts);
    // Glow pass: a soft, wide, semi-transparent stroke underneath.
    if (style.glow > 0) {
      ctx.shadowColor = style.color;
      ctx.shadowBlur = style.glow;
      ctx.strokeStyle = style.color;
      ctx.globalAlpha = 0.5;
      ctx.lineWidth = style.width;
      ctx.stroke(path);
    }
    // Crisp pass: the solid line on top.
    ctx.shadowBlur = 0;
    ctx.globalAlpha = 1;
    ctx.strokeStyle = style.color;
    ctx.lineWidth = style.width;
    ctx.stroke(path);
  }

  // The ball "dot" at the leading tip of the tracer.
  if (style.showDot) {
    const tip = pts[pts.length - 1];
    const r = Math.max(3, style.width * 0.9);
    ctx.shadowColor = style.color;
    ctx.shadowBlur = style.glow;
    ctx.fillStyle = "#ffffff";
    ctx.globalAlpha = 1;
    ctx.beginPath();
    ctx.arc(tip.x, tip.y, r, 0, Math.PI * 2);
    ctx.fill();
  }

  ctx.restore();
}
