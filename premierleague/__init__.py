"""
Premier League Dixon-Coles model.

A data-fittable league model built on the same Dixon-Coles Poisson core as the
WC2026 project, but with team strengths estimated by maximum likelihood from
match results (fit.py) rather than hand-tuned, and a proper per-match home
advantage. Run `python -m premierleague` for a projected-table demo.
"""

from .dixoncoles import Ratings, match_lambdas, outcome_probs, strip_vig_1x2, value_edge
from .ratings import BUNDLED, PL_TEAMS, build_ratings
from .fit import fit_ratings, Match
from .season import simulate_season, projected_table

__all__ = [
    "Ratings", "match_lambdas", "outcome_probs", "strip_vig_1x2", "value_edge",
    "BUNDLED", "PL_TEAMS", "build_ratings",
    "fit_ratings", "Match",
    "simulate_season", "projected_table",
]
