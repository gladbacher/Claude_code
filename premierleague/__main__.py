"""
CLI: project the Premier League season from bundled or fitted ratings.

    python -m premierleague --sims 10000
    python -m premierleague --csv path/to/E0.csv --xi 0.0019   # fit from real data
"""

from __future__ import annotations

import argparse

import numpy as np

from .ratings import BUNDLED
from .season import simulate_season, projected_table


def main() -> None:
    ap = argparse.ArgumentParser(description="Premier League season projection")
    ap.add_argument("--sims", type=int, default=10_000)
    ap.add_argument("--csv", type=str, default=None,
                    help="football-data.co.uk results CSV to fit ratings from")
    ap.add_argument("--xi", type=float, default=0.0,
                    help="time-decay rate per day when fitting (0 = equal weight)")
    args = ap.parse_args()

    if args.csv:
        from .data import load_results_csv
        from .fit import fit_ratings
        matches = load_results_csv(args.csv)
        print(f"Fitting Dixon-Coles ratings on {len(matches)} matches "
              f"(xi={args.xi})...")
        ratings = fit_ratings(matches, xi=args.xi)
        source = args.csv
    else:
        ratings = BUNDLED
        source = "bundled illustrative ratings"

    print(f"Premier League projection — {args.sims:,} seasons "
          f"(home adv ×{np.exp(ratings.home_adv):.2f}, rho {ratings.rho:+.3f})")
    print(f"Ratings: {source}\n")

    probs = simulate_season(ratings, n_sims=args.sims)
    table = projected_table(probs)

    hdr = f"{'#':>2}  {'Club':20} {'xPts':>5}  {'Title':>6}  {'Top4':>6}  {'Top6':>6}  {'Rel':>6}"
    print(hdr)
    print("-" * len(hdr))
    for i, (team, p) in enumerate(table, 1):
        print(f"{i:>2}  {team:20} {p['xpts']:5.1f}  {p['title']*100:5.1f}%  "
              f"{p['top4']*100:5.1f}%  {p['top6']*100:5.1f}%  {p['relegation']*100:5.1f}%")


if __name__ == "__main__":
    main()
