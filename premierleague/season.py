"""
Season Monte Carlo: play the full 380-match double round-robin many times and
aggregate each club's title / top-4 / top-6 / relegation odds and expected
points — the league analogue of the WC tournament simulator.
"""

from __future__ import annotations

import numpy as np

from .dixoncoles import Ratings, match_lambdas
from .data import round_robin_fixtures, sample_scoreline

RELEGATION_SPOTS = 3
CHAMPIONS_LEAGUE = 4   # top-4 → UCL
EUROPE = 6             # top-6 → European places (rough)


def simulate_season(ratings: Ratings, n_sims: int = 10_000,
                    rng: np.random.Generator | None = None) -> dict[str, dict]:
    """
    Returns {team: {title, top4, top6, relegation, xpts, avg_pos}} probabilities.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    teams = ratings.teams
    n = len(teams)
    fixtures = round_robin_fixtures(teams)
    lambdas = {(h, a): match_lambdas(ratings, h, a) for h, a in fixtures}

    title = {t: 0 for t in teams}
    top4 = {t: 0 for t in teams}
    top6 = {t: 0 for t in teams}
    releg = {t: 0 for t in teams}
    pts_tot = {t: 0.0 for t in teams}
    pos_tot = {t: 0.0 for t in teams}

    for _ in range(n_sims):
        pts = {t: 0 for t in teams}
        gd = {t: 0 for t in teams}
        gf = {t: 0 for t in teams}
        for home, away in fixtures:
            lh, la = lambdas[(home, away)]
            hg, ag = sample_scoreline(lh, la, ratings.rho, rng)
            if hg > ag:
                pts[home] += 3
            elif hg == ag:
                pts[home] += 1
                pts[away] += 1
            else:
                pts[away] += 3
            gd[home] += hg - ag
            gd[away] += ag - hg
            gf[home] += hg
            gf[away] += ag

        order = sorted(teams, key=lambda t: (pts[t], gd[t], gf[t], rng.random()),
                       reverse=True)
        for rank, t in enumerate(order):
            pos_tot[t] += rank + 1
            if rank == 0:
                title[t] += 1
            if rank < CHAMPIONS_LEAGUE:
                top4[t] += 1
            if rank < EUROPE:
                top6[t] += 1
            if rank >= n - RELEGATION_SPOTS:
                releg[t] += 1
            pts_tot[t] += pts[t]

    return {
        t: {
            "title": title[t] / n_sims,
            "top4": top4[t] / n_sims,
            "top6": top6[t] / n_sims,
            "relegation": releg[t] / n_sims,
            "xpts": pts_tot[t] / n_sims,
            "avg_pos": pos_tot[t] / n_sims,
        }
        for t in teams
    }


def projected_table(season_probs: dict[str, dict]) -> list[tuple[str, dict]]:
    """Clubs ordered by expected points (projected final table)."""
    return sorted(season_probs.items(), key=lambda kv: kv[1]["xpts"], reverse=True)
