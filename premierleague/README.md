# Premier League Dixon-Coles model

A data-fittable league model built on the same Dixon-Coles Poisson core as the
WC2026 project — but engineered the way a season model *should* be: team
strengths are **estimated by maximum likelihood from real match results**
rather than hand-tuned, with a proper per-match home advantage and optional
recency weighting.

## Why this is the "grown-up" version of the WC model

| | WC2026 model | Premier League model |
|---|---|---|
| Team ratings | hand-set per-game averages + FIFA-rank multiplier + confederation fudge | **fitted by MLE** from match results (`fit.py`) |
| Home advantage | only host nations (neutral venues) | **every home team**, one fitted `home_adv` |
| `rho` (low-score) | fixed −0.13 | **fitted** from the data |
| Recency | none (static averages) | **exponential time-decay** (`xi`) up-weights recent form |
| Value calc | flat-vig subtraction (conservative, approximate) | **proper overround stripping** (`strip_vig_1x2`) |

The league setting is exactly what Dixon & Coles (1997) designed their method
for, so the core transfers cleanly and the hacks the WC model needs (rank
multiplier, confederation discount) simply disappear — the data supplies the
strengths directly.

## Usage

```bash
# Season projection from bundled illustrative ratings
python -m premierleague --sims 10000

# Fit ratings from a real season, then project
#   (download E0.csv from football-data.co.uk first; allow-list the host)
python -m premierleague --csv E0.csv --xi 0.0019   # xi≈1yr half-life
```

```python
from premierleague import fit_ratings, simulate_season, projected_table
from premierleague.data import load_results_csv

matches  = load_results_csv("E0.csv", ref_day="2025-05-25")
ratings  = fit_ratings(matches, xi=0.0019)     # recency-weighted MLE
probs    = simulate_season(ratings, n_sims=10000)
for club, p in projected_table(probs):
    print(club, round(p["xpts"], 1), f"{p['title']*100:.1f}% title")
```

## Modules

| File | Purpose |
|------|---------|
| `dixoncoles.py` | Core: `Ratings`, λ from strengths, DC-corrected score grid, market vig-stripping |
| `fit.py` | Dixon-Coles **maximum-likelihood fit** with time decay + optional Bayesian priors |
| `priors.py` | Season priors: carry last season forward, seed **promoted clubs** with a weak prior |
| `market.py` | **Value layer** — model vs vig-stripped 1X2 odds, per-outcome edge + EV, ranked value bets |
| `data.py` | football-data.co.uk CSV loader · double round-robin · synthetic-season generator |
| `ratings.py` | Bundled illustrative 2024-25 strengths (replace with fitted values) |
| `season.py` | 380-match season Monte Carlo → title / top-4 / top-6 / relegation / xPts |
| `__main__.py` | CLI projected-table |

## Value bets & promoted clubs

```python
from premierleague import BUNDLED, value_bets, MatchOdds, season_priors, fit_ratings

# Which prices beat the vig-stripped fair line?
bets = value_bets(BUNDLED, [MatchOdds("Arsenal", "Tottenham", 1.70, 4.0, 4.6)], min_edge=0.03)
#  → [{'bet': 'Home (Arsenal)', 'model_p': .66, 'fair_p': .56, 'edge': +.105, 'ev': +.126}]

# New season: carry last year forward, seed the promoted clubs, shrink early form.
priors, strength = season_priors(last_season=fitted, current_teams=teams,
                                 promoted=["Leeds", "Burnley", "Sunderland"])
ratings = fit_ratings(new_matches, xi=0.0019, priors=priors, prior_strength=strength)
```

## Validation

`tests/` cover season-probability conservation (title→1, top-4→4, top-6→6,
relegation→3) and a **fitter round-trip**: on a synthetic season the MLE
recovers the true attack/defence strengths (Pearson corr ≈ 0.94–0.96) and
`rho`, confirming the estimation is sound.

## Roadmap to a production PL model

- [x] **Promoted-team priors / Bayesian shrinkage** — `priors.py` + `fit_ratings(priors=…)`.
- [x] **Market value layer** — `market.py`: model vs vig-stripped 1X2, edge + EV.
- [ ] **Real data ingestion** — point `load_results_csv` at football-data.co.uk
      (or an API); refit nightly, blending the last ~2 seasons with time decay.
- [ ] **More markets** — extend the value layer to O-U / AH / BTTS, and add outright
      title/top-4/relegation value off the season sim.
- [ ] **In-season updates** — refit after each round; track live title/top-4/
      relegation odds and calibration (Brier score, log-loss).
- [ ] **Extensions** — separate home/away attack, manager-change bumps,
      player-availability (xG with/without key players), and a scorer model.
