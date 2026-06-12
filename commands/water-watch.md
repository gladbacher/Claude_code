---
description: Run the weekly UK water quality and sewage content cycle - spill/data radar, financial follow-the-money, master script, and derivatives from a transcript if provided.
---

# Water Watch Command

Weekly pipeline for UK water quality / sewage spill content. Thesis (shares DNA with the inequality series in `content/inequality-series/`): privatised water is an extraction machine — bills service shareholder dividends and debt loaded onto the companies, while sewage goes into rivers because infrastructure investment is the variable that gets cut. The series voice is the same person as the inequality series: controlled anger, named mechanisms, real numbers, never performative. Outputs live in `content/water-series/weekly/YYYY-MM-DD/`.

## Workflow

### Step 1 — Radar

Search the last 7 days across:

**Data & enforcement**
- Environment Agency: storm overflow / Event Duration Monitoring data, pollution incident reports, prosecutions and fines
- Ofwat: enforcement actions, dividend/performance decisions, price review news
- Drinking Water Inspectorate notices
- Annual EDM data drop (spring) and bathing water classifications — flag if imminent so the user can pre-film

**Company finance**
- Water company results: dividends paid, debt levels, interest costs, executive pay, totex vs actual infrastructure spend
- Thames Water (and any other distressed operator) restructuring news — the live case study
- Credit rating actions on water companies

**Campaign & discourse**
- Surfers Against Sewage alerts and reports, Top of the Poops rankings, River Action, Feargal Sharkey
- Local news: named beaches/rivers closed, swimmer illness stories, angling club complaints — these are the HUMAN-lens material
- Ministerial statements using "record investment" / "tough new powers" framing — translation-format material

Return THREE ranked angles in the same format as the inequality radar: hook sentence, the tension (the contradiction), key number + source link, lens (NEWS / MECHANISM / RECEIPT / LOCAL), shelf life. Rank by emotional proximity: a named river or beach beats a national statistic; a bill increase beats a regulatory abstraction.

Present the three with AskUserQuestion for the user to pick.

### Step 2 — Follow the money

For the chosen angle, build the financial chain before scripting — every episode must connect the spill to the balance sheet:

> spill/failure → which company → dividends + debt interest paid since privatisation or over a recent named period → infrastructure spend over the same period → who owns the company (PE/sovereign/pension funds) → what customers' bills are rising by

Every figure with a source link. If a figure can't be sourced, it doesn't go in the script.

### Step 3 — Master script

6–8 minute direct-to-camera script on the series spine: the incident or number → the mechanism (how the money actually flows) → the story being told instead ("record investment", "blame the rain", "blame wet wipes") → the ask. One mechanism per episode. One core number repeated. Mark three [SHORT CANDIDATE] moments: one REVEAL, one TRANSLATION (the official line, translated), one LOCAL/ASK.

CTA rotation: follow → check your own river/beach (link Top of the Poops / SAS map — "comment what you find") → write to your MP with one specific question → share to someone who swims/fishes/pays the bill. The "check your own river" CTA is the engagement engine for this niche — it makes every comment section local.

Run the hostile pass before presenting: a water company comms officer's strongest rebuttals, fixed in the script pre-emptively.

### Step 4 — Derivatives (only if `$ARGUMENTS` contains a transcript)

From the filmed transcript: newsletter (900–1,200 words, full sourcing, "what I'm watching" closer — upcoming data drops, Ofwat decisions) and 3 shorts cut-sheets in the house style (plain number cards, white on black).

## Reactive formats

Same two as the inequality series, max one per week:

- **Receipt** — a fine, prosecution, or data drop confirms a previous episode: "Last month I showed you {{company}}'s numbers. Today the Environment Agency {{action}}."
- **Translation** — minister or company statement, translated into the money chain in 60 seconds.

## Rules

- Companies may be named — enforcement actions, financial filings, and EDM data are public record — but every named claim needs a primary source (EA, Ofwat, Companies House, company annual report) linked in the saved file, not a campaign group's paraphrase of it.
- Distinguish clearly between legal storm overflow discharges and illegal dry spills/permit breaches; conflating them is the rebuttal that kills credibility.
- Health claims stay sourced and conservative (UKHSA, peer-reviewed) — "people got sick at X" only with a citation.
- B-roll notes per episode: outfall pipes, named river signage, bill close-ups, company HQ exteriors. No faces, nothing staged.
