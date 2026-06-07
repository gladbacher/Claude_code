"""
WC2026 model command-line interface.

Usage examples:
    python -m wc2026 --match "England" "Ghana"
    python -m wc2026 --group L
    python -m wc2026 --all-groups
    python -m wc2026 --value "France" "Norway" --home-win 1.75 --draw 3.60 --away-win 4.50 --over25 1.80 --btts 1.65
    python -m wc2026 --fixtures L
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from typing import Optional

from .data import GROUPS, TEAMS, FIXTURES
from .model import simulate_match, simulate_group, find_value, AH_LINES


# ── Helpers ──────────────────────────────────────────────────────────────────

def _closest_team(name: str) -> str | None:
    matches = difflib.get_close_matches(name, TEAMS.keys(), n=1, cutoff=0.6)
    return matches[0] if matches else None


def _validate_team(name: str) -> str:
    if name in TEAMS:
        return name
    suggestion = _closest_team(name)
    hint = f" Did you mean '{suggestion}'?" if suggestion else ""
    print(f"Unknown team '{name}'.{hint}")
    print(f"Available teams: {', '.join(sorted(TEAMS.keys()))}")
    sys.exit(1)


def _pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def _odds(p: float) -> str:
    return f"{1/p:.2f}" if p > 0 else "∞"


# ── Display functions ─────────────────────────────────────────────────────────

def display_match(home: str, away: str, n_sims: int = 50_000) -> None:
    """Print full match prediction."""
    result = simulate_match(home, away, n_sims=n_sims)

    print(f"\n{'═'*56}")
    print(f"  {home}  vs  {away}")
    print(f"  λ {home}: {result['lambda_home']:.2f}  |  λ {away}: {result['lambda_away']:.2f}")
    print(f"{'═'*56}")

    print(f"\n  Match Result")
    print(f"  {'Home win':20s} {_pct(result['home_win']):>7}  (fair odds {_odds(result['home_win'])})")
    print(f"  {'Draw':20s} {_pct(result['draw']):>7}  (fair odds {_odds(result['draw'])})")
    print(f"  {'Away win':20s} {_pct(result['away_win']):>7}  (fair odds {_odds(result['away_win'])})")

    print(f"\n  Goals Markets")
    for line, key in [(0.5, "over_05"), (1.5, "over_15"), (2.5, "over_25"),
                      (3.5, "over_35"), (4.5, "over_45")]:
        p_over = result[key]
        p_under = 1.0 - p_over
        print(f"  {'Over '+str(line):12s}  {_pct(p_over):>7}  ({_odds(p_over)})  "
              f"Under: {_pct(p_under):>7}  ({_odds(p_under)})")

    print(f"\n  Both Teams To Score")
    print(f"  {'Yes':12s}  {_pct(result['btts']):>7}  ({_odds(result['btts'])})")
    print(f"  {'No':12s}  {_pct(1-result['btts']):>7}  ({_odds(1-result['btts'])})")

    print(f"\n  Asian Handicap (home perspective)")
    print(f"  {'Line':>6}  {'Home':>7}  {'Push':>7}  {'Away':>7}")
    for line in AH_LINES:
        hc = result['ah_home'][line]
        pu = result['ah_push'][line]
        ac = result['ah_away'][line]
        marker = " ◄" if abs(hc - 0.5) < 0.06 else ""
        print(f"  {line:>+6.2f}  {_pct(hc):>7}  {_pct(pu):>7}  {_pct(ac):>7}{marker}")

    print(f"\n  Top Scorelines")
    sorted_grid = sorted(result['score_grid'].items(), key=lambda x: x[1], reverse=True)
    for (h, a), p in sorted_grid[:9]:
        print(f"  {h}-{a}  {_pct(p)}")
    print()


def display_group(group: str, n_sims: int = 20_000) -> None:
    """Print group stage qualification probabilities."""
    if group not in GROUPS:
        print(f"Unknown group '{group}'. Valid groups: {', '.join(sorted(GROUPS.keys()))}")
        sys.exit(1)

    result = simulate_group(group, n_sims=n_sims)
    teams = GROUPS[group]

    print(f"\n{'═'*56}")
    print(f"  Group {group} — Qualification Probabilities ({n_sims:,} sims)")
    print(f"{'═'*56}")
    print(f"  {'Team':25s} {'Qual%':>7}  {'Win%':>6}  {'3rd%':>6}  {'Avg Pts':>8}")
    print(f"  {'─'*52}")

    for team in sorted(teams, key=lambda t: result['qualification'][t], reverse=True):
        q = result['qualification'][team]
        w = result['win_group'][team]
        t3 = result['third_place'][team]
        pts = result['points_avg'][team]
        print(f"  {team:25s} {_pct(q):>7}  {_pct(w):>6}  {_pct(t3):>6}  {pts:>8.2f}")
    print()


def display_value(
    home: str,
    away: str,
    home_win_odds: Optional[float] = None,
    draw_odds: Optional[float] = None,
    away_win_odds: Optional[float] = None,
    over25_odds: Optional[float] = None,
    btts_odds: Optional[float] = None,
    n_sims: int = 50_000,
    vig: float = 0.047,
) -> None:
    """Print value bets for a specific match given market odds."""
    result = simulate_match(home, away, n_sims=n_sims)

    print(f"\n{'═'*60}")
    print(f"  Value Analysis: {home} vs {away}")
    print(f"{'═'*60}")
    print(f"  {'Market':20s} {'Model%':>7}  {'Mkt Odds':>9}  {'Edge':>7}  {'Value?':>7}")
    print(f"  {'─'*56}")

    checks = [
        ("Home win", result["home_win"], home_win_odds),
        ("Draw", result["draw"], draw_odds),
        ("Away win", result["away_win"], away_win_odds),
        ("Over 2.5", result["over_25"], over25_odds),
        ("BTTS Yes", result["btts"], btts_odds),
    ]

    found_value = False
    for label, model_p, odds in checks:
        if odds is None:
            continue
        edge, is_value = find_value(model_p, odds, vig=vig)
        flag = "✓ VALUE" if is_value else ""
        print(f"  {label:20s} {_pct(model_p):>7}  {odds:>9.2f}  {edge:>+7.3f}  {flag}")
        if is_value:
            found_value = True

    if not found_value:
        print(f"\n  No value bets found at current odds (min edge {vig:.1%} assumed vig).")
    print()


def display_fixtures(group: str) -> None:
    """Print fixtures for a group."""
    if group not in GROUPS:
        print(f"Unknown group '{group}'. Valid: {', '.join(sorted(GROUPS.keys()))}")
        sys.exit(1)

    matches = [(h, a, md, dt) for h, a, md, dt in FIXTURES
               if TEAMS[h]["group"] == group]

    print(f"\nGroup {group} fixtures:")
    for h, a, md, dt in sorted(matches, key=lambda x: (x[2], x[3])):
        print(f"  MD{md}  {dt}  {h} vs {a}")
    print()


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="wc2026",
        description="WC2026 group stage betting model",
    )

    parser.add_argument("--match", nargs=2, metavar=("HOME", "AWAY"),
                        help="Predict a single match")
    parser.add_argument("--group", metavar="G",
                        help="Simulate a group (A-L)")
    parser.add_argument("--all-groups", action="store_true",
                        help="Simulate all 12 groups")
    parser.add_argument("--fixtures", metavar="G",
                        help="Show fixtures for a group")
    parser.add_argument("--value", nargs=2, metavar=("HOME", "AWAY"),
                        help="Find value bets (supply odds with flags below)")
    parser.add_argument("--home-win", type=float, metavar="ODDS")
    parser.add_argument("--draw", type=float, metavar="ODDS")
    parser.add_argument("--away-win", type=float, metavar="ODDS")
    parser.add_argument("--over25", type=float, metavar="ODDS")
    parser.add_argument("--btts", type=float, metavar="ODDS")
    parser.add_argument("--sims", type=int, default=50_000,
                        help="Monte Carlo simulations (default 50000)")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON instead of formatted table")

    args = parser.parse_args()

    if args.match:
        home, away = args.match
        home = _validate_team(home)
        away = _validate_team(away)
        if args.json:
            result = simulate_match(home, away, n_sims=args.sims)
            # Convert tuple keys in score_grid to strings
            result["score_grid"] = {f"{h}-{a}": p for (h, a), p in result["score_grid"].items()}
            print(json.dumps(result, indent=2))
        else:
            display_match(home, away, n_sims=args.sims)

    elif args.group:
        display_group(args.group.upper(), n_sims=args.sims)

    elif args.all_groups:
        for g in sorted(GROUPS.keys()):
            display_group(g, n_sims=args.sims)

    elif args.fixtures:
        display_fixtures(args.fixtures.upper())

    elif args.value:
        home, away = args.value
        home = _validate_team(home)
        away = _validate_team(away)
        display_value(
            home, away,
            home_win_odds=args.home_win,
            draw_odds=args.draw,
            away_win_odds=args.away_win,
            over25_odds=args.over25,
            btts_odds=args.btts,
            n_sims=args.sims,
        )

    else:
        parser.print_help()
