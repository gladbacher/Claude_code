---
description: Run the weekly UK energy bills content cycle - price/regulator radar, follow-the-money on networks and suppliers, master script, and derivatives from a transcript if provided.
---

# Energy Watch Command

Weekly pipeline for UK energy bills content. Thesis (same family as the inequality and water series): the gap between what energy costs to produce and what households pay is an extraction layer — network monopolies paying dividends on borrowed money, standing charges socialising failures, pricing structures that didn't fall when wholesale did. Same series voice: controlled anger, named mechanisms, primary-source numbers, never performative. Outputs live in `content/energy-series/weekly/YYYY-MM-DD/`.

## Workflow

### Step 1 — Radar

Search the last 7 days across:

**Price & regulator**
- Ofgem: price cap announcements and methodology, standing charge reviews, supplier enforcement, network price controls (RIIO)
- Wholesale vs retail divergence: day-ahead/futures gas and electricity prices vs the cap trajectory
- Quarterly price cap dates — flag the next one if within 3 weeks so the user can pre-film

**Company finance**
- Network operator results (National Grid, the DNOs, gas distribution): dividends, debt, returns vs Ofgem allowances — and who owns them (PE, sovereign wealth, overseas pension funds)
- Supplier results and margins; generator profits
- Supplier-failure legacy costs and where they sit on bills

**Policy & discourse**
- Government announcements: price cap tweaks, social tariff debate, green levies rows, zonal pricing debate
- "Cheapest electricity in Europe by 2030"-style claims and any ministerial "global gas prices" framing — translation material
- Fuel poverty data (NEA, End Fuel Poverty Coalition), prepayment meter stories, debt enforcement stories — HUMAN-lens material
- Martin Lewis / MSE coverage — what the consumer-advice space is angry about this week

Return THREE ranked angles: hook sentence, the tension, key number + source link, lens (NEWS / MECHANISM / RECEIPT / HUMAN), shelf life. Rank by bill proximity: a line item the viewer can find on their own bill beats any sector statistic.

Present the three with AskUserQuestion for the user to pick.

### Step 2 — Follow the money

Build the chain before scripting — every episode connects a line on the bill to a balance sheet:

> bill component (unit rate / standing charge / levy) → who collects it → that entity's dividends, debt interest, and allowed returns over a named period → who owns the entity → what the same component was 5 years ago

Anchor everything to the bill: the standing charge is the recurring star — a daily fee charged regardless of usage, carrying network costs and supplier-failure costs, which hits low-usage/poorer households hardest. Every figure with a primary source (Ofgem, Companies House, annual reports); no figure, no claim.

### Step 3 — Master script

6–8 minute direct-to-camera script on the series spine: the number on your bill → the mechanism (where that money actually goes) → the story told instead ("global gas prices", "investment in the grid", "it's the green levies") → the ask. One mechanism per episode, one core number repeated. Mark three [SHORT CANDIDATE] moments: one REVEAL, one TRANSLATION, one ASK.

CTA rotation: follow → **read your own bill** ("pause this, find your standing charge, comment what you pay per day" — the engagement engine for this niche) → write to your MP with one specific question → share to the person in your life who pays by prepayment meter.

Hostile pass before presenting: the strongest rebuttals from an Ofgem economist and a network company comms team (e.g. "returns are regulated", "standing charges reflect fixed costs"), conceded where true, dismantled where misleading — fixed in the script pre-emptively.

### Step 4 — Derivatives (only if `$ARGUMENTS` contains a transcript)

From the filmed transcript: newsletter (900–1,200 words, full sourcing, "what I'm watching" closer — next cap announcement, pending Ofgem decisions) and 3 shorts cut-sheets in house style (plain number cards, white on black).

## Reactive formats

Same two as the sibling series, max one per week:

- **Receipt** — a cap announcement, enforcement action, or results release confirms a previous episode: "In March I showed you where the standing charge goes. Today Ofgem {{action}}."
- **Translation** — minister or company explains a price rise; translate it into the money chain in 60 seconds.

## Rules

- Companies and ownership may be named from public record (Ofgem determinations, Companies House, annual reports) — link the primary source in the saved file, never a campaign paraphrase.
- Distinguish cleanly between wholesale costs (real, global) and the extraction layers on top (network returns, failure costs, structure of the cap) — conceding the real part is what makes the rest land.
- No energy-switching affiliate links or supplier recommendations in scripts — the series critiques the market; monetising switches inside it breaks trust.
- B-roll notes: bill close-ups (own bill, redacted), prepayment meters, pylons/substations, smart meter in-home displays showing standing charge accruing at midnight usage-zero. No faces, nothing staged.
