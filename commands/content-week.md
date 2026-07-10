---
description: Run the weekly inequality-series content cycle - news radar, angle pick, then master script (and derivatives from a transcript if provided).
---

# Content Week Command

Runs one full week of the content pipeline defined in `content/inequality-series/pipeline/`. Read these files first, in order: `content/inequality-series/memory.md` (current state — last topic/lens/CTA, standing claims, active direction memo), then `pipeline/README.md`, `pipeline/prompts.md`, `pipeline/news-radar.md`, and any direction memo named in memory.md. They are the source of truth for tone, structure, and prompts. The newsletter and scripts in `content/inequality-series/` define the established voice; match it.

Work one step at a time in the order below; complete and present each step before starting the next. Do not combine steps into one response.

## Workflow

### Step 1 — Radar

Run web searches per the source list in `pipeline/news-radar.md` covering the last 7 days. Use `memory.md` for the last topic and lens (fall back to the most recent `weekly/` folder if memory.md is missing). Produce the three ranked angles in the radar prompt's exact format, plus the "upcoming events to pre-film for" flags.

Hard rule: every angle's key number must come from a page you actually fetched this run, with the working link included. If you cannot verify a story with a fetchable source, do not present it — mark the slot "no verifiable angle" instead. Never present a plausible-sounding story from memory as news.

Present the three angles with AskUserQuestion and let the user pick (or supply their own).

### Step 2 — Master script

With the chosen angle, apply the master-video prompt (`pipeline/prompts.md` §1): 6–8 minute direct-to-camera script on the series spine (mechanism → who profits → the story told instead → the ask), one mechanism, one core number, three [SHORT CANDIDATE] markers, next CTA from the rotation.

Then run the hostile pass (§1, second prompt) on your own draft before showing it: flag claims needing a source before broadcast, and fix any drift from evidenced anger into performance.

Save to `content/inequality-series/weekly/YYYY-MM-DD-<slug>/master-script.md` with a header noting lens, CTA, tension, and sources for every number.

### Step 3 — Derivatives (only if the user provides a filmed transcript)

If `$ARGUMENTS` contains or points to a transcript, generate from the *transcript* (not the script):

- `newsletter.md` — per prompts §2 (900–1,200 words, sourcing added, "what I'm watching" closer)
- `shorts.md` — three cut-sheets per prompts §3 (REVEAL / FIGHT / ASK, in/out quotes, cold-open hooks, captions, number cards, pinned comments)

If no transcript yet, stop after Step 2 and remind the user to re-run `/content-week <transcript file>` after filming.

### Step 4 — Update memory (every run, non-optional)

After Step 2 (and again after Step 3 if it ran), update `content/inequality-series/memory.md`: last completed week's topic/lens/CTA/core number, the next CTA in rotation, any new on-camera claims added to the standing claims register, and the covered-topics list. State the diff you made so the user can verify.

## Rules

- One reactive piece max per week; reactive scripts use the formats in `news-radar.md`, never improvised.
- Every number in any output must carry a source link in the saved file.
- Never two identical CTAs in consecutive weeks — check the previous week's folder.
- Composite characters only for HUMAN-lens content; no real identifiable people; no naming specific care operators without a checked source (see script 4's legal note).
