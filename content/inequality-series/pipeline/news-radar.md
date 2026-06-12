# News Radar

The replacement for trawling the web. Run the radar prompt every Monday (or just run `/content-week`, which includes it). It returns three ranked angles; you pick one in two minutes.

## What the radar watches

Standing source list — the prompt instructs the model to search these areas, you never visit them yourself:

**Data drops & reports**
- ONS: house price index, wealth & assets survey, pension statistics
- FCA / TPR publications on pension fees and DC outcomes
- IFS, Resolution Foundation, Positive Money, Tax Justice UK reports
- Bank of England rate decisions and QE/QT commentary

**Sector signals**
- Private equity activity in care homes, dentistry, childcare, vets, GP practices (acquisitions, administrations, CMA references)
- Care home operator results, CQC enforcement, sale-and-leaseback deals
- Housebuilder and land-banking results announcements

**Political surface**
- Budget/fiscal-event measures touching IHT, CGT, pension allowances, business rates
- Any minister or shadow minister using "capital flight", "fiscal responsibility", "intergenerational fairness" framing — these are content on a plate
- Wealth tax debate: Zucman proposal coverage, G20/EU minimum-tax progress, Stevenson appearances and the responses to him

**Discourse**
- What's travelling on TikTok/X/Reddit (r/UKPersonalFinance, r/HousingUK) about pensions, care costs, rent, inheritance — especially *wrong* takes worth correcting and *angry* threads showing where the audience already is

## The radar prompt (Monday)

> You are the researcher for a weekly UK wealth-inequality video series (thesis: concentrated wealth extracts assets from the middle class — pensions, home equity, savings, inheritance — per Stevenson/Zucman). Search the last 7 days across: UK economic data releases, pension/care/housing sector news, private equity activity in care-adjacent sectors, fiscal policy announcements, and social discourse on these topics.
>
> Return the THREE strongest video angles. For each: (1) the hook in one spoken sentence, (2) the tension — the contradiction at its core, phrased to drop straight into my master-script prompt, (3) the key number with its source and a link, (4) which series lens it is (NEWS / MECHANISM / REBUTTAL / HUMAN), (5) shelf life — must it run this week or does it keep?
>
> Rank by: emotional proximity to a 45–65 year old with a house and a pension, beats novelty, beats scale. Reject anything that requires the viewer to care about an institution rather than themselves. Last week's video was about {{last topic}} using the {{last lens}} lens, so weight the other lenses. Flag separately, in one line each, anything that's *about to* happen (scheduled data release, budget date, earnings announcement) that I should pre-film for.

## Reactive formats (when something breaks mid-week)

The one exception to "shorts come from the master video". Two formats, both filmable in under 30 minutes:

**The 60-second receipt** — news confirms something the series already said. Structure: "Three weeks ago I told you {{claim}}. Today {{news}}." → 20 seconds on what the story actually means → "This is the machine working in public. Full video on this mechanism is pinned." Links new viewers back into the catalogue; the back-catalogue is the asset.

**The translation** — a politician/CEO says something in the standard framing. Structure: play or quote the clip → "Let me translate." → restate it in extraction terms → one number → out. No CTA needed; the translation *is* the hook.

Reactive prompt:

> {{paste the news item / quote / clip transcript}}
>
> You are the series voice. Which reactive format fits — receipt or translation? Write the 60-second script. If it's a receipt, name which past video it confirms. One number maximum. The emotional target: "they're not even hiding it."

## Discipline

- Maximum one reactive piece per week. The weekly master video is the product; reactions are distribution.
- Never react to something you can't attach a number or a named mechanism to — outrage without receipts breaks the tone rules.
- If the radar produces nothing strong, that's fine: run a MECHANISM week from the idea bank. The backlog is the floor under the whole pipeline.
