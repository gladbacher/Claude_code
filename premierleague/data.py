"""
Data loading for the Premier League model.

- `load_results_csv` reads the standard football-data.co.uk format (columns
  Date, HomeTeam, AwayTeam, FTHG, FTAG), so a real season is one download away:
      https://www.football-data.co.uk/mmz4281/2425/E0.csv
  (host must be allow-listed in restricted environments).
- `round_robin_fixtures` builds the 380-match double round-robin.
- `synthetic_season` draws a full season of scorelines from a Ratings object —
  used to demo/test the fitter without external data.
"""

from __future__ import annotations

import csv
from datetime import date, datetime

import numpy as np

from .dixoncoles import Ratings, match_lambdas, dc_tau
from .fit import Match

# football-data.co.uk names → our canonical names (only the differing ones).
_ALIASES = {
    "Nott'm Forest": "Nottingham Forest",
    "Man Utd": "Man United",
    "Spurs": "Tottenham",
}


def _canon(name: str) -> str:
    return _ALIASES.get(name.strip(), name.strip())


def load_results_csv(path: str, ref_day: str | None = None) -> list[Match]:
    """Parse a football-data.co.uk results CSV into Matches with time-decay ages."""
    ref = datetime.strptime(ref_day, "%Y-%m-%d").date() if ref_day else date.today()
    out: list[Match] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                hg, ag = int(row["FTHG"]), int(row["FTAG"])
            except (KeyError, ValueError):
                continue
            days_ago = 0.0
            raw_date = row.get("Date", "")
            for fmt in ("%d/%m/%Y", "%d/%m/%y"):
                try:
                    d = datetime.strptime(raw_date, fmt).date()
                    days_ago = max(0.0, (ref - d).days)
                    break
                except ValueError:
                    continue
            out.append(Match(_canon(row["HomeTeam"]), _canon(row["AwayTeam"]),
                             hg, ag, days_ago))
    return out


def round_robin_fixtures(teams: list[str]) -> list[tuple[str, str]]:
    """Every ordered pair once (home & away) — a full league season."""
    return [(h, a) for h in teams for a in teams if h != a]


def sample_scoreline(lam_h: float, lam_a: float, rho: float,
                     rng: np.random.Generator) -> tuple[int, int]:
    """Draw a scoreline with the stochastic Dixon-Coles low-score re-roll."""
    hg = int(rng.poisson(lam_h))
    ag = int(rng.poisson(lam_a))
    if dc_tau(hg, ag, lam_h, lam_a, rho) < rng.uniform():
        hg = int(rng.poisson(lam_h))
        ag = int(rng.poisson(lam_a))
    return hg, ag


def synthetic_season(ratings: Ratings, rng: np.random.Generator) -> list[Match]:
    """One simulated season of results drawn from `ratings` (for fit demos/tests)."""
    matches: list[Match] = []
    for home, away in round_robin_fixtures(ratings.teams):
        lh, la = match_lambdas(ratings, home, away)
        hg, ag = sample_scoreline(lh, la, ratings.rho, rng)
        matches.append(Match(home, away, hg, ag, 0.0))
    return matches
