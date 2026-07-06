"""
Dixon-Coles Poisson core for league football.

This is the principled engine a betting model should be built on: team attack
and defence strengths on the log scale, a global home-advantage term, and the
Dixon-Coles low-score correlation correction. The WC2026 model approximates
these strengths with hand-tuned per-game averages + a FIFA-rank multiplier;
here they are proper parameters that can be FITTED from match results
(see fit.py), which is the natural fit for a 380-match league season.

    log λ_home = mu + att[home] - def[away] + home_adv
    log λ_away = mu + att[away] - def[home]

where a higher att means "scores more" and a higher def means "concedes fewer"
(defensive strength). Attack and defence are identifiable up to a constant, so
fit.py pins them with sum-zero constraints.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class Ratings:
    """A fitted (or hand-set) rating set for a league."""
    mu: float                       # baseline log goal rate
    home_adv: float                 # home advantage (log scale)
    rho: float                      # Dixon-Coles low-score correlation
    att: dict[str, float] = field(default_factory=dict)   # attack strength
    dfn: dict[str, float] = field(default_factory=dict)   # defensive strength

    @property
    def teams(self) -> list[str]:
        return sorted(self.att)


def dc_tau(x: int, y: int, lam: float, mu: float, rho: float) -> float:
    """Dixon-Coles correction factor for the four low-score cells."""
    if x == 0 and y == 0:
        return 1.0 - lam * mu * rho
    if x == 0 and y == 1:
        return 1.0 + lam * rho
    if x == 1 and y == 0:
        return 1.0 + mu * rho
    if x == 1 and y == 1:
        return 1.0 - rho
    return 1.0


def match_lambdas(r: Ratings, home: str, away: str) -> tuple[float, float]:
    """Expected goals for a fixture given ratings."""
    lam_h = math.exp(r.mu + r.att[home] - r.dfn[away] + r.home_adv)
    lam_a = math.exp(r.mu + r.att[away] - r.dfn[home])
    return lam_h, lam_a


def score_matrix(lam_h: float, lam_a: float, rho: float,
                 max_goals: int = 10) -> list[list[float]]:
    """Normalised P(home=h, away=a) grid with Dixon-Coles correction."""
    # Poisson pmf without scipy (fast, dependency-light).
    def pois(k: int, lam: float) -> float:
        return math.exp(-lam) * lam ** k / math.factorial(k)

    ph = [pois(h, lam_h) for h in range(max_goals + 1)]
    pa = [pois(a, lam_a) for a in range(max_goals + 1)]
    grid = [[ph[h] * pa[a] * dc_tau(h, a, lam_h, lam_a, rho)
             for a in range(max_goals + 1)] for h in range(max_goals + 1)]
    total = sum(sum(row) for row in grid)
    if total > 0:
        grid = [[v / total for v in row] for row in grid]
    return grid


def outcome_probs(lam_h: float, lam_a: float, rho: float,
                  max_goals: int = 10) -> dict:
    """1X2, over/under 2.5, and BTTS probabilities from the score grid."""
    grid = score_matrix(lam_h, lam_a, rho, max_goals)
    home = draw = away = 0.0
    over25 = btts = 0.0
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            p = grid[h][a]
            if h > a:
                home += p
            elif h == a:
                draw += p
            else:
                away += p
            if h + a > 2:
                over25 += p
            if h > 0 and a > 0:
                btts += p
    return {
        "home": home, "draw": draw, "away": away,
        "over25": over25, "under25": 1.0 - over25, "btts": btts,
        "lambda_home": lam_h, "lambda_away": lam_a,
    }


# ── Market helpers (the value calc the WC model should adopt) ─────────────────

def strip_vig_1x2(home_odds: float, draw_odds: float, away_odds: float) -> dict:
    """
    Proper vig removal: normalise the three implied probabilities so they sum
    to 1. This is the correct fair-price baseline for value detection — unlike
    subtracting a flat vig from a single line (which the WC find_value does).
    """
    imp = [1.0 / home_odds, 1.0 / draw_odds, 1.0 / away_odds]
    total = sum(imp)
    fair = [x / total for x in imp]
    return {"home": fair[0], "draw": fair[1], "away": fair[2], "overround": total - 1.0}


def value_edge(model_p: float, fair_p: float) -> float:
    """Edge vs the vig-stripped fair probability (positive = model sees value)."""
    return model_p - fair_p
