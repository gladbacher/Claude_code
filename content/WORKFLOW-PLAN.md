# Workflow Plan — The Content Operation

How the whole machine runs: four series, one presenter, roughly one desk-hour per series per week. Companion document: `USER-GUIDE.md` (the how-to). This is the *what and when*.

## 1. The operating model

Every series runs the same loop:

```
MONDAY          TUESDAY         WEDNESDAY      THURSDAY            FRI–WED
radar (10 min) → script (20 min) → film (1–2 h) → derive (30 min) → publish + drip
   pick angle      edit pass        one take       from transcript    video, newsletter,
   (2 min)         hostile pass                                       3 shorts
```

One command drives each series. Run it bare on Monday (radar + script), run it again with your transcript after filming (newsletter + shorts cut-sheets). Everything saves to dated folders with sources attached to every number.

| Series | Command | Master output day | Distinct asset |
|--------|---------|-------------------|----------------|
| Inequality | `/content-week` | Friday | The thesis; the flagship voice |
| Water Watch | `/water-watch` | Friday | "Check your own river" engagement engine |
| Energy Watch | `/energy-watch` | Friday | "Read your own bill" engagement engine |
| The Rumour, Graded | `/transfer-week` | Monday (pre-gossip-column) | Public accuracy ledger |

## 2. Phasing — do not launch all four at once

Four master videos a week is a full-time production job. Phase in:

- **Phase 1 (now — ~4 weeks): Inequality only.** Prove the loop end to end: radar → film → derive → publish → shorts drip. Fix friction while the stakes are one series. Documentary week (see §5) lands in this phase — treat it as the launch event.
- **Phase 2 (+4–8 weeks): add ONE adjacent series** — energy or water (shared voice, shared villains, research compounds). Pick whichever radar produced the stronger Mondays during phase 1 (run both radars weekly even before launching; it costs minutes).
- **Phase 3 (when phase 2 is routine): Transfers.** Different audience, different tone, Monday cadence — effectively a second brand. Only start when the "Follow the Money" side runs itself. Note the transfer window calendar: launching 2–3 weeks before a window opens gives the ledger time to seed.
- **Steady state ceiling: three weekly masters.** If all four must run, drop one Follow-the-Money series to fortnightly and say so on the page — a stated cadence kept beats a weekly cadence missed.

## 3. The weekly calendar (steady state, phases 1–2)

| Day | Block | What happens |
|-----|-------|--------------|
| Mon AM | 30 min desk | Run each live series' command; pick angles; note pre-film flags (cap announcements, data drops) |
| Tue | 30–45 min desk | Review scripts; run/inspect the hostile pass; lock scripts |
| Wed | Filming block | All masters filmed back-to-back (same light, same setup — batch it). Reactive shorts also filmed here if the week has one |
| Thu | 45 min desk | Feed transcripts back to commands; review newsletter + cut-sheets; schedule posts |
| Fri | — | Master video + newsletter publish |
| Sat / Mon / Wed | — | Shorts drip (auto-scheduled Thursday) |

**Reactive pieces** (receipt / translation formats) are the only unscheduled work: max one per series per week, filmable in under 30 minutes, only when a radar-worthy story breaks mid-week and carries a number.

## 4. Cross-series rules

- **One voice for the Follow-the-Money three** (inequality, water, energy): same person, same tone rules, same number-card style. Cross-reference freely ("the same pension funds that own your water company…") — the compounding audience is the point.
- **Transfers stays firewalled**: different tone (dry, amused), no politics, no cross-promotion in either direction beyond the shared "receipts" ethos.
- **CTA rotation is per-series**, tracked via each series' previous weekly folder. Never two identical CTAs consecutively within a series.
- **The ledgers are sacred**: transfer accuracy ledger updated before each new grading; corrections in any series go on camera in the next episode. This is the moat — never skip it under time pressure.

## 5. Event weeks (override the calendar)

Some weeks the calendar bends to an external event. Current live example: **Stevenson's Channel 4 documentary (8 July, YouTube 12 July)** — see `inequality-series/direction-2026-07.md` for the full play (reactive short before broadcast, companion master timed to the YouTube release). The general pattern for any event week:

1. Radar flags the event ≥1 week out (commands are built to flag scheduled drops — cap announcements, EDM data, budget days, deadline day).
2. Pre-film the evergreen part; hold a 60-second reactive slot for the day itself.
3. Companion, never competitor: ride the search spike toward this operation's specific angle.

## 6. Newsletter and site

- Landing pages live in `site/` (hub + one per series). Deploy per `site/README.md`; wire the email forms to the chosen provider before promoting any page.
- The newsletter is derived from the transcript, never written fresh — it is the video in forwardable form plus sourcing. One send per series per week; if running multiple series, a combined weekly digest from the hub page is the growth lever.

## 7. Cadence of maintenance

| Rhythm | Task |
|--------|------|
| Weekly | CTA rotation check (automatic in commands); transfer ledger outcomes pass |
| Monthly | Refill the inequality idea bank (`pipeline/prompts.md` §4); prune recycled-rumour list; review shorts performance → adjust which [SHORT CANDIDATE] types get cut |
| Quarterly / on events | Direction memo review (e.g. `direction-2026-07.md` review date after the documentary run); lens re-weighting decisions; phase gate: launch next series or not |

## 8. Quality gates (non-negotiable, all series)

1. No number without a primary source linked in the saved file.
2. No reaction without a number or named mechanism attached.
3. Hostile pass on every master script before filming.
4. Concede what's true before dismantling what isn't (energy: wholesale costs; water: legal overflows exist; transfers: some rumours are real).
5. Corrections on camera, next episode.
