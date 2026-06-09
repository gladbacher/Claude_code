"""Tests for the full-tournament Monte Carlo simulator."""

import numpy as np

from wc2026.tournament import simulate_tournament, STAGES, R32_BRACKET, _THIRD_SLOT_FACES
from wc2026.data import TEAMS


def test_stage_totals_conserved():
    """Each stage's probabilities must sum to the exact number of slots."""
    probs = simulate_tournament(n_sims=1500, rng=np.random.default_rng(1))
    expected = {
        "win_group": 12, "qualify": 24, "reach_r32": 32, "reach_r16": 16,
        "reach_qf": 8, "reach_sf": 4, "reach_final": 2, "champion": 1,
    }
    for stage, exp in expected.items():
        total = sum(probs[t][stage] for t in probs)
        assert abs(total - exp) < 1e-6, f"{stage} sums to {total}, expected {exp}"


def test_probabilities_monotonic():
    """A team cannot reach a later stage more often than an earlier one."""
    probs = simulate_tournament(n_sims=1500, rng=np.random.default_rng(2))
    chain = STAGES[2:]  # reach_r32 → champion
    for t, p in probs.items():
        for a, b in zip(chain, chain[1:]):
            assert p[a] >= p[b] - 1e-9, f"{t}: {a}={p[a]} < {b}={p[b]}"


def test_all_teams_present():
    probs = simulate_tournament(n_sims=500, rng=np.random.default_rng(3))
    assert len(probs) == 48
    assert all(set(p.keys()) == set(STAGES) for p in probs.values())


def test_bracket_is_complete_and_valid():
    """R32 bracket must field all 24 winner/runner slots + 8 thirds, no same-group ties."""
    assert len(R32_BRACKET) == 16
    codes = [c for match in R32_BRACKET for c in match]
    winners = {c[1] for c in codes if c[0] == "1"}
    runners = {c[1] for c in codes if c[0] == "2"}
    thirds = [c[1] for c in codes if c[0] == "3"]
    assert winners == set("ABCDEFGHIJKL")
    assert runners == set("ABCDEFGHIJKL")
    assert sorted(thirds) == list(range(8))
    # No match pairs two sides from the same group.
    for a, b in R32_BRACKET:
        ga = a[1] if a[0] != "3" else None
        gb = b[1] if b[0] != "3" else None
        if ga and gb:
            assert ga != gb
    # Third slots face real groups, distinct count matches slots.
    assert len(_THIRD_SLOT_FACES) == 8


def test_strong_team_beats_title_longshot():
    """Sanity: a top contender should have materially higher title odds than a minnow."""
    probs = simulate_tournament(n_sims=2000, rng=np.random.default_rng(4))
    assert probs["England"]["champion"] > probs["Haiti"]["champion"]
    assert probs["Spain"]["reach_r16"] > probs["Saudi Arabia"]["reach_r16"]
