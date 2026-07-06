"""
Bundled Premier League team strengths (illustrative, 2024-25 shape).

These let the season simulator run out of the box. They are hand-set *priors*
in the same spirit as the WC model's ratings — the point of this package is
that fit.py can REPLACE them with values estimated by maximum likelihood from
real match results. Attack/defence are on the log scale, centred to league
average (0 = average, +0.3 ≈ scores/concedes ~35% better than average).
"""

from __future__ import annotations

from .dixoncoles import Ratings

# ── Baseline match environment ────────────────────────────────────────────────
# Average team at home ≈ exp(mu + home_adv) goals, away ≈ exp(mu) goals.
MU = 0.223         # log(1.25) — average away goals ~1.25
HOME_ADV = 0.215   # ~1.24× at home (average home goals ~1.55)
RHO = -0.05        # Dixon-Coles rho for English league (small, per Dixon-Coles 1997)

# Raw (att, def) log-strengths, higher = better. Centred in build_ratings().
_RAW: dict[str, tuple[float, float]] = {
    "Man City":          ( 0.45,  0.30),
    "Liverpool":         ( 0.42,  0.40),
    "Arsenal":           ( 0.35,  0.45),
    "Chelsea":           ( 0.30,  0.18),
    "Newcastle":         ( 0.30,  0.15),
    "Tottenham":         ( 0.28, -0.15),
    "Aston Villa":       ( 0.22,  0.10),
    "Brentford":         ( 0.20, -0.05),
    "Brighton":          ( 0.18,  0.05),
    "Bournemouth":       ( 0.15,  0.12),
    "Crystal Palace":    ( 0.12,  0.14),
    "Fulham":            ( 0.10,  0.06),
    "Nottingham Forest": ( 0.10,  0.22),
    "Man United":        ( 0.05,  0.00),
    "West Ham":          ( 0.00, -0.20),
    "Everton":           (-0.15,  0.12),
    "Wolves":            (-0.05, -0.25),
    "Leicester":         (-0.20, -0.35),
    "Ipswich":           (-0.25, -0.30),
    "Southampton":       (-0.45, -0.42),
}


def build_ratings() -> Ratings:
    """Return centred bundled ratings (attack and defence each average to 0)."""
    att = {t: a for t, (a, _d) in _RAW.items()}
    dfn = {t: d for t, (_a, d) in _RAW.items()}
    m_a = sum(att.values()) / len(att)
    m_d = sum(dfn.values()) / len(dfn)
    att = {t: v - m_a for t, v in att.items()}
    dfn = {t: v - m_d for t, v in dfn.items()}
    # Preserve the goal scale after centring (see dixoncoles docstring).
    mu = MU - m_a + m_d
    return Ratings(mu=mu, home_adv=HOME_ADV, rho=RHO, att=att, dfn=dfn)


PL_TEAMS: list[str] = list(_RAW.keys())
BUNDLED = build_ratings()
