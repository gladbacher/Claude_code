"""Unit tests for the WC2026 model core."""

import math
import pytest

from wc2026.model import (
    get_lambdas,
    simulate_match,
    simulate_group,
    find_value,
    dc_tau,
    score_grid,
    AH_LINES,
)
from wc2026.data import TEAMS, GROUPS
from wc2026.staking import BankrollManager


# ── get_lambdas ───────────────────────────────────────────────────────────────

def test_get_lambdas_returns_positive():
    lh, la = get_lambdas("Spain", "Qatar")
    assert lh > 0
    assert la > 0


def test_get_lambdas_strong_vs_weak():
    """Spain should have a higher lambda than Qatar when attacking."""
    lh, la = get_lambdas("Spain", "Qatar")
    assert lh > la, "Spain expected goals should exceed Qatar's"


def test_get_lambdas_clamped():
    """Lambdas must stay within reasonable range."""
    for home in list(TEAMS.keys())[:6]:
        for away in list(TEAMS.keys())[6:12]:
            lh, la = get_lambdas(home, away)
            assert 0.3 <= lh <= 6.0
            assert 0.3 <= la <= 6.0


# ── dc_tau ────────────────────────────────────────────────────────────────────

def test_dc_tau_non_low_scores_is_one():
    assert dc_tau(2, 3, 1.5, 1.5) == pytest.approx(1.0)
    assert dc_tau(3, 0, 1.5, 1.5) == pytest.approx(1.0)


def test_dc_tau_low_scores_deviate():
    # rho = -0.13 should decrease 0-0 probability slightly
    assert dc_tau(0, 0, 1.5, 1.5) != pytest.approx(1.0)


# ── score_grid ────────────────────────────────────────────────────────────────

def test_score_grid_sums_to_one():
    grid = score_grid(1.5, 1.2)
    total = sum(grid.values())
    assert total == pytest.approx(1.0, abs=1e-4)


def test_score_grid_most_likely_low_scores():
    """Most probable scorelines should be low-scoring."""
    grid = score_grid(1.2, 1.0)
    top3 = sorted(grid, key=grid.get, reverse=True)[:3]
    for h, a in top3:
        assert h + a <= 4


# ── simulate_match ────────────────────────────────────────────────────────────

def test_match_probabilities_sum_to_one():
    result = simulate_match("Germany", "Austria", n_sims=10_000)
    total = result["home_win"] + result["draw"] + result["away_win"]
    assert total == pytest.approx(1.0, abs=0.005)


def test_ah_probabilities_sum_to_one():
    result = simulate_match("France", "Iraq", n_sims=10_000)
    for line in AH_LINES:
        total = result["ah_home"][line] + result["ah_push"][line] + result["ah_away"][line]
        assert total == pytest.approx(1.0, abs=0.005), f"AH line {line} sums to {total}"


def test_germany_beats_curacao():
    """Germany should be heavy favourite over Curacao."""
    result = simulate_match("Germany", "Curacao", n_sims=20_000)
    assert result["home_win"] > 0.55


def test_spain_beats_saudi_arabia():
    result = simulate_match("Spain", "Saudi Arabia", n_sims=20_000)
    assert result["home_win"] > 0.60


def test_btts_in_range():
    result = simulate_match("Sweden", "Netherlands", n_sims=10_000)
    assert 0.0 < result["btts"] < 1.0


# ── simulate_group ────────────────────────────────────────────────────────────

def test_group_qual_sums_to_two():
    """Total qualification probability across a group must sum to exactly 2.0."""
    result = simulate_group("H", n_sims=5_000)
    total = sum(result["qualification"].values())
    assert total == pytest.approx(2.0, abs=0.05)


def test_group_l_england_top_qual():
    """England should have highest qualification probability in Group L."""
    result = simulate_group("L", n_sims=5_000)
    best = max(result["qualification"], key=result["qualification"].get)
    assert best == "England"


def test_group_win_sums_to_one():
    result = simulate_group("A", n_sims=5_000)
    total = sum(result["win_group"].values())
    assert total == pytest.approx(1.0, abs=0.05)


# ── find_value ────────────────────────────────────────────────────────────────

def test_find_value_detects_edge():
    edge, is_value = find_value(model_prob=0.55, decimal_odds=2.20)
    assert is_value
    assert edge > 0


def test_find_value_no_edge():
    edge, is_value = find_value(model_prob=0.40, decimal_odds=2.10)
    assert not is_value


# ── BankrollManager ───────────────────────────────────────────────────────────

def test_kelly_stake_zero_when_no_edge():
    bm = BankrollManager(bankroll=1000.0, min_edge=0.05)
    stake, edge = bm.kelly_stake(model_p=0.45, decimal_odds=2.10)
    assert stake == 0.0


def test_kelly_stake_capped():
    bm = BankrollManager(bankroll=1000.0, max_kelly_fraction=0.25, min_edge=0.01)
    stake, edge = bm.kelly_stake(model_p=0.90, decimal_odds=1.50)
    assert stake <= 1000.0 * 0.25


def test_kelly_stake_positive_edge():
    bm = BankrollManager(bankroll=1000.0, min_edge=0.05)
    stake, edge = bm.kelly_stake(model_p=0.60, decimal_odds=2.10)
    assert stake > 0
    assert edge > 0


def test_bankroll_settlement():
    bm = BankrollManager(bankroll=1000.0, min_edge=0.01)
    bet = bm.log_bet("Eng vs Gha", "Home win", model_p=0.65, decimal_odds=1.90)
    if bet:
        bm.settle(bet, won=True)
        assert bm.bankroll > 1000.0


def test_all_teams_present():
    assert len(TEAMS) == 48


def test_all_groups_have_four_teams():
    for g, members in GROUPS.items():
        assert len(members) == 4, f"Group {g} has {len(members)} teams"
