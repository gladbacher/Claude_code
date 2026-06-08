"""
Compare model probabilities against average bookmaker 1X2 odds.

Usage:
  python -m wc2026.compare [--sims N] [--min-edge FLOAT] [--group X] [--html FILE]

Outputs a ranked table of value bets (edge > min_edge after vig stripping).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .data import FIXTURES
from .data.odds import MARKET_ODDS
from .model import simulate_match, find_value

# American-odds to decimal helper (already stored as decimal in odds.py)
VIG: float = 0.047
DEFAULT_SIMS: int = 10_000
MIN_EDGE: float = 0.03  # 3% minimum edge to flag as value


def _implied(dec_odds: float) -> float:
    return 1.0 / dec_odds


def compare_all(
    n_sims: int = DEFAULT_SIMS,
    min_edge: float = MIN_EDGE,
    group_filter: str | None = None,
) -> list[dict]:
    """
    Simulate all 72 fixtures and compare model probs to market implied probs.

    Returns a list of dicts, one per (match, market) combination where edge > min_edge,
    sorted by edge descending.
    """
    from .data import TEAMS

    results = []

    fixtures = FIXTURES
    if group_filter:
        fixtures = [f for f in fixtures if TEAMS[f[0]]["group"] == group_filter.upper()]

    for home, away, matchday, date in fixtures:
        key = (home, away)
        if key not in MARKET_ODDS:
            continue

        odds = MARKET_ODDS[key]
        sim = simulate_match(home, away, n_sims=n_sims)

        markets = [
            ("Home Win",  sim["home_win"],  odds["home"]),
            ("Draw",      sim["draw"],       odds["draw"]),
            ("Away Win",  sim["away_win"],   odds["away"]),
        ]

        for label, model_p, dec_odds in markets:
            edge, is_value = find_value(model_p, dec_odds, vig=VIG)
            implied_p = _implied(dec_odds)
            results.append({
                "date":      date,
                "matchday":  matchday,
                "home":      home,
                "away":      away,
                "group":     TEAMS[home]["group"],
                "market":    label,
                "model_p":   round(model_p, 4),
                "implied_p": round(implied_p, 4),
                "dec_odds":  dec_odds,
                "edge":      round(edge, 4),
                "value":     is_value,
                "src":       odds.get("src", "?"),
                "lam_home":  round(sim["lambda_home"], 2),
                "lam_away":  round(sim["lambda_away"], 2),
            })

    results.sort(key=lambda r: r["edge"], reverse=True)
    return results


def _pct(f: float) -> str:
    return f"{f * 100:.1f}%"


def print_table(results: list[dict], min_edge: float = MIN_EDGE) -> None:
    value_bets = [r for r in results if r["edge"] >= min_edge]

    print(f"\n{'='*100}")
    print(f"  WC2026 MODEL vs MARKET  —  {len(value_bets)} value bets (edge ≥ {min_edge*100:.0f}%)")
    print(f"{'='*100}")
    print(f"{'Date':<12} {'Grp':<4} {'Match':<40} {'Market':<10} {'Model':>6} {'Mkt':>6} {'Odds':>6} {'Edge':>7}  Src")
    print(f"{'-'*100}")

    for r in value_bets:
        match_str = f"{r['home']} v {r['away']}"
        edge_star = "★" if r["edge"] >= 0.08 else ("·" if r["edge"] >= 0.05 else " ")
        print(
            f"{r['date']:<12} {r['group']:<4} {match_str:<40} {r['market']:<10} "
            f"{_pct(r['model_p']):>6} {_pct(r['implied_p']):>6} {r['dec_odds']:>6.2f} "
            f"{_pct(r['edge']):>7}  [{r['src']}] {edge_star}"
        )

    print(f"\n★ = edge ≥ 8%  · = edge ≥ 5%  [C] = confirmed odds  [E] = estimated odds")

    # Summary by group
    print(f"\n{'─'*60}")
    print("  FULL MODEL vs MARKET SUMMARY (all 72 × 3 markets)")
    print(f"{'─'*60}")
    print(f"{'Date':<12} {'Match':<40} λH   λA  | H-Win%  Draw%  A-Win%")
    print(f"{'-'*60}")

    seen = set()
    for r in results:
        k = (r["home"], r["away"])
        if k in seen:
            continue
        seen.add(k)
        home_r = next(x for x in results if x["home"] == r["home"] and x["away"] == r["away"] and x["market"] == "Home Win")
        draw_r = next(x for x in results if x["home"] == r["home"] and x["away"] == r["away"] and x["market"] == "Draw")
        away_r = next(x for x in results if x["home"] == r["home"] and x["away"] == r["away"] and x["market"] == "Away Win")

        def fmt(row: dict) -> str:
            star = "▲" if row["edge"] >= min_edge else " "
            return f"{_pct(row['model_p'])}({_pct(row['implied_p'])}){star}"

        match_str = f"{r['home']} v {r['away']}"
        print(
            f"{r['date']:<12} {match_str:<40} {r['lam_home']:.2f} {r['lam_away']:.2f} | "
            f"{fmt(home_r):>14} {fmt(draw_r):>14} {fmt(away_r):>14}"
        )


def write_html(results: list[dict], output: Path, min_edge: float = MIN_EDGE) -> None:
    """Generate a standalone HTML value-bet report."""
    value_bets = [r for r in results if r["edge"] >= min_edge]

    rows_value = ""
    for r in value_bets:
        edge_class = "edge-high" if r["edge"] >= 0.08 else ("edge-med" if r["edge"] >= 0.05 else "edge-low")
        src_badge = f'<span class="src-{r["src"].lower()}">[{r["src"]}]</span>'
        rows_value += (
            f'<tr class="{edge_class}">'
            f'<td>{r["date"]}</td><td>{r["group"]}</td>'
            f'<td>{r["home"]} v {r["away"]}</td>'
            f'<td>{r["market"]}</td>'
            f'<td>{_pct(r["model_p"])}</td>'
            f'<td>{_pct(r["implied_p"])}</td>'
            f'<td>{r["dec_odds"]:.2f}</td>'
            f'<td class="edge-val">{_pct(r["edge"])}</td>'
            f'<td>{src_badge}</td>'
            f'</tr>\n'
        )

    # Full summary table
    rows_full = ""
    seen: set = set()
    for r in results:
        k = (r["home"], r["away"])
        if k in seen:
            continue
        seen.add(k)
        home_r = next(x for x in results if x["home"] == r["home"] and x["away"] == r["away"] and x["market"] == "Home Win")
        draw_r = next(x for x in results if x["home"] == r["home"] and x["away"] == r["away"] and x["market"] == "Draw")
        away_r = next(x for x in results if x["home"] == r["home"] and x["away"] == r["away"] and x["market"] == "Away Win")

        def cell(row: dict) -> str:
            cls = "value-cell" if row["edge"] >= min_edge else ""
            return f'<td class="{cls}">{_pct(row["model_p"])}<br><small>mkt {_pct(row["implied_p"])}</small></td>'

        match_str = f"{r['home']} v {r['away']}"
        src = MARKET_ODDS.get((r["home"], r["away"]), {}).get("src", "?")
        src_badge = f'<span class="src-{src.lower()}">[{src}]</span>'
        rows_full += (
            f'<tr><td>{r["date"]}</td><td>{r["group"]}</td>'
            f'<td>{match_str} {src_badge}</td>'
            f'<td>{r["lam_home"]:.2f}</td><td>{r["lam_away"]:.2f}</td>'
            f'{cell(home_r)}{cell(draw_r)}{cell(away_r)}</tr>\n'
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>WC2026 Model vs Market</title>
<style>
  body{{font-family:system-ui,sans-serif;max-width:1400px;margin:2rem auto;padding:0 1rem;background:#0f172a;color:#e2e8f0}}
  h1{{color:#f8fafc;font-size:1.6rem;margin-bottom:0.3rem}}
  p.sub{{color:#94a3b8;margin-top:0;font-size:.9rem}}
  h2{{color:#cbd5e1;font-size:1.1rem;margin:2rem 0 .5rem}}
  table{{width:100%;border-collapse:collapse;font-size:.85rem}}
  th{{background:#1e293b;color:#94a3b8;text-align:left;padding:.5rem .6rem;position:sticky;top:0}}
  td{{padding:.4rem .6rem;border-bottom:1px solid #1e293b}}
  tr:hover td{{background:#1e293b80}}
  .edge-high td{{background:#16221440;border-left:3px solid #22c55e}}
  .edge-med  td{{background:#1c1e1440;border-left:3px solid #eab308}}
  .edge-low  td{{background:#1e1a1440;border-left:3px solid #3b82f6}}
  .edge-val{{font-weight:700;color:#22c55e}}
  .edge-med .edge-val{{color:#eab308}}
  .edge-low .edge-val{{color:#3b82f6}}
  .value-cell{{background:#162214;font-weight:600;color:#86efac}}
  .src-c{{color:#22c55e;font-size:.75rem}}
  .src-e{{color:#94a3b8;font-size:.75rem}}
  small{{color:#64748b}}
  .legend{{display:flex;gap:1.5rem;font-size:.8rem;margin:.5rem 0 1rem;color:#94a3b8}}
  .legend span{{display:flex;align-items:center;gap:.3rem}}
  .dot{{width:10px;height:10px;border-radius:50%;display:inline-block}}
</style>
</head>
<body>
<h1>⚽ WC2026 — Model vs Market</h1>
<p class="sub">Dixon-Coles Poisson + shrinkage + FIFA ranking adjustment + host advantage &nbsp;|&nbsp;
Vig stripped at {VIG*100:.1f}% &nbsp;|&nbsp; Edge = model prob − implied prob − vig</p>

<div class="legend">
  <span><span class="dot" style="background:#22c55e"></span> Edge ≥ 8% (★)</span>
  <span><span class="dot" style="background:#eab308"></span> Edge 5–8%</span>
  <span><span class="dot" style="background:#3b82f6"></span> Edge 3–5%</span>
  <span><span class="src-c">[C]</span> = confirmed market odds</span>
  <span><span class="src-e">[E]</span> = estimated odds</span>
</div>

<h2>Value Bets (edge ≥ {min_edge*100:.0f}%) — {len(value_bets)} bets across {len(seen)} matches</h2>
<table>
<thead><tr>
  <th>Date</th><th>Grp</th><th>Match</th><th>Market</th>
  <th>Model</th><th>Market Implied</th><th>Odds</th><th>Edge</th><th>Src</th>
</tr></thead>
<tbody>{rows_value}</tbody>
</table>

<h2>Full Summary — All Fixtures</h2>
<table>
<thead><tr>
  <th>Date</th><th>Grp</th><th>Match</th><th>λH</th><th>λA</th>
  <th>Home Win<br><small>model(mkt)</small></th>
  <th>Draw<br><small>model(mkt)</small></th>
  <th>Away Win<br><small>model(mkt)</small></th>
</tr></thead>
<tbody>{rows_full}</tbody>
</table>
</body>
</html>"""

    output.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare WC2026 model vs market odds")
    parser.add_argument("--sims", type=int, default=DEFAULT_SIMS)
    parser.add_argument("--min-edge", type=float, default=MIN_EDGE)
    parser.add_argument("--group", type=str, default=None, help="Filter to one group (A-L)")
    parser.add_argument("--html", type=str, default=None, help="Write HTML report to this path")
    args = parser.parse_args()

    print(f"Running {args.sims:,} simulations per match…", file=sys.stderr)
    results = compare_all(n_sims=args.sims, min_edge=args.min_edge, group_filter=args.group)
    print_table(results, min_edge=args.min_edge)

    if args.html:
        out = Path(args.html)
        write_html(results, out, min_edge=args.min_edge)
        print(f"\nHTML report → {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
