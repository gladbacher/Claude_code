# Weekly Content Pipeline

One filmed video per week is the master asset. Everything else — newsletter, shorts — is derived from it, never written separately. You present; the pipeline supplies the argument, the script, and the derivatives.

## The week

| Day | Step | Effort | Output |
|-----|------|--------|--------|
| Mon | **Radar** — run the news-radar prompt (`news-radar.md`) or `/content-week` | 10 min review | 3 candidate angles, ranked |
| Mon | **Pick** — choose one angle, reply with the pick | 2 min | Locked topic |
| Tue | **Script** — generate master script with the master-video prompt (`prompts.md` §1) | 20 min edit pass | 6–8 min video script |
| Wed | **Film** — one take ethos, direct to camera, single light | 1–2 hrs | Master video |
| Thu | **Derive** — feed the *final spoken transcript* (not the script) into the derivation prompts (§2–3) | 30 min edit | Newsletter + 3 shorts cut-sheets |
| Fri | **Publish video + newsletter.** Shorts drip Sat/Mon/Wed | — | — |

Total writing/desk effort: roughly one hour a week. The only step that can't be delegated is filming and the Monday pick.

## Rules that keep it coherent

1. **Master-first.** Shorts are cut from the video (cut-sheets give timestamp + hook + caption), so face, tone, and argument stay consistent. Never script a short from scratch unless it's a reactive piece (see `news-radar.md` §Reactive formats).
2. **Derive from the transcript, not the script.** What you actually said on camera is the source of truth — it carries your phrasing, and the newsletter should sound like you.
3. **One mechanism per week.** Every video names exactly one extraction mechanism with one number. Breadth is the enemy; the series already establishes the big picture.
4. **Every video lands on the same spine.** Whatever the week's topic: (a) here's the mechanism, (b) here's who profits, (c) here's the story you're being told instead, (d) here's the ask. The spine is what makes a one-off viewer recognise the series.
5. **CTA rotation.** Cycle follow → share → MP question → recruit. Never two identical CTAs in consecutive weeks.

## Freshness system (so it never goes stale)

Rotate through four lenses; each week's angle must come from a different lens than the last:

- **NEWS** — react to something from the radar (a results announcement, a policy story, a viral post). Highest reach, shortest shelf life.
- **MECHANISM** — explain one extraction machine in detail (pension fees, sale-and-leaseback, threshold freezes...). The backbone. Bank of unexploited mechanisms lives in `prompts.md` §4.
- **REBUTTAL** — steelman and dismantle one opposition argument ("they'll leave", "it's a politics of envy", "wealth taxes failed in France"). Great comment-section fuel.
- **HUMAN** — one person's numbers walked through end to end ("Margaret, 71, owns a £350k house..."). Composite characters, clearly framed as typical, never real identifiable people.

A NEWS week can substitute at any time — a strong radar hit always beats the rotation.

## Files

- `prompts.md` — the prompt library (master video, newsletter, shorts, idea bank)
- `news-radar.md` — sources, the radar prompt, reactive short formats
- `/content-week` command (`commands/content-week.md`) — runs radar + drafting inside Claude Code in one shot
