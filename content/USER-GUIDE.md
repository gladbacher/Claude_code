# User Guide — Running the Content Pipeline

The hands-on manual: what to type, when, and what you get back. Companion document: `WORKFLOW-PLAN.md` (the schedule and strategy). You never need to write a prompt from scratch — the commands carry them.

## Setup (once)

1. Open Claude Code in this repository (CLI, desktop app, or claude.ai/code) on a branch that contains the commands (currently `claude/amazing-carson-66coei`; `main` after the PR merges).
2. That's it. The four commands appear in the `/` menu:
   - `/content-week` — inequality series
   - `/water-watch` — water quality & sewage
   - `/energy-watch` — energy bills
   - `/transfer-week` — football transfer rumours
3. Optional, before promoting the site: wire the email forms per `site/README.md`.

## The Monday run (per live series)

Type the command with no arguments:

```
/content-week
```

What happens:
1. Claude searches the last 7 days across that series' source list (regulators, company filings, campaign groups, social discourse — you never trawl anything).
2. You get **three ranked angles**, each with: a hook sentence, the tension, the key number with a source link, which lens it is, and its shelf life. Upcoming events worth pre-filming for are flagged separately.
3. Pick one (a picker appears; you can also type your own angle).
4. Claude drafts the master script — 6–8 minutes, direct to camera, on the series spine — then attacks its own draft (the "hostile pass") and fixes the weak claims before showing you.
5. The script saves to `content/<series>/weekly/YYYY-MM-DD-<slug>/master-script.md`, with lens, CTA, tension, and a source for every number in the header.

Your job Monday: read three angles, pick one. ~10 minutes.
Your job Tuesday: read the script aloud once, edit anything that doesn't sound like you, lock it.

**Transfers differs slightly:** `/transfer-week` grades 5 rumours on the house rubric and updates the accuracy ledger (`content/transfer-series/ledger.md`) *before* grading — outcomes of old calls are checked automatically. You pick which rumours and which 60-second teaching concept.

## Film (Wednesday)

Direct to camera, single light, one take ethos. The script marks three `[SHORT CANDIDATE]` moments — glance at them before filming so you deliver those beats cleanly (they become your shorts). Get a transcript of what you actually said (any transcription tool; accuracy matters more than formatting) and save it as a text file.

## The Thursday run (derivatives)

Run the same command again, pointing at your transcript:

```
/content-week transcripts/2026-07-17.txt
```

You get, in the same weekly folder:
- **`newsletter.md`** — 900–1,200 words in your voice (built from the transcript, not the script, so it sounds like what you actually said), with full sourcing added and a "what I'm watching next week" closer. Paste into your newsletter provider.
- **`shorts.md`** — three cut-sheets, each with: in/out points quoted from your own words, the 2-second cold open (on-screen text + spoken line, including a re-record line if the segment doesn't open on its hook), caption, number card in house style, and the comment to pin. The three do different jobs — one REVEAL, one FIGHT, one ASK — drip them Sat/Mon/Wed.

## Reactive pieces (only when news breaks mid-week)

Two formats, both in each series' command / `pipeline/news-radar.md`, both filmable in under 30 minutes:
- **Receipt** — news confirms something you already said: "Three weeks ago I told you X. Today it happened."
- **Translation** — an official statement, translated into the money chain in 60 seconds.

Rules: maximum one per series per week, and never react to anything you can't attach a number or named mechanism to. Ask Claude: *"Reactive piece: [paste the news item]"* — it picks the format and writes the script.

## Where everything lives

```
content/
├── WORKFLOW-PLAN.md            ← the schedule and strategy
├── USER-GUIDE.md               ← this file
├── inequality-series/
│   ├── newsletter-*.md         ← launch newsletter
│   ├── scripts/01–05           ← launch video scripts
│   ├── pipeline/               ← prompts, radar, weekly system
│   ├── direction-2026-07.md    ← current direction memo (documentary week, Zucman)
│   └── weekly/                 ← everything the commands produce
├── water-series/weekly/
├── energy-series/weekly/
├── transfer-series/
│   ├── ledger.md               ← the public accuracy ledger
│   └── weekly/
site/                           ← landing pages (deploy per site/README.md)
```

## Troubleshooting

- **A command isn't in the `/` menu** — you're on a branch without it, or in the wrong directory. Check you're in this repo and on the right branch.
- **The radar returns weak angles** — say so and run a MECHANISM week instead: "Nothing strong this week — give me a mechanism episode from the idea bank." The backlog in `pipeline/prompts.md` §4 is the floor under every dry week.
- **A number in a draft has no source** — reject it. The commands are instructed never to include unsourced figures; if one slips through, reply "source this or cut it." Never film an unsourced number.
- **You want to change the standing behaviour of a series** — edit its command file in `commands/` (they're plain markdown), or for a temporary shift write a dated direction memo like `direction-2026-07.md` and tell the Monday run to read it.
- **Same CTA two weeks running** — the commands check the previous weekly folder, but if the folder wasn't saved, tell it what last week's CTA was.

## The five rules that protect the brand

1. Every number carries a source in the saved file — no exceptions.
2. Outrage without receipts never ships.
3. Derive from the transcript, not the script.
4. Corrections go on camera in the next episode.
5. When in doubt, ship the mechanism episode — the backlog means there is never a dry week.
