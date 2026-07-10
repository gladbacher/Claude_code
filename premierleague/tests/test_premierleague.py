"""Tests for the Premier League Dixon-Coles model."""

import numpy as np

from premierleague.ratings import BUNDLED, PL_TEAMS
from premierleague.dixoncoles import outcome_probs, match_lambdas, strip_vig_1x2
from premierleague.data import synthetic_season, round_robin_fixtures
from premierleague.fit import fit_ratings
from premierleague.season import simulate_season
from premierleague.market import MatchOdds, assess_match, value_bets
from premierleague.priors import season_priors, PROMOTED_PRIOR


def test_fixtures_full_double_round_robin():
    fx = round_robin_fixtures(PL_TEAMS)
    assert len(fx) == 20 * 19          # 380 matches
    assert len(set(fx)) == len(fx)     # no duplicates


def test_outcome_probs_normalised():
    lh, la = match_lambdas(BUNDLED, "Man City", "Southampton")
    p = outcome_probs(lh, la, BUNDLED.rho)
    assert abs(p["home"] + p["draw"] + p["away"] - 1.0) < 1e-6
    assert lh > la                     # strong home team scores more


def test_strip_vig():
    fair = strip_vig_1x2(2.0, 3.5, 4.0)
    assert abs(fair["home"] + fair["draw"] + fair["away"] - 1.0) < 1e-9
    assert fair["overround"] > 0       # book has margin


def test_season_probabilities_conserved():
    probs = simulate_season(BUNDLED, n_sims=1500, rng=np.random.default_rng(1))
    assert abs(sum(p["title"] for p in probs.values()) - 1.0) < 1e-6
    assert abs(sum(p["top4"] for p in probs.values()) - 4.0) < 1e-6
    assert abs(sum(p["top6"] for p in probs.values()) - 6.0) < 1e-6
    assert abs(sum(p["relegation"] for p in probs.values()) - 3.0) < 1e-6


def test_stronger_team_higher_title_odds():
    probs = simulate_season(BUNDLED, n_sims=1500, rng=np.random.default_rng(2))
    assert probs["Man City"]["title"] > probs["Southampton"]["title"]
    assert probs["Southampton"]["relegation"] > probs["Liverpool"]["relegation"]


def test_mle_recovers_strength_ranking():
    """Fitting on a synthetic season should recover the true attack ranking."""
    rng = np.random.default_rng(3)
    matches = synthetic_season(BUNDLED, rng) + synthetic_season(BUNDLED, rng)
    fit = fit_ratings(matches, xi=0.0)
    teams = BUNDLED.teams
    true_a = [BUNDLED.att[t] for t in teams]
    fit_a = [fit.att[t] for t in teams]
    # Pearson correlation of true vs fitted attack strengths.
    mx, my = np.mean(true_a), np.mean(fit_a)
    corr = (np.sum((np.array(true_a) - mx) * (np.array(fit_a) - my))
            / (np.std(true_a) * np.std(fit_a) * len(teams)))
    assert corr > 0.85, f"attack recovery corr too low: {corr:.3f}"


def test_market_edge_matches_model_minus_fair():
    """assess_match edges must equal model prob minus vig-stripped fair prob."""
    mo = MatchOdds("Man City", "Southampton", 1.20, 7.0, 15.0)
    a = assess_match(BUNDLED, mo)
    fair_sum = sum(leg["fair_p"] for leg in a["legs"])
    assert abs(fair_sum - 1.0) < 1e-9            # vig removed
    for leg in a["legs"]:
        assert abs(leg["edge"] - (leg["model_p"] - leg["fair_p"])) < 1e-9
    # Strong home team offered a generous price => positive value on home.
    home_leg = next(l for l in a["legs"] if l["outcome"] == "home")
    assert home_leg["edge"] > 0


def test_value_bets_filters_and_ranks():
    odds = [
        MatchOdds("Man City", "Southampton", 1.60, 4.5, 6.0),   # City underpriced
        MatchOdds("Liverpool", "Arsenal", 2.00, 3.6, 3.8),      # ~fair
    ]
    rows = value_bets(BUNDLED, odds, min_edge=0.03)
    assert all(r["edge"] >= 0.03 for r in rows)
    assert rows == sorted(rows, key=lambda r: r["edge"], reverse=True)


def test_priors_anchor_promoted_on_small_sample():
    """With few games, priors keep a promoted club nearer its weak prior."""
    rng = np.random.default_rng(11)
    sample = synthetic_season(BUNDLED, rng)[:70]
    promoted = ["Ipswich", "Leicester", "Southampton"]
    priors, strength = season_priors(BUNDLED, BUNDLED.teams, promoted=promoted)
    assert priors["Ipswich"] == PROMOTED_PRIOR
    no_prior = fit_ratings(sample, xi=0.0)
    with_prior = fit_ratings(sample, xi=0.0, priors=priors, prior_strength=strength)
    # The prior-shrunk estimate sits closer to the weak prior than the raw MLE.
    d_prior = abs(with_prior.att["Ipswich"] - PROMOTED_PRIOR[0])
    d_raw = abs(no_prior.att["Ipswich"] - PROMOTED_PRIOR[0])
    assert d_prior <= d_raw
