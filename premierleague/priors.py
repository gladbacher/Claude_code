"""
Season priors for the Premier League fit.

Two real problems the plain MLE can't solve alone:
  1. Newly promoted clubs have no top-flight history — their strengths are
     unknown until they've played a chunk of the season.
  2. Early in a season, 5-6 games is too few to fit 20 teams stably.

`season_priors` builds a prior (att, def) for every club plus a suggested
`prior_strength`, to pass to `fit.fit_ratings`. Carried-over clubs are anchored
to last season's fitted rating; promoted clubs get a weak "just-survives"
prior. The shrinkage fades naturally as real results accumulate.
"""

from __future__ import annotations

from .dixoncoles import Ratings

# Typical strength of a promoted club: around the relegation battle, i.e. a bit
# below league-average attack and defence (log scale, centred ratings).
PROMOTED_PRIOR: tuple[float, float] = (-0.28, -0.26)


def season_priors(
    last_season: Ratings | None,
    current_teams: list[str],
    promoted: list[str] | None = None,
    promoted_prior: tuple[float, float] = PROMOTED_PRIOR,
    prior_strength: float = 6.0,
) -> tuple[dict[str, tuple[float, float]], float]:
    """
    Build (priors, prior_strength) for `fit_ratings`.

    - last_season: fitted ratings from the previous campaign (or None).
    - current_teams: the 20 clubs in the division this season.
    - promoted: clubs new to the division (default: those absent last season).
    - prior_strength: ridge weight in "pseudo-matches" (~6 ≈ two months of form
      before the data dominates). Higher = stickier priors.
    """
    promoted = set(promoted or [])
    if last_season is not None and not promoted:
        promoted = {t for t in current_teams if t not in last_season.att}

    priors: dict[str, tuple[float, float]] = {}
    for t in current_teams:
        if t in promoted or last_season is None or t not in last_season.att:
            priors[t] = promoted_prior
        else:
            priors[t] = (last_season.att[t], last_season.dfn[t])
    return priors, prior_strength
