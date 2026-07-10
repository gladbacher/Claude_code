# Lesser-Model Pack — Running the Weekly Loop on a Smaller Model

How to run the inequality pipeline on a cheap/fast model (Claude Haiku in Claude Code is the primary target; §5 covers plain chat with any model). Written for a model that follows instructions literally and infers nothing.

## 1. Why this exists

The big-model version of this pipeline tolerates vague instructions because the model fills gaps. A smaller model doesn't. Three compensations, all already built in:

1. **Explicit state** — `content/inequality-series/memory.md` holds last week's topic/lens/CTA and the standing claims. The command reads it at start and writes it at end. Never rely on the model remembering or inferring.
2. **Defensive radar** — smaller models are more likely to present plausible-sounding "news" that doesn't exist. The radar rules in §3 make hallucination detectable: no link, no story.
3. **One step per message** — don't ask for radar + script + shorts in one go. Each stage completes and gets checked before the next starts.

## 2. Setup in Claude Code (once per session)

```
/model haiku
```

Then work as normal. Everything below assumes Haiku is active. If a step's output is repeatedly poor (radar especially), escalate just that step: `/model sonnet`, rerun the step, drop back. **Escalation order when quality slips: radar first, hostile pass second, script third.** The derivatives (newsletter/shorts from transcript) almost never need escalation — transformation is a small-model strength; judgement under uncertainty is not.

## 3. The Monday run

Type: `/content-week`

The command handles the sequence. Your checks, in order — do not skip on a small model:

**Radar checks (before picking an angle):**
- [ ] Every angle has a working source link. Open each one. **A story without a link you can open does not exist** — reject it and say "angle 2's source doesn't check out, replace it."
- [ ] The number in each angle actually appears in the linked source (skim for it).
- [ ] The lens differs from `memory.md` last-lens (unless NEWS or the active direction memo overrides).
- If all three angles are weak or unverifiable: "Skip the radar. Give me a MECHANISM episode on {{pick from the idea bank, prompts.md §4}} — no news claims, mechanism and arithmetic only." This is the safe harbour: mechanism episodes need no fresh facts, so a small model can't hallucinate news into them.

**Script checks (before locking):**
- [ ] One mechanism, one core number, number repeated, spine present (mechanism → who profits → the story told instead → the ask).
- [ ] Three `[SHORT CANDIDATE]` markers exist.
- [ ] CTA matches `memory.md` next-CTA.
- [ ] Hostile pass ran. On Haiku, run it as its own message and be explicit: *"Now attack this script as an FT-reading sceptic. List the 3 weakest claims and any number lacking a source. Rewrite only those passages."*
- [ ] Read it aloud once. If any sentence sounds like a press release, have it rewritten: *"Rewrite paragraph N in spoken English."*

**Close the run:** *"Update memory.md: topic, lens, CTA, core number, and add any on-camera claims to the standing claims register."* Verify the file changed.

## 4. The Thursday run

Type: `/content-week <path-to-transcript>`

Checks:
- [ ] Newsletter quotes phrases you actually said (spot-check 2–3 against the transcript).
- [ ] Every number in the newsletter has a source link — on a small model, explicitly ask: *"List every number in this newsletter with its source link. Cut any number that has neither."*
- [ ] Shorts do three different jobs (REVEAL / FIGHT / ASK), and each in/out quote really is in the transcript.

## 5. Portable prompt pack (no Claude Code — any chat model)

If working in a plain chat window, paste the **context block** below first, then the stage prompt. Keep both in a note on your phone/desktop.

**Context block (paste first, every conversation):**

> You are the writer for a weekly UK wealth-inequality video series. Thesis: concentrated wealth extracts assets from the middle class — pensions (DB→DC shift + ~1.5%/yr fees ≈ a third of a pot over 40 years), home equity (care costs + private equity care sector), savings (a decade of near-zero rates as policy), small business, inheritance (frozen thresholds). Foundations: Gary Stevenson (asset price inflation from concentrated wealth; doesn't self-correct), Gabriel Zucman (2% minimum tax above £100m — ~£15bn/yr from ~1,000 UK families; ownership transparency; 1909 precedent). Voice: one credible person joining the dots — controlled evidenced anger, named mechanisms, real numbers, spoken English, never softened, never performative. Series spine every episode: the mechanism → who profits → the story told instead → the ask. Hard rule: never state a fact or number without a source you can link; if you are not certain something is real, say "UNVERIFIED" next to it instead of asserting it.
> My current state: last topic {{...}}, last lens {{...}}, next CTA {{...}}.

Then use the stage prompts from `prompts.md` (§1 master script, §2 newsletter, §3 shorts, §4 idea bank, §5 rebuttal) — they are already copy-paste-ready. For the radar in a plain chat, only use a model with real web browsing, and apply the same rule: open every link before trusting the angle. If the model has no browsing, do not ask it for news at all — run mechanism/rebuttal weeks and take news angles from your own feeds.

## 6. What NOT to delegate to a small model

- **Trust decisions** — whether a source is credible, whether a claim is safe to say on camera. The checklists above keep those decisions yours.
- **The final read** — nothing is filmed that you haven't read aloud once.
- **Memory** — never ask "what did we cover last week?" without `memory.md` in front of it.

## 7. Weekly cost/quality dial

| Situation | Setting |
|-----------|---------|
| Normal week | Haiku throughout + checklists |
| Radar keeps missing/hallucinating | Sonnet for radar step only |
| High-stakes episode (naming companies, legal-adjacent) | Sonnet/Opus for hostile pass; everything else Haiku |
| Documentary-week-style event content | Full-size model for the master script; it's the flagship |
