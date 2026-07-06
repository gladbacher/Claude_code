"""
Maximum-likelihood Dixon-Coles fit with exponential time decay.

This is the piece that turns the engine into a real, self-updating model:
given a list of match results it estimates every team's attack and defence
strength, the home-advantage term and the low-score correlation rho by
maximising the (time-weighted) Poisson likelihood — the method from
Dixon & Coles (1997). Recent matches can be up-weighted via `xi` so the
ratings track current form.

    minimise  −Σ w_t [ log τ(x,y) + log Pois(x; λ_h) + log Pois(y; λ_a) ]

Usage:
    from premierleague.fit import fit_ratings
    ratings = fit_ratings(matches, xi=0.0018)   # xi in 1/days; 0 = no decay
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from .dixoncoles import Ratings, dc_tau


@dataclass
class Match:
    home: str
    away: str
    home_goals: int
    away_goals: int
    days_ago: float = 0.0     # for time-decay weighting; 0 = weight 1


def _log_pois(k: int, lam: float) -> float:
    return -lam + k * math.log(lam) - math.lgamma(k + 1)


def fit_ratings(matches: list[Match], xi: float = 0.0,
                max_iter: int = 200) -> Ratings:
    """
    Fit Dixon-Coles ratings by weighted maximum likelihood.

    xi: time-decay rate (per day). Weight of a match d days old is exp(-xi*d).
        xi=0 weights all matches equally. A season half-life of ~1 year is
        roughly xi≈0.0019.
    """
    teams = sorted({m.home for m in matches} | {m.away for m in matches})
    n = len(teams)
    idx = {t: i for i, t in enumerate(teams)}

    weights = np.array([math.exp(-xi * m.days_ago) for m in matches])
    hi = np.array([idx[m.home] for m in matches])
    ai = np.array([idx[m.away] for m in matches])
    hg = np.array([m.home_goals for m in matches])
    ag = np.array([m.away_goals for m in matches])

    # Parameter vector: [att(0..n-1), def(0..n-1), home_adv, rho, mu]
    # Identifiability: att and def are each softly centred via a penalty.
    def unpack(theta):
        att = theta[:n]
        dfn = theta[n:2 * n]
        home_adv = theta[2 * n]
        rho = theta[2 * n + 1]
        mu = theta[2 * n + 2]
        return att, dfn, home_adv, rho, mu

    def neg_log_lik(theta):
        att, dfn, home_adv, rho, mu = unpack(theta)
        lam_h = np.exp(mu + att[hi] - dfn[ai] + home_adv)
        lam_a = np.exp(mu + att[ai] - dfn[hi])
        lam_h = np.clip(lam_h, 1e-6, 12.0)
        lam_a = np.clip(lam_a, 1e-6, 12.0)

        # Poisson log-likelihood (vectorised).
        ll = (-lam_h + hg * np.log(lam_h) - _gammaln(hg + 1)
              + -lam_a + ag * np.log(lam_a) - _gammaln(ag + 1))

        # Dixon-Coles low-score correction (only the four affected cells).
        tau = np.ones(len(matches))
        m00 = (hg == 0) & (ag == 0)
        m01 = (hg == 0) & (ag == 1)
        m10 = (hg == 1) & (ag == 0)
        m11 = (hg == 1) & (ag == 1)
        tau[m00] = 1.0 - lam_h[m00] * lam_a[m00] * rho
        tau[m01] = 1.0 + lam_h[m01] * rho
        tau[m10] = 1.0 + lam_a[m10] * rho
        tau[m11] = 1.0 - rho
        tau = np.clip(tau, 1e-9, None)
        ll = ll + np.log(tau)

        # Sum-zero penalty keeps att/def identifiable and centred.
        penalty = 100.0 * (att.mean() ** 2 + dfn.mean() ** 2)
        return -(weights * ll).sum() + penalty

    theta0 = np.concatenate([
        np.zeros(n),               # att
        np.zeros(n),               # def
        [0.2],                     # home_adv
        [-0.05],                   # rho
        [math.log(1.3)],           # mu
    ])
    bounds = ([(-2, 2)] * n) + ([(-2, 2)] * n) + [(-0.5, 1.0), (-0.3, 0.3), (-1, 2)]

    res = minimize(neg_log_lik, theta0, method="L-BFGS-B", bounds=bounds,
                   options={"maxiter": max_iter})

    att, dfn, home_adv, rho, mu = unpack(res.x)
    return Ratings(
        mu=float(mu), home_adv=float(home_adv), rho=float(rho),
        att={t: float(att[idx[t]]) for t in teams},
        dfn={t: float(dfn[idx[t]]) for t in teams},
    )


def _gammaln(arr):
    from scipy.special import gammaln
    return gammaln(arr)
