"""
Generate a single-file HTML prediction report for all WC2026 group stage matches.

Usage:
    python -m wc2026.report [--sims N] [--out PATH]
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from .data import GROUPS, FIXTURES, TEAMS
from .model import simulate_match, simulate_group, scorer_probs, get_lambdas


# ── Helpers ───────────────────────────────────────────────────────────────────

def _pct(v: float) -> str:
    return f"{v*100:.1f}%"

def _odds(p: float) -> str:
    return f"{1/p:.2f}" if p > 0.001 else "—"

def _bar(p: float, width: int = 80) -> str:
    filled = round(p * width)
    return "█" * filled + "░" * (width - filled)

def _ah_line(result: dict) -> float:
    """Return the AH line where home cover probability is closest to 50%."""
    from .model import AH_LINES
    return min(AH_LINES, key=lambda l: abs(result["ah_home"][l] - 0.50))


# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #0f1117;
  color: #e0e0e0;
  font-size: 14px;
  line-height: 1.5;
}
h1 { color: #ff6b2b; font-size: 28px; font-weight: 800; letter-spacing: -0.5px; }
h2 { color: #ff6b2b; font-size: 18px; font-weight: 700; margin-bottom: 4px; }
.header {
  padding: 24px 32px 16px;
  border-bottom: 2px solid #1e2130;
  display: flex; align-items: center; gap: 16px;
}
.subtitle { color: #888; font-size: 13px; margin-top: 4px; }
.tabs {
  display: flex; flex-wrap: wrap; gap: 4px;
  padding: 16px 32px 0;
  border-bottom: 2px solid #1e2130;
  position: sticky; top: 0; background: #0f1117; z-index: 10;
}
.tab {
  padding: 8px 18px; border-radius: 6px 6px 0 0;
  background: #1a1d28; color: #888; cursor: pointer;
  border: 1px solid #1e2130; border-bottom: none;
  font-weight: 600; font-size: 13px; transition: all 0.15s;
}
.tab:hover { background: #222636; color: #ccc; }
.tab.active { background: #ff6b2b; color: #fff; border-color: #ff6b2b; }
.group-section { display: none; padding: 24px 32px; }
.group-section.active { display: block; }
.group-header {
  display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px;
}
.team-chip {
  background: #1a1d28; border: 1px solid #2a2d3e;
  padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600;
}
.matches-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(680px, 1fr));
  gap: 16px;
}
.match-card {
  background: #15181f; border: 1px solid #1e2130;
  border-radius: 12px; overflow: hidden;
}
.match-header {
  background: #1a1d28; padding: 12px 20px;
  display: flex; justify-content: space-between; align-items: center;
}
.match-teams {
  font-size: 17px; font-weight: 700; color: #fff; letter-spacing: -0.3px;
}
.vs { color: #555; font-size: 13px; margin: 0 6px; }
.match-meta { color: #666; font-size: 12px; }
.match-body { padding: 16px 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.section-title {
  font-size: 11px; font-weight: 700; color: #ff6b2b;
  text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px;
}
.market-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 5px 0; border-bottom: 1px solid #1a1d28;
}
.market-row:last-child { border-bottom: none; }
.market-label { color: #aaa; font-size: 13px; }
.market-prob { font-weight: 700; font-size: 14px; color: #fff; }
.market-odds { color: #888; font-size: 12px; margin-left: 6px; }
.prob-bar-container { position: relative; height: 6px; background: #1e2130; border-radius: 3px; margin-top: 10px; overflow: hidden; }
.prob-bar-home { position: absolute; left: 0; top: 0; height: 100%; background: #3b82f6; border-radius: 3px 0 0 3px; }
.prob-bar-draw { position: absolute; top: 0; height: 100%; background: #888; }
.prob-bar-away { position: absolute; right: 0; top: 0; height: 100%; background: #ef4444; border-radius: 0 3px 3px 0; }
.outcome-labels {
  display: flex; justify-content: space-between; margin-top: 4px; font-size: 11px; color: #666;
}
.lambda-row { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.lambda-chip {
  background: #1e2130; border-radius: 6px; padding: 4px 10px;
  font-size: 12px; color: #aaa;
}
.lambda-chip span { color: #ff6b2b; font-weight: 700; }
.scorer-list { list-style: none; }
.scorer-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 4px 0; border-bottom: 1px solid #1a1d28;
}
.scorer-item:last-child { border-bottom: none; }
.scorer-name { font-size: 13px; color: #ccc; }
.scorer-bar-wrap { flex: 1; margin: 0 10px; height: 4px; background: #1e2130; border-radius: 2px; }
.scorer-bar { height: 100%; background: #ff6b2b; border-radius: 2px; }
.scorer-prob { font-size: 12px; font-weight: 700; color: #ff6b2b; min-width: 36px; text-align: right; }
.home-scorers { border-right: 1px solid #1e2130; padding-right: 16px; }
.ah-badge {
  display: inline-block; background: #1e2130; border-radius: 6px;
  padding: 3px 10px; font-size: 12px; color: #aaa; margin-top: 4px;
}
.ah-badge span { color: #fff; font-weight: 700; }
.goals-row { display: flex; gap: 8px; flex-wrap: wrap; }
.ou-chip {
  background: #1e2130; border-radius: 6px; padding: 4px 10px;
  font-size: 12px;
}
.ou-chip .label { color: #888; }
.ou-chip .val { color: #fff; font-weight: 700; margin-left: 4px; }
.ou-chip .fair { color: #666; font-size: 11px; margin-left: 3px; }
.btts-row { margin-top: 8px; display: flex; gap: 8px; }
.btts-chip {
  background: #1e2130; border-radius: 6px; padding: 4px 10px; font-size: 12px;
}
.btts-chip .label { color: #888; }
.btts-chip .val { font-weight: 700; margin-left: 4px; }
.green { color: #22c55e; }
.red { color: #ef4444; }
.qual-section { margin-top: 20px; }
.qual-table { width: 100%; border-collapse: collapse; }
.qual-table th {
  background: #1a1d28; padding: 8px 12px; text-align: left;
  font-size: 11px; font-weight: 700; color: #ff6b2b;
  text-transform: uppercase; letter-spacing: 0.8px;
}
.qual-table td { padding: 8px 12px; border-bottom: 1px solid #1a1d28; font-size: 13px; }
.qual-table tr:last-child td { border-bottom: none; }
.qual-table tr:hover td { background: #1a1d28; }
.qual-bar { height: 4px; background: #1e2130; border-radius: 2px; margin-top: 4px; }
.qual-bar-fill { height: 100%; background: #3b82f6; border-radius: 2px; }
.footer { padding: 24px 32px; color: #444; font-size: 12px; border-top: 1px solid #1e2130; margin-top: 32px; }
@media (max-width: 768px) {
  .matches-grid { grid-template-columns: 1fr; }
  .match-body { grid-template-columns: 1fr; }
  .home-scorers { border-right: none; padding-right: 0; }
  .tabs { padding: 12px 16px 0; }
  .group-section { padding: 16px; }
  .header { padding: 16px; }
}
"""

# ── JS ────────────────────────────────────────────────────────────────────────

JS = """
function showGroup(g) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.group-section').forEach(s => s.classList.remove('active'));
  document.getElementById('tab-' + g).classList.add('active');
  document.getElementById('group-' + g).classList.add('active');
}
window.addEventListener('DOMContentLoaded', () => {
  const first = document.querySelector('.tab');
  if (first) first.click();
});
"""


# ── Card builder ──────────────────────────────────────────────────────────────

def _match_card(home: str, away: str, date: str, matchday: int, n_sims: int) -> str:
    res = simulate_match(home, away, n_sims=n_sims)
    lh, la = res["lambda_home"], res["lambda_away"]

    hw, dr, aw = res["home_win"], res["draw"], res["away_win"]
    o25 = res["over_25"]
    u25 = 1 - o25
    btts = res["btts"]
    ah = _ah_line(res)

    h_scorers = scorer_probs(home, lh)
    a_scorers = scorer_probs(away, la)

    # Probability bar widths
    bar_h = round(hw * 100)
    bar_d = round(dr * 100)
    bar_a = round(aw * 100)
    bar_d_left = bar_h

    def scorer_rows(players: list[dict]) -> str:
        rows = ""
        for p in players[:4]:
            w = round(p["prob"] * 100)
            rows += f"""
            <li class="scorer-item">
              <span class="scorer-name">{p['name']}</span>
              <div class="scorer-bar-wrap"><div class="scorer-bar" style="width:{w}%"></div></div>
              <span class="scorer-prob">{_pct(p['prob'])}</span>
            </li>"""
        return rows

    ou_chips = ""
    for line, key in [(0.5, "over_05"), (1.5, "over_15"), (2.5, "over_25"), (3.5, "over_35"), (4.5, "over_45")]:
        p = res[key]
        ou_chips += f"""<div class="ou-chip">
          <span class="label">O{line}</span>
          <span class="val">{_pct(p)}</span>
          <span class="fair">{_odds(p)}</span>
        </div>"""

    return f"""
<div class="match-card">
  <div class="match-header">
    <div>
      <div class="match-teams">
        {home} <span class="vs">vs</span> {away}
      </div>
    </div>
    <div class="match-meta">MD{matchday} · {date}</div>
  </div>
  <div class="match-body">
    <!-- Left column -->
    <div>
      <div class="lambda-row">
        <div class="lambda-chip">λ {home}: <span>{lh:.2f}</span></div>
        <div class="lambda-chip">λ {away}: <span>{la:.2f}</span></div>
      </div>

      <div class="section-title">Match Result</div>
      <div class="market-row">
        <span class="market-label">{home}</span>
        <span><span class="market-prob">{_pct(hw)}</span><span class="market-odds">({_odds(hw)})</span></span>
      </div>
      <div class="market-row">
        <span class="market-label">Draw</span>
        <span><span class="market-prob">{_pct(dr)}</span><span class="market-odds">({_odds(dr)})</span></span>
      </div>
      <div class="market-row">
        <span class="market-label">{away}</span>
        <span><span class="market-prob">{_pct(aw)}</span><span class="market-odds">({_odds(aw)})</span></span>
      </div>
      <div class="prob-bar-container" style="margin-top:10px">
        <div class="prob-bar-home" style="width:{bar_h}%"></div>
        <div class="prob-bar-draw" style="left:{bar_d_left}%;width:{bar_d}%"></div>
        <div class="prob-bar-away" style="width:{bar_a}%"></div>
      </div>
      <div class="outcome-labels">
        <span>{home}</span><span>Draw</span><span>{away}</span>
      </div>

      <div style="margin-top:14px">
        <div class="section-title">Goals Markets</div>
        <div class="goals-row">{ou_chips}</div>
        <div class="btts-row">
          <div class="btts-chip"><span class="label">BTTS Yes</span><span class="val {'green' if btts>0.5 else ''}">{_pct(btts)}</span></div>
          <div class="btts-chip"><span class="label">BTTS No</span><span class="val {'green' if btts<=0.5 else ''}">{_pct(1-btts)}</span></div>
        </div>
        <div style="margin-top:8px">
          <div class="ah-badge">Best AH line: <span>{ah:+.2f}</span>
            · Home {_pct(res['ah_home'][ah])}
            · Away {_pct(res['ah_away'][ah])}</div>
        </div>
      </div>
    </div>

    <!-- Right column: scorers -->
    <div>
      <div class="section-title">Anytime Scorers — {home}</div>
      <ul class="scorer-list">{scorer_rows(h_scorers)}</ul>

      <div class="section-title" style="margin-top:14px">Anytime Scorers — {away}</div>
      <ul class="scorer-list">{scorer_rows(a_scorers)}</ul>
    </div>
  </div>
</div>"""


# ── Qualification table ───────────────────────────────────────────────────────

def _qual_table(group: str, n_sims: int) -> str:
    from .data import GROUPS
    result = simulate_group(group, n_sims=n_sims)
    teams = sorted(GROUPS[group], key=lambda t: result["qualification"][t], reverse=True)

    rows = ""
    for rank, team in enumerate(teams, 1):
        q = result["qualification"][team]
        w = result["win_group"][team]
        t3 = result["third_place"][team]
        pts = result["points_avg"][team]
        bar_w = round(q * 100)
        rows += f"""
        <tr>
          <td>{rank}</td>
          <td><strong>{team}</strong></td>
          <td>
            <div style="font-weight:700">{_pct(q)}</div>
            <div class="qual-bar"><div class="qual-bar-fill" style="width:{bar_w}%"></div></div>
          </td>
          <td>{_pct(w)}</td>
          <td style="color:#888">{_pct(t3)}</td>
          <td>{pts:.2f}</td>
        </tr>"""

    return f"""
<div class="qual-section">
  <div class="section-title">Group Qualification Probabilities ({n_sims:,} sims)</div>
  <table class="qual-table">
    <thead>
      <tr>
        <th>#</th><th>Team</th><th>Qualify</th><th>Win Group</th><th>3rd Place</th><th>Avg Pts</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</div>"""


# ── Full report ───────────────────────────────────────────────────────────────

def generate_report(n_sims: int = 10_000, output: Path | None = None) -> Path:
    """Generate HTML report for all 72 group stage matches."""
    if output is None:
        output = Path("wc2026_predictions.html")

    groups = sorted(GROUPS.keys())

    # Build tab bar
    tabs = ""
    for g in groups:
        teams = GROUPS[g]
        tab_title = f"Group {g}"
        tabs += f'<button class="tab" id="tab-{g}" onclick="showGroup(\'{g}\')">{tab_title}</button>\n'

    # Build group sections
    sections = ""
    total = sum(1 for _ in FIXTURES)
    done = 0
    for g in groups:
        teams = GROUPS[g]
        fixtures_in_group = [(h, a, md, dt) for h, a, md, dt in FIXTURES
                             if TEAMS[h]["group"] == g]

        chips = "".join(f'<div class="team-chip">{t}</div>' for t in teams)
        cards = ""
        for h, a, md, dt in sorted(fixtures_in_group, key=lambda x: (x[2], x[3])):
            print(f"  Simulating {h} vs {a}...", flush=True)
            cards += _match_card(h, a, dt, md, n_sims)
            done += 1
        qual = _qual_table(g, n_sims)

        sections += f"""
<div class="group-section" id="group-{g}">
  <h2>Group {g}</h2>
  <div class="group-header">{chips}</div>
  {qual}
  <div style="margin-top:20px">
    <div class="section-title" style="font-size:13px;margin-bottom:12px">Match Predictions</div>
    <div class="matches-grid">{cards}</div>
  </div>
</div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WC2026 Group Stage Predictions</title>
  <style>{CSS}</style>
</head>
<body>

<div class="header">
  <div>
    <h1>⚽ WC2026 Group Stage Predictions</h1>
    <div class="subtitle">
      Dixon-Coles Poisson model · {n_sims:,} Monte Carlo simulations per match ·
      Data: ScoutingStats.ai · Generated {__import__('datetime').date.today()}
    </div>
  </div>
</div>

<div class="tabs">{tabs}</div>

{sections}

<div class="footer">
  Model: Dixon-Coles Poisson (ρ = −0.13) · Maher expected goals parameterisation ·
  Player anytime scorer probabilities scaled by match λ.
  [SS] = ScoutingStats.ai verified · [est] = estimated from general knowledge.
  <strong>Not financial advice. Bet responsibly.</strong>
</div>

<script>{JS}</script>
</body>
</html>"""

    output.write_text(html, encoding="utf-8")
    print(f"\nReport saved → {output.resolve()}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate WC2026 HTML prediction report")
    parser.add_argument("--sims", type=int, default=10_000)
    parser.add_argument("--out", type=Path, default=Path("wc2026_predictions.html"))
    args = parser.parse_args()
    print(f"Generating report ({args.sims:,} sims per match)...")
    generate_report(n_sims=args.sims, output=args.out)


if __name__ == "__main__":
    main()
