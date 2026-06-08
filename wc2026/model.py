"""
WC2026 match simulation engine.

Uses independent Poisson draws with Dixon-Coles low-score correction.
Expected goals are derived from attack/defence ratings weighted by
opposition strength (SoT-based ranking).
"""

from __future__ import annotations

import logging
import random
from typing import TypedDict

import numpy as np
from scipy.stats import poisson

import math

from .data import TEAMS, PLAYERS

logger = logging.getLogger(__name__)

# ── Dixon-Coles rho ──────────────────────────────────────────────────────────
# Estimated from historical WC data. Corrects for correlation between
# low-score outcomes (0-0, 1-0, 0-1, 1-1).
RHO: float = -0.13

# ── Simulation defaults ───────────────────────────────────────────────────────
DEFAULT_SIMS: int = 50_000

# ── Global averages (computed once at import) ─────────────────────────────────
_MEAN_ATT: float = sum(t["att"] for t in TEAMS.values()) / len(TEAMS)
_MEAN_DEF: float = sum(t["defence"] for t in TEAMS.values()) / len(TEAMS)

# ── Model calibration constants ───────────────────────────────────────────────
# Shrink extreme sample-based stats towards the field mean (Bayesian regression).
# Addresses inflated stats from weak-confederation fixtures (CAF, CONCACAF).
SHRINK_K: float = 0.35

# FIFA ranking adjustment: tanh-bounded ±RANK_K multiplier.
# log(MEDIAN_RANK / team_rank): positive for top teams, negative for weak ones.
RANK_K: float = 0.40
MEDIAN_RANK: int = 40

# Home advantage multiplier for tournament host nations (USA, Canada, Mexico).
HOME_ADV: float = 1.12


def _eff_att(team: str) -> float:
    """Effective attack rate: shrinkage + FIFA ranking upward adjustment."""
    raw = TEAMS[team]["att"]
    shrunk = raw * (1 - SHRINK_K) + _MEAN_ATT * SHRINK_K
    rank = TEAMS[team].get("fifa_rank", MEDIAN_RANK)
    rank_mult = 1.0 + RANK_K * math.tanh(math.log(MEDIAN_RANK / rank))
    return shrunk * rank_mult


def _eff_def(team: str) -> float:
    """Effective defence rate: shrinkage + FIFA ranking downward adjustment (lower GA = better)."""
    raw = TEAMS[team]["defence"]
    shrunk = raw * (1 - SHRINK_K) + _MEAN_DEF * SHRINK_K
    rank = TEAMS[team].get("fifa_rank", MEDIAN_RANK)
    # Divide: top teams concede less → rank_mult > 1 reduces effective GA
    rank_mult = 1.0 + RANK_K * math.tanh(math.log(MEDIAN_RANK / rank))
    return shrunk / rank_mult


# Pre-computed effective mean defence for lambda scaling (computed after helpers defined)
def _compute_eff_mean_def() -> float:
    return sum(_eff_def(t) for t in TEAMS) / len(TEAMS)

_EFF_MEAN_DEF: float = _compute_eff_mean_def()


class MatchResult(TypedDict):
    home_win: float
    draw: float
    away_win: float
    over_05: float
    over_15: float
    over_25: float
    over_35: float
    over_45: float
    btts: float
    ah_home: dict[float, float]   # line → home cover probability
    ah_away: dict[float, float]   # line → away cover probability
    ah_push: dict[float, float]   # line → push probability
    lambda_home: float
    lambda_away: float
    score_grid: dict[tuple[int, int], float]


def get_lambdas(home: str, away: str) -> tuple[float, float]:
    """
    Compute expected goals using shrinkage-adjusted Maher parameterisation:

        λ_home = eff_att(home) × (eff_def(away) / eff_mean_def) × home_adv
        λ_away = eff_att(away) × (eff_def(home) / eff_mean_def)

    Effective ratings apply Bayesian shrinkage towards the field mean (corrects
    for weak-confederation inflation) and a FIFA ranking multiplier (top teams
    boosted, bottom teams reduced, tanh-bounded at ±30%).  Host nations get a
    1.12× home advantage on their attack lambda.

    Returns (lambda_home, lambda_away).
    """
    h_att = _eff_att(home)
    a_def = _eff_def(away)
    a_att = _eff_att(away)
    h_def = _eff_def(home)

    home_mult = HOME_ADV if TEAMS[home].get("host") else 1.0

    lam_h = h_att * (a_def / _EFF_MEAN_DEF) * home_mult
    lam_a = a_att * (h_def / _EFF_MEAN_DEF)

    lam_h = max(0.3, min(lam_h, 6.0))
    lam_a = max(0.3, min(lam_a, 6.0))

    logger.debug(
        "λ %s=%.3f  %s=%.3f  (eff_mean_def=%.3f, home_mult=%.2f)",
        home, lam_h, away, lam_a, _EFF_MEAN_DEF, home_mult,
    )
    return lam_h, lam_a


def dc_tau(x: int, y: int, lam: float, mu: float, rho: float = RHO) -> float:
    """Dixon-Coles correction factor for low-score outcomes."""
    if x == 0 and y == 0:
        return 1.0 - lam * mu * rho
    if x == 0 and y == 1:
        return 1.0 + lam * rho
    if x == 1 and y == 0:
        return 1.0 + mu * rho
    if x == 1 and y == 1:
        return 1.0 - rho
    return 1.0


def score_grid(
    lam_h: float, lam_a: float, max_goals: int = 7
) -> dict[tuple[int, int], float]:
    """
    Return probability mass for every scoreline up to max_goals each,
    with Dixon-Coles correction applied to low-score cells.
    """
    grid: dict[tuple[int, int], float] = {}
    total = 0.0
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            p = poisson.pmf(h, lam_h) * poisson.pmf(a, lam_a)
            p *= dc_tau(h, a, lam_h, lam_a)
            grid[(h, a)] = p
            total += p
    # Renormalise (DC correction shifts mass slightly)
    if total > 0:
        grid = {k: v / total for k, v in grid.items()}
    return grid


def _ah_result(
    home_goals: int,
    away_goals: int,
    line: float,
) -> tuple[float, float, float]:
    """
    Resolve Asian Handicap for a single scoreline.
    Returns (home_cover, push, away_cover) fractions summing to 1.0.

    Quarter-ball lines (e.g. -0.75) split the stake 50/50 across
    the two adjacent whole/half lines.
    """
    # Decompose quarter lines into two adjacent bets
    remainder = line % 0.5
    if abs(remainder - 0.25) < 1e-9:
        # e.g. -0.75 → average of -0.5 and -1.0
        low = line - 0.25
        high = line + 0.25
        hc_l, pu_l, ac_l = _ah_result(home_goals, away_goals, low)
        hc_h, pu_h, ac_h = _ah_result(home_goals, away_goals, high)
        return (hc_l + hc_h) / 2, (pu_l + pu_h) / 2, (ac_l + ac_h) / 2

    margin = home_goals - away_goals + line  # positive → home covers
    if abs(margin) < 1e-9:
        return 0.0, 1.0, 0.0
    return (1.0, 0.0, 0.0) if margin > 0 else (0.0, 0.0, 1.0)


AH_LINES: list[float] = [
    -2.5, -2.0, -1.75, -1.5, -1.25, -1.0, -0.75, -0.5, -0.25,
    0.0,
    0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5,
]


def simulate_match(
    home: str,
    away: str,
    n_sims: int = DEFAULT_SIMS,
    rng: np.random.Generator | None = None,
) -> MatchResult:
    """
    Run Monte Carlo simulation and return probability estimates for all markets.

    Dixon-Coles correction is applied post-simulation by reweighting
    outcomes via their correction factors (faster than redrawing).
    """
    if rng is None:
        rng = np.random.default_rng()

    lam_h, lam_a = get_lambdas(home, away)

    # Draw goals
    h_goals = rng.poisson(lam_h, n_sims)
    a_goals = rng.poisson(lam_a, n_sims)

    # Compute Dixon-Coles weights for each simulation
    dc_weights = np.ones(n_sims)
    for i in range(n_sims):
        dc_weights[i] = dc_tau(int(h_goals[i]), int(a_goals[i]), lam_h, lam_a)
    dc_weights = np.clip(dc_weights, 0.0, None)
    w_total = dc_weights.sum()

    def wp(mask: np.ndarray) -> float:
        return float(dc_weights[mask].sum() / w_total)

    total = h_goals + a_goals
    diff = h_goals - a_goals

    home_win = wp(diff > 0)
    draw = wp(diff == 0)
    away_win = wp(diff < 0)

    over_05 = wp(total > 0)
    over_15 = wp(total > 1)
    over_25 = wp(total > 2)
    over_35 = wp(total > 3)
    over_45 = wp(total > 4)
    btts = wp((h_goals > 0) & (a_goals > 0))

    # Asian Handicap by line
    ah_home: dict[float, float] = {}
    ah_away: dict[float, float] = {}
    ah_push: dict[float, float] = {}
    for line in AH_LINES:
        hc = np.zeros(n_sims)
        pu = np.zeros(n_sims)
        ac = np.zeros(n_sims)
        for i in range(n_sims):
            hc[i], pu[i], ac[i] = _ah_result(int(h_goals[i]), int(a_goals[i]), line)
        ah_home[line] = float((dc_weights * hc).sum() / w_total)
        ah_push[line] = float((dc_weights * pu).sum() / w_total)
        ah_away[line] = float((dc_weights * ac).sum() / w_total)

    grid = score_grid(lam_h, lam_a)

    return MatchResult(
        home_win=home_win,
        draw=draw,
        away_win=away_win,
        over_05=over_05,
        over_15=over_15,
        over_25=over_25,
        over_35=over_35,
        over_45=over_45,
        btts=btts,
        ah_home=ah_home,
        ah_away=ah_away,
        ah_push=ah_push,
        lambda_home=lam_h,
        lambda_away=lam_a,
        score_grid=grid,
    )


class GroupResult(TypedDict):
    qualification: dict[str, float]   # team → probability of top-2 finish
    third_place: dict[str, float]     # team → probability of finishing 3rd
    win_group: dict[str, float]       # team → probability of group winner
    points_avg: dict[str, float]      # team → average points


def simulate_group(
    group: str,
    n_sims: int = 20_000,
    rng: np.random.Generator | None = None,
) -> GroupResult:
    """
    Simulate a complete group stage (round-robin, 6 matches) n_sims times.
    WC2026: top 2 qualify automatically; 3rd place enters best-third playoff.
    """
    from .data import GROUPS

    teams = GROUPS[group]
    if len(teams) != 4:
        raise ValueError(f"Group {group} has {len(teams)} teams, expected 4")

    if rng is None:
        rng = np.random.default_rng()

    # Pre-compute lambdas for all 6 fixtures
    fixtures = [
        (teams[i], teams[j])
        for i in range(4)
        for j in range(i + 1, 4)
    ]
    lambdas = {(h, a): get_lambdas(h, a) for h, a in fixtures}

    qual_count: dict[str, int] = {t: 0 for t in teams}
    third_count: dict[str, int] = {t: 0 for t in teams}
    win_count: dict[str, int] = {t: 0 for t in teams}
    pts_total: dict[str, float] = {t: 0.0 for t in teams}

    for _ in range(n_sims):
        pts: dict[str, int] = {t: 0 for t in teams}
        gd: dict[str, int] = {t: 0 for t in teams}
        gf: dict[str, int] = {t: 0 for t in teams}

        for home, away in fixtures:
            lh, la = lambdas[(home, away)]
            hg = int(rng.poisson(lh))
            ag = int(rng.poisson(la))
            tau = dc_tau(hg, ag, lh, la)
            # Stochastic DC correction: re-roll if tau < uniform(0,1)
            if tau < rng.uniform():
                # Simple re-roll for DC correction (accurate at low cost)
                hg = int(rng.poisson(lh))
                ag = int(rng.poisson(la))

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

        # Sort: pts → gd → gf → random (coin flip for equal teams)
        order = sorted(
            teams,
            key=lambda t: (pts[t], gd[t], gf[t], random.random()),
            reverse=True,
        )
        win_count[order[0]] += 1
        qual_count[order[0]] += 1
        qual_count[order[1]] += 1
        third_count[order[2]] += 1
        for t in teams:
            pts_total[t] += pts[t]

    return GroupResult(
        qualification={t: qual_count[t] / n_sims for t in teams},
        third_place={t: third_count[t] / n_sims for t in teams},
        win_group={t: win_count[t] / n_sims for t in teams},
        points_avg={t: pts_total[t] / n_sims for t in teams},
    )


def find_value(
    model_prob: float,
    decimal_odds: float,
    vig: float = 0.047,
) -> tuple[float, bool]:
    """
    Compute edge relative to market price net of vig.

    Returns (edge, is_value) where is_value is True when edge > 0.
    """
    implied = 1.0 / decimal_odds
    edge = model_prob - implied - vig
    return edge, edge > 0.0


def scorer_probs(
    team: str,
    match_lambda: float,
    top_n: int = 5,
) -> list[dict]:
    """
    Estimate anytime scorer probability for a team's top players.

    Uses Poisson individual scoring:
        λ_player = player_gpg * (match_lambda / team_avg_att)
        P(scores) = 1 - exp(-λ_player)

    Returns list of dicts sorted by probability descending.
    """
    team_avg_att = TEAMS[team]["att"]
    players = PLAYERS.get(team, [])
    results = []
    for p in players:
        lam = p["gpg"] * (match_lambda / team_avg_att)
        prob = 1.0 - math.exp(-lam)
        results.append({"name": p["name"], "prob": round(prob, 3)})
    results.sort(key=lambda x: x["prob"], reverse=True)
    return results[:top_n]
