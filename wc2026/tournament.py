"""
WC2026 full-tournament Monte Carlo: group stage → knockouts → champion.

Extends the group simulator to play the complete bracket so we can estimate,
for every team, the probability of:
  win_group, qualify (top-2), reach_r32 (top-2 OR best-third),
  reach_r16, reach_qf, reach_sf, reach_final, champion.

The knockout bracket (`R32_BRACKET`) is a FIXED model bracket: it slots group
winners (1X), runners-up (2X) and the eight best third-placed teams into the
Round of 32. It follows FIFA's real principles — winners are spread across the
draw and never meet a same-group side in the R32 — but it is NOT FIFA's exact
official third-place combination table (495 cases for 8-of-12 groups). Path
difficulty for individual teams therefore carries some bracket-model
uncertainty; headline contender probabilities are robust to it.

Group matches use `get_lambdas` (host nations keep their home edge). Knockout
matches are played at neutral venues — no host advantage — and ties are
resolved by a simulated 30-minute extra time, then a near-even penalty shootout
with a small edge to the stronger side.

Usage:
    python -m wc2026.tournament --sims 20000
"""

from __future__ import annotations

import argparse

import numpy as np

from .data import GROUPS, FIXTURES, TEAMS
from .model import (
    get_lambdas,
    dc_tau,
    _eff_att,
    _eff_def,
    _EFF_MEAN_DEF,
)

ALL_GROUPS = sorted(GROUPS.keys())

STAGES = [
    "win_group", "qualify", "reach_r32", "reach_r16",
    "reach_qf", "reach_sf", "reach_final", "champion",
]

STAGE_LABELS = {
    "win_group":   "Win Grp",
    "qualify":     "Top 2",
    "reach_r32":   "R32",
    "reach_r16":   "R16",
    "reach_qf":    "QF",
    "reach_sf":    "SF",
    "reach_final": "Final",
    "champion":    "Champion",
}


# ── Fixed model bracket ───────────────────────────────────────────────────────
# Each entry is a Round-of-32 match between two slot codes:
#   ("1", "A")  group A winner
#   ("2", "A")  group A runner-up
#   ("3", n)    the slot for a best-placed third (n = 0..7), filled per sim
# Listed in bracket order: matches (0,1) feed one R16 tie, (2,3) the next, etc.
# Winners face thirds/runners-up from OTHER groups; no group winner sits in the
# same R32 match as a side from its own group.
R32_BRACKET: list[tuple[tuple, tuple]] = [
    # ── Quarter 1 ──
    (("1", "A"), ("3", 0)),   (("2", "B"), ("2", "C")),
    (("1", "D"), ("2", "F")),  (("1", "E"), ("3", 1)),
    # ── Quarter 2 ──
    (("1", "G"), ("3", 2)),   (("2", "E"), ("2", "H")),
    (("1", "J"), ("3", 3)),   (("1", "K"), ("2", "L")),
    # ── Quarter 3 ──
    (("1", "C"), ("3", 4)),   (("2", "A"), ("2", "K")),
    (("1", "F"), ("3", 5)),   (("1", "B"), ("2", "D")),
    # ── Quarter 4 ──
    (("1", "H"), ("3", 6)),   (("2", "G"), ("2", "I")),
    (("1", "I"), ("2", "J")),  (("1", "L"), ("3", 7)),
]

# Group winners whose R32 opponent is a best-third (in R32_BRACKET order).
# Used to assign the 8 qualifying thirds while avoiding a same-group rematch.
_THIRD_SLOT_FACES = ["A", "E", "G", "J", "C", "F", "H", "L"]


# ── Pre-computed lambdas ──────────────────────────────────────────────────────

def _group_fixtures_by_group() -> dict[str, list[tuple[str, str]]]:
    """Actual group fixtures (home, away) so host nations keep their home edge."""
    out: dict[str, list[tuple[str, str]]] = {g: [] for g in ALL_GROUPS}
    for home, away, _md, _date in FIXTURES:
        out[TEAMS[home]["group"]].append((home, away))
    return out


_GROUP_FIXTURES = _group_fixtures_by_group()
_GROUP_LAM: dict[tuple[str, str], tuple[float, float]] = {
    (h, a): get_lambdas(h, a)
    for fx in _GROUP_FIXTURES.values() for (h, a) in fx
}


def _neutral_lambdas(t1: str, t2: str) -> tuple[float, float]:
    """Expected goals at a neutral venue (no host advantage) for a knockout tie."""
    l1 = _eff_att(t1) * (_eff_def(t2) / _EFF_MEAN_DEF)
    l2 = _eff_att(t2) * (_eff_def(t1) / _EFF_MEAN_DEF)
    return max(0.3, min(l1, 6.0)), max(0.3, min(l2, 6.0))


# All ordered pairs can meet in the knockouts → precompute once.
_KO_LAM: dict[tuple[str, str], tuple[float, float]] = {}
for _t1 in TEAMS:
    for _t2 in TEAMS:
        if _t1 != _t2:
            _KO_LAM[(_t1, _t2)] = _neutral_lambdas(_t1, _t2)


# ── Match primitives ──────────────────────────────────────────────────────────

def _draw_score(l1: float, l2: float, rng: np.random.Generator) -> tuple[int, int]:
    """Poisson scoreline with the same stochastic Dixon-Coles re-roll as the group sim."""
    g1 = int(rng.poisson(l1))
    g2 = int(rng.poisson(l2))
    if dc_tau(g1, g2, l1, l2) < rng.uniform():
        g1 = int(rng.poisson(l1))
        g2 = int(rng.poisson(l2))
    return g1, g2


def _knockout_winner(t1: str, t2: str, rng: np.random.Generator) -> str:
    """Resolve a single-elimination tie: 90', then 30' ET, then a shootout."""
    l1, l2 = _KO_LAM[(t1, t2)]
    g1, g2 = _draw_score(l1, l2, rng)
    if g1 != g2:
        return t1 if g1 > g2 else t2
    # Extra time: ~1/3 of a match's worth of expected goals.
    e1 = int(rng.poisson(l1 / 3.0))
    e2 = int(rng.poisson(l2 / 3.0))
    if e1 != e2:
        return t1 if e1 > e2 else t2
    # Penalties: near coin-flip, small edge to the stronger attacking side.
    p1 = 0.5 + 0.15 * ((l1 - l2) / (l1 + l2))
    return t1 if rng.uniform() < p1 else t2


# ── One full tournament ───────────────────────────────────────────────────────

def _simulate_group_once(group: str, rng: np.random.Generator) -> list[tuple]:
    """Return standings as a sorted list of (team, pts, gd, gf), best first."""
    teams = GROUPS[group]
    pts = {t: 0 for t in teams}
    gd = {t: 0 for t in teams}
    gf = {t: 0 for t in teams}

    for home, away in _GROUP_FIXTURES[group]:
        lh, la = _GROUP_LAM[(home, away)]
        hg, ag = _draw_score(lh, la, rng)
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

    order = sorted(
        teams,
        key=lambda t: (pts[t], gd[t], gf[t], rng.random()),
        reverse=True,
    )
    return [(t, pts[t], gd[t], gf[t]) for t in order]


def _assign_thirds(third_standings: list[tuple], rng: np.random.Generator) -> dict[int, str]:
    """
    Pick the 8 best third-placed teams and map them to third-slots 0..7,
    avoiding a same-group rematch with the group winner each slot faces.
    `third_standings` is a list of (team, group, pts, gd, gf).
    """
    ranked = sorted(third_standings, key=lambda x: (x[2], x[3], x[4], rng.random()),
                    reverse=True)
    qualifiers = ranked[:8]

    slots = list(range(8))
    assignment: dict[int, str] = {}
    # Greedy: hardest-to-place teams (fewest legal slots) first.
    remaining = [(team, grp) for team, grp, *_ in qualifiers]
    while remaining:
        # team with fewest legal remaining slots
        def legal_slots(grp):
            return [s for s in slots if _THIRD_SLOT_FACES[s] != grp]
        remaining.sort(key=lambda tg: len(legal_slots(tg[1])))
        team, grp = remaining.pop(0)
        legal = legal_slots(grp) or slots  # fall back if no legal slot
        slot = legal[0]
        assignment[slot] = team
        slots.remove(slot)
    return assignment


def _simulate_tournament_once(rng: np.random.Generator, counts: dict[str, dict[str, int]]) -> None:
    """Play one tournament and increment per-stage reach counts in place."""
    pos: dict[tuple, str] = {}
    third_standings = []

    for g in ALL_GROUPS:
        standings = _simulate_group_once(g, rng)
        winner, runner, third = standings[0][0], standings[1][0], standings[2]
        pos[("1", g)] = winner
        pos[("2", g)] = runner
        third_standings.append((third[0], g, third[1], third[2], third[3]))
        counts[winner]["win_group"] += 1
        counts[winner]["qualify"] += 1
        counts[runner]["qualify"] += 1

    third_assign = _assign_thirds(third_standings, rng)
    for slot, team in third_assign.items():
        pos[("3", slot)] = team

    # Build the 32-team R32 field in bracket order.
    def resolve(code: tuple) -> str:
        return pos[code]

    round_teams = []
    for a_code, b_code in R32_BRACKET:
        round_teams.append(resolve(a_code))
        round_teams.append(resolve(b_code))

    for t in round_teams:
        counts[t]["reach_r32"] += 1

    # Fold the bracket: R32 → R16 → QF → SF → Final.
    next_stage = ["reach_r16", "reach_qf", "reach_sf", "reach_final", "champion"]
    teams_in = round_teams
    for stage in next_stage:
        winners = []
        for i in range(0, len(teams_in), 2):
            w = _knockout_winner(teams_in[i], teams_in[i + 1], rng)
            winners.append(w)
            counts[w][stage] += 1
        teams_in = winners


# ── Public API ────────────────────────────────────────────────────────────────

def simulate_tournament(n_sims: int = 20_000,
                        rng: np.random.Generator | None = None) -> dict[str, dict[str, float]]:
    """
    Run `n_sims` full tournaments. Returns {team: {stage: probability}} for
    every stage in STAGES.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    counts: dict[str, dict[str, int]] = {
        t: {s: 0 for s in STAGES} for t in TEAMS
    }

    for _ in range(n_sims):
        _simulate_tournament_once(rng, counts)

    return {
        t: {s: counts[t][s] / n_sims for s in STAGES}
        for t in TEAMS
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def _print_table(probs: dict[str, dict[str, float]], top: int | None = None) -> None:
    rows = sorted(probs.items(), key=lambda kv: kv[1]["champion"], reverse=True)
    if top:
        rows = rows[:top]

    headers = ["Team", "Grp"] + [STAGE_LABELS[s] for s in STAGES]
    widths = [22, 4] + [8] * len(STAGES)

    def fmt_row(cells):
        return "  ".join(str(c).ljust(w) for c, w in zip(cells, widths))

    print(fmt_row(headers))
    print("-" * (sum(widths) + 2 * len(widths)))
    for team, p in rows:
        cells = [team, TEAMS[team]["group"]] + [f"{p[s]*100:.1f}%" for s in STAGES]
        print(fmt_row(cells))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="WC2026 full-tournament Monte Carlo (progression + title odds)"
    )
    parser.add_argument("--sims", type=int, default=20_000,
                        help="Number of full tournaments to simulate (default 20000)")
    parser.add_argument("--top", type=int, default=24,
                        help="Show only the top-N teams by title odds (default 24; 0 = all)")
    args = parser.parse_args()

    print(f"WC2026 Tournament Simulator — {args.sims:,} tournaments")
    print("Group stage (with host advantage) → R32 → R16 → QF → SF → Final\n")

    probs = simulate_tournament(n_sims=args.sims)
    _print_table(probs, top=(None if args.top == 0 else args.top))

    print("\nNote: knockout bracket is a fixed model bracket (see module docstring);")
    print("title odds for the leading contenders are robust to its exact slotting.")


if __name__ == "__main__":
    main()
