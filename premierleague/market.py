"""
Market / value layer for the Premier League model.

Compares model probabilities (from Dixon-Coles ratings) against bookmaker
1X2 odds, stripping the vig *properly* by normalising the overround
(`dixoncoles.strip_vig_1x2`) — the correct fair-price baseline. Returns per-
outcome edges and a ranked list of value bets across a set of fixtures.

    from premierleague.market import assess_match, value_bets, MatchOdds
    bets = value_bets(ratings, [MatchOdds("Arsenal","Chelsea",1.9,3.6,4.2), ...])
"""

from __future__ import annotations

from dataclasses import dataclass

from .dixoncoles import Ratings, match_lambdas, outcome_probs, strip_vig_1x2, value_edge


@dataclass
class MatchOdds:
    home: str
    away: str
    home_odds: float
    draw_odds: float
    away_odds: float


def assess_match(ratings: Ratings, mo: MatchOdds) -> dict:
    """Model vs market for one fixture: probs, fair prices, and per-outcome edges."""
    lh, la = match_lambdas(ratings, mo.home, mo.away)
    p = outcome_probs(lh, la, ratings.rho)
    fair = strip_vig_1x2(mo.home_odds, mo.draw_odds, mo.away_odds)

    legs = []
    for key, odds in (("home", mo.home_odds), ("draw", mo.draw_odds), ("away", mo.away_odds)):
        model_p = p[key]
        edge = value_edge(model_p, fair[key])
        legs.append({
            "outcome": key,
            "model_p": model_p,
            "fair_p": fair[key],
            "odds": odds,
            "edge": edge,
            "ev": model_p * odds - 1.0,      # expected value per unit stake
        })
    legs.sort(key=lambda x: x["edge"], reverse=True)
    return {
        "home": mo.home, "away": mo.away,
        "lambda_home": lh, "lambda_away": la,
        "overround": fair["overround"],
        "legs": legs,
        "best": legs[0],
    }


_LEG_LABEL = {"home": "Home", "draw": "Draw", "away": "Away"}


def value_bets(ratings: Ratings, odds_list: list[MatchOdds],
               min_edge: float = 0.02) -> list[dict]:
    """
    Every outcome whose model probability beats the vig-stripped fair price by
    at least `min_edge`, ranked by edge. Each row names the fixture, the leg,
    model vs fair %, the price and the EV.
    """
    rows = []
    for mo in odds_list:
        a = assess_match(ratings, mo)
        for leg in a["legs"]:
            if leg["edge"] >= min_edge:
                side = mo.home if leg["outcome"] == "home" else (
                    mo.away if leg["outcome"] == "away" else "Draw")
                rows.append({
                    "match": f"{mo.home} v {mo.away}",
                    "bet": f"{_LEG_LABEL[leg['outcome']]}"
                           + (f" ({side})" if leg["outcome"] != "draw" else ""),
                    "model_p": leg["model_p"],
                    "fair_p": leg["fair_p"],
                    "odds": leg["odds"],
                    "edge": leg["edge"],
                    "ev": leg["ev"],
                })
    rows.sort(key=lambda r: r["edge"], reverse=True)
    return rows
