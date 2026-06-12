---
description: Run the weekly football transfer content cycle - rumour radar, grade the week's rumours, master script, accuracy ledger update, and derivatives from a transcript if provided.
---

# Transfer Week Command

Weekly pipeline for the "The Rumour, Graded" series. The product is NOT rumour aggregation — it is teaching the audience to *read* rumours: source quality, agent fingerprints, financial plausibility. The moat is a public accuracy ledger. Outputs live in `content/transfer-series/weekly/YYYY-MM-DD/`.

## Voice

Direct to camera, dry, amused, forensic. Never breathless. Credibility from the grading record, not from claiming inside sources — explicitly the opposite of an ITK account: "I don't know anything. I just read carefully."

## Workflow

### Step 1 — Rumour radar

Search the last 7 days for the highest-traction transfer rumours (Premier League focus). Sources to weight, in tier order:

- **Tier 1**: club/player official statements, Romano "here we go", David Ornstein/The Athletic, club-dedicated beat reporters
- **Tier 2**: Sky Sports News, BBC, national broadsheets
- **Tier 3**: national tabloids, aggregated "gossip column" items
- **Tier 4**: foreign outlets known for agent placement, in-the-know accounts, anything sourced to "reports"

Also pull each rumoured club's financial context where findable: PSR/Squad Cost Rule headroom commentary, recent academy sales, wage structure stories, amortisation patterns.

Return the 5 rumours with the best mix of traction and gradeability.

### Step 2 — Grade

Score each rumour on the house rubric (0–10 overall, shown as a card):

| Axis | What to check |
|------|---------------|
| **Source tier** | Best outlet carrying it, per the tier list. Quote who actually originated it, not who repeated it |
| **Agent fingerprints** | Contract expiring/renewal due? Story appears just before talks? Single-outlet exclusive with no follow-up? "Player flattered by interest"? |
| **Financial plausibility** | Fee vs club's realistic headroom, wage fit vs current structure, does the selling club need to sell before June 30 (accounting deadline)? |
| **Squad logic** | Does the buying club actually need the position? Manager quotes? |
| **Pattern match** | Does this match a known recycler pattern (same rumour every window)? |

Verdict line for each, in voice: e.g. "This is a contract negotiation wearing a transfer rumour as a coat. 3/10."

### Step 3 — Accuracy ledger

Maintain `content/transfer-series/ledger.md`: every graded rumour, date, grade, one-line reasoning, and an OUTCOME column (CONFIRMED / DIED / RECYCLED / OPEN). Each week, before grading new rumours, search for outcomes on OPEN entries and update them. Compute and display the running hit rate. Ledger updates are non-optional — the ledger IS the brand.

Any newly-resolved entry where the grade was right is a **receipt short** candidate: "Three weeks ago I gave this 2/10. Here's it dying."

### Step 4 — Master script

6–8 minute direct-to-camera script: cold open on the week's most absurd rumour, then grade the 5, ledger segment ("the scoreboard"), and close with one teaching point — a single concept (amortisation, pure-profit academy sales, sell-on clauses, agent windows) explained in 60 seconds so every episode leaves the viewer permanently smarter. Mark three [SHORT CANDIDATE] moments: one GRADE (funniest verdict), one RECEIPT (ledger update), one TEACH (the concept).

Present angles/choices with AskUserQuestion where the user should pick (e.g. which 5 rumours, which teaching concept).

### Step 5 — Derivatives (only if `$ARGUMENTS` contains a transcript)

From the filmed transcript: 3 shorts cut-sheets (in/out quotes, cold-open hook, caption ≤3 hashtags, grade card in house style — plain white on black) and a newsletter version with the full ledger table embedded and sources linked for every claim.

## Rules

- Never present a rumour as news — always as an object being examined.
- Every grade must cite who originated the story. No grading screenshots of unnamed aggregators.
- Window cadence: during transfer windows this can run twice weekly and reactive receipt shorts any day; between windows, switch the teaching segment to lead (finance explainers) and grade "contract saga" stories instead.
- Betting/gambling references: none. Keeps the content advertiser-safe and under-18-audience-safe.
