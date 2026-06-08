"""
WC2026 per-match HTML prediction report generator.

Generates a single self-contained HTML file with one detailed match card per
group-stage fixture (72 total), grouped by group (A–L) with sticky tab navigation.

Usage:
    python -m wc2026.report_match --sims 10000 --out wc2026_match_pages.html
"""

from __future__ import annotations

import argparse
import html as html_mod
import math
import sys
from typing import Any

from .data import GROUPS, FIXTURES, TEAMS
from .data.odds import MARKET_ODDS
from .model import simulate_match, scorer_probs, AH_LINES, simulate_group

# ── Country flag emoji map ──────────────────────────────────────────────────
FLAG: dict[str, str] = {
    "Mexico":                   "🇲🇽",
    "South Africa":             "🇿🇦",
    "Korea Republic":           "🇰🇷",
    "Czech Republic":           "🇨🇿",
    "Canada":                   "🇨🇦",
    "Qatar":                    "🇶🇦",
    "Switzerland":              "🇨🇭",
    "Bosnia and Herzegovina":   "🇧🇦",
    "Brazil":                   "🇧🇷",
    "Morocco":                  "🇲🇦",
    "Haiti":                    "🇭🇹",
    "Scotland":                 "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "United States":            "🇺🇸",
    "Paraguay":                 "🇵🇾",
    "Türkiye":                  "🇹🇷",
    "Australia":                "🇦🇺",
    "Germany":                  "🇩🇪",
    "Curacao":                  "🇨🇼",
    "Côte d'Ivoire":            "🇨🇮",
    "Ecuador":                  "🇪🇨",
    "Sweden":                   "🇸🇪",
    "Netherlands":              "🇳🇱",
    "Japan":                    "🇯🇵",
    "Tunisia":                  "🇹🇳",
    "Belgium":                  "🇧🇪",
    "Egypt":                    "🇪🇬",
    "Iran":                     "🇮🇷",
    "New Zealand":              "🇳🇿",
    "Spain":                    "🇪🇸",
    "Saudi Arabia":             "🇸🇦",
    "Cape Verde Islands":       "🇨🇻",
    "Uruguay":                  "🇺🇾",
    "France":                   "🇫🇷",
    "Norway":                   "🇳🇴",
    "Iraq":                     "🇮🇶",
    "Senegal":                  "🇸🇳",
    "Argentina":                "🇦🇷",
    "Algeria":                  "🇩🇿",
    "Austria":                  "🇦🇹",
    "Jordan":                   "🇯🇴",
    "Portugal":                 "🇵🇹",
    "Colombia":                 "🇨🇴",
    "Congo DR":                 "🇨🇩",
    "Uzbekistan":               "🇺🇿",
    "England":                  "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Croatia":                  "🇭🇷",
    "Ghana":                    "🇬🇭",
    "Panama":                   "🇵🇦",
}


def _flag(team: str) -> str:
    return FLAG.get(team, "🌍")


def _pct(p: float, decimals: int = 1) -> str:
    return f"{p * 100:.{decimals}f}%"


def _odds(p: float) -> str:
    if p <= 0:
        return "—"
    return f"{1/p:.2f}"


def _edge_pct(edge: float) -> str:
    return f"{edge * 100:+.1f}%"


# ── CSS ──────────────────────────────────────────────────────────────────────

CSS = """
:root {
  --bg:      #0f1117;
  --card:    #15181f;
  --border:  #2a2d38;
  --accent:  #ff6b2b;
  --accent2: #ff9d6e;
  --text:    #e8eaf0;
  --sub:     #8b90a0;
  --green:   #22c55e;
  --red:     #ef4444;
  --yellow:  #f59e0b;
  --tab-bg:  #1c1f2e;
  --tab-act: #ff6b2b;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 13px;
  line-height: 1.4;
}

/* ── Sticky tab bar ── */
#tab-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--tab-bg);
  border-bottom: 2px solid var(--border);
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  padding: 6px 8px;
}

.tab-btn {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--sub);
  padding: 5px 11px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.15s;
}

.tab-btn:hover { background: var(--border); color: var(--text); }
.tab-btn.active {
  background: var(--tab-act);
  border-color: var(--tab-act);
  color: #fff;
}

/* ── Group section ── */
.group-section { display: none; padding: 16px 12px; }
.group-section.visible { display: block; }

.group-header {
  font-size: 18px;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 2px solid var(--accent);
}

/* ── Qual table ── */
.qual-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 18px;
  font-size: 12px;
}

.qual-table th {
  background: #1e2130;
  color: var(--sub);
  text-align: left;
  padding: 5px 8px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.qual-table td {
  padding: 5px 8px;
  border-bottom: 1px solid var(--border);
}

.qual-table tr:hover td { background: rgba(255,107,43,0.05); }

.prob-hi  { color: var(--green);  font-weight: 700; }
.prob-mid { color: var(--yellow); }
.prob-lo  { color: var(--red);    }

/* ── Match card ── */
.match-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  margin-bottom: 14px;
  overflow: hidden;
}

.match-card.value-bet {
  border: 2px solid var(--green);
  box-shadow: 0 0 10px rgba(34,197,94,0.15);
}

/* ── Card header ── */
.card-header {
  background: #1a1d28;
  padding: 12px 14px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 8px;
  border-bottom: 1px solid var(--border);
}

.teams-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.team-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}

.vs-sep {
  font-size: 11px;
  color: var(--sub);
  font-weight: 600;
}

.match-meta {
  font-size: 11px;
  color: var(--sub);
  text-align: right;
}

.lambda-badge {
  display: inline-block;
  background: rgba(255,107,43,0.15);
  color: var(--accent2);
  border-radius: 4px;
  padding: 2px 7px;
  font-size: 11px;
  font-weight: 600;
  margin-top: 4px;
}

/* ── Card body ── */
.card-body {
  padding: 12px 14px;
}

/* ── Section title ── */
.sec-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--sub);
  margin: 14px 0 6px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--border);
}

.sec-title:first-child { margin-top: 0; }

/* ── 1X2 row ── */
.result-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 6px;
  margin-bottom: 8px;
}

.result-cell {
  background: #1e2130;
  border-radius: 6px;
  padding: 8px 10px;
  text-align: center;
  border: 1px solid var(--border);
}

.result-cell.value-highlight {
  border-color: var(--green);
  background: rgba(34,197,94,0.08);
}

.result-label { font-size: 10px; color: var(--sub); text-transform: uppercase; }
.result-prob  { font-size: 18px; font-weight: 700; color: var(--text); margin: 2px 0; }
.result-odds  { font-size: 11px; color: var(--accent2); }
.result-edge  { font-size: 10px; margin-top: 2px; }
.edge-pos { color: var(--green); font-weight: 700; }
.edge-neg { color: var(--sub); }

/* ── Tri-bar ── */
.tri-bar {
  display: flex;
  height: 10px;
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 8px;
}

.tri-home { background: #3b82f6; }
.tri-draw { background: #6b7280; }
.tri-away { background: #ef4444; }

/* ── Score grid ── */
.score-grid-wrap {
  overflow-x: auto;
  margin-bottom: 4px;
}

.score-grid {
  border-collapse: collapse;
  font-size: 11px;
  min-width: 320px;
}

.score-grid th {
  background: #1e2130;
  color: var(--sub);
  padding: 4px 8px;
  text-align: center;
  font-weight: 600;
}

.score-grid td {
  padding: 4px 8px;
  text-align: center;
  border: 1px solid var(--border);
  min-width: 46px;
  font-size: 11px;
  transition: opacity 0.1s;
}

.score-grid td.top-score {
  font-weight: 700;
  outline: 1px solid var(--accent);
}

.score-grid .row-label {
  background: #1e2130;
  color: var(--sub);
  font-weight: 600;
}

/* ── Goals / BTTS table ── */
.ou-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  margin-bottom: 4px;
}

.ou-table th {
  background: #1e2130;
  color: var(--sub);
  padding: 4px 8px;
  text-align: left;
  font-weight: 600;
}

.ou-table td {
  padding: 4px 8px;
  border-bottom: 1px solid var(--border);
}

.ou-table tr:last-child td { border-bottom: none; }

/* ── AH table ── */
.ah-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.ah-table th {
  background: #1e2130;
  color: var(--sub);
  padding: 4px 8px;
  text-align: center;
  font-weight: 600;
}

.ah-table td {
  padding: 4px 8px;
  text-align: center;
  border-bottom: 1px solid var(--border);
}

.ah-table tr.fair-line td {
  background: rgba(255,107,43,0.12);
  color: var(--accent2);
  font-weight: 700;
}

/* ── Scorers ── */
.scorers-wrap {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.scorer-team-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--sub);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 5px;
}

.scorer-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.scorer-name {
  flex: 1;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.scorer-bar-wrap {
  width: 60px;
  background: var(--border);
  border-radius: 3px;
  height: 5px;
  flex-shrink: 0;
}

.scorer-bar {
  background: var(--accent);
  height: 5px;
  border-radius: 3px;
}

.scorer-pct {
  font-size: 11px;
  color: var(--accent2);
  min-width: 32px;
  text-align: right;
}

/* ── Market comparison ── */
.market-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.market-table th {
  background: #1e2130;
  color: var(--sub);
  padding: 4px 8px;
  text-align: left;
  font-weight: 600;
}

.market-table td {
  padding: 5px 8px;
  border-bottom: 1px solid var(--border);
}

.market-table tr.val-bet td:first-child {
  border-left: 3px solid var(--green);
}

.market-table tr.no-val td:first-child {
  border-left: 3px solid var(--border);
}

/* ── Elevenify placeholder ── */
.elevenify-box {
  background: #1a1d28;
  border: 1px dashed var(--border);
  border-radius: 6px;
  padding: 12px 14px;
  text-align: center;
}

.elevenify-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--accent);
  margin-bottom: 4px;
}

.elevenify-notice {
  font-size: 11px;
  color: var(--sub);
  font-style: italic;
}

/* ── All-groups overview ── */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 14px;
}

.overview-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
}

.overview-card-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 8px;
}

/* ── Value star ── */
.star { color: #f59e0b; margin-left: 4px; }

/* ── Responsive ── */
@media (max-width: 600px) {
  .scorers-wrap { grid-template-columns: 1fr; }
  .result-row   { grid-template-columns: 1fr; }
  .overview-grid { grid-template-columns: 1fr; }
}
"""

# ── JavaScript ───────────────────────────────────────────────────────────────

JS = """
function showGroup(g) {
  document.querySelectorAll('.group-section').forEach(el => el.classList.remove('visible'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById('sec-' + g).classList.add('visible');
  document.getElementById('tab-' + g).classList.add('active');
}

document.addEventListener('DOMContentLoaded', function() {
  showGroup('ALL');
});
"""


# ── HTML helpers ─────────────────────────────────────────────────────────────

def _h(s: str) -> str:
    """HTML-escape a string."""
    return html_mod.escape(str(s))


def _prob_colour(p: float) -> str:
    """Colour class for a probability value."""
    if p >= 0.70:
        return "prob-hi"
    if p >= 0.40:
        return "prob-mid"
    return "prob-lo"


# ── Card sections ────────────────────────────────────────────────────────────

def _result_section(home: str, away: str, res: dict, mo: dict | None) -> str:
    hw = res["home_win"]
    dr = res["draw"]
    aw = res["away_win"]

    edge_home = edge_draw = edge_away = None
    val_home = val_draw = val_away = False

    if mo:
        from .model import find_value
        edge_home, val_home = find_value(hw, mo["home"])
        edge_draw, val_draw = find_value(dr, mo["draw"])
        edge_away, val_away = find_value(aw, mo["away"])

    def cell(label: str, prob: float, mkt_odds: float | None,
             edge: float | None, is_val: bool) -> str:
        val_cls = "value-highlight" if is_val else ""
        odds_str = _odds(prob)
        edge_html = ""
        if edge is not None:
            star = '<span class="star">★</span>' if is_val else ""
            cls = "edge-pos" if is_val else "edge-neg"
            edge_html = (
                f'<div class="result-edge">'
                f'<span class="{cls}">Edge: {_edge_pct(edge)}</span>{star}'
                f'</div>'
            )
        mkt_html = ""
        if mkt_odds is not None:
            mkt_html = f'<div class="result-odds">Mkt: {mkt_odds:.2f}</div>'

        return (
            f'<div class="result-cell {val_cls}">'
            f'  <div class="result-label">{_h(label)}</div>'
            f'  <div class="result-prob">{_pct(prob)}</div>'
            f'  <div class="result-odds">Fair: {odds_str}</div>'
            f'  {mkt_html}'
            f'  {edge_html}'
            f'</div>'
        )

    cells = (
        cell(f"{_flag(home)} Home", hw, mo["home"] if mo else None, edge_home, val_home)
        + cell("Draw", dr, mo["draw"] if mo else None, edge_draw, val_draw)
        + cell(f"{_flag(away)} Away", aw, mo["away"] if mo else None, edge_away, val_away)
    )

    # Tri-bar
    hw_w = hw * 100
    dr_w = dr * 100
    aw_w = aw * 100

    tri = (
        f'<div class="tri-bar">'
        f'  <div class="tri-home" style="width:{hw_w:.1f}%"></div>'
        f'  <div class="tri-draw" style="width:{dr_w:.1f}%"></div>'
        f'  <div class="tri-away" style="width:{aw_w:.1f}%"></div>'
        f'</div>'
    )

    return (
        '<div class="sec-title">1. Match Result (1X2)</div>'
        f'<div class="result-row">{cells}</div>'
        f'{tri}'
    )


def _score_grid_section(res: dict) -> str:
    grid = res["score_grid"]

    # top-5 scorelines
    sorted_scores = sorted(grid.items(), key=lambda x: x[1], reverse=True)
    top5 = {k for k, _ in sorted_scores[:5]}

    header_row = "<tr><th>H\\ A</th>" + "".join(f"<th>{a}</th>" for a in range(6)) + "</tr>"

    rows = ""
    for h in range(6):
        row = f'<tr><td class="row-label">{h}</td>'
        for a in range(6):
            p = grid.get((h, a), 0.0)
            opacity = min(1.0, p / 0.15)
            bg = f"rgba(255,107,43,{opacity:.3f})"
            top_cls = " top-score" if (h, a) in top5 else ""
            p_str = f"{p*100:.1f}%" if p >= 0.01 else ""
            row += (
                f'<td class="{top_cls}" style="background:{bg}">'
                f'{p_str}</td>'
            )
        row += "</tr>"
        rows += row

    table = (
        '<div class="score-grid-wrap">'
        f'<table class="score-grid">{header_row}{rows}</table>'
        '</div>'
    )

    return '<div class="sec-title">2. Score Grid (heatmap)</div>' + table


def _goals_section(res: dict) -> str:
    lines = [
        ("O/U 0.5",  res["over_05"],  1 - res["over_05"]),
        ("O/U 1.5",  res["over_15"],  1 - res["over_15"]),
        ("O/U 2.5",  res["over_25"],  1 - res["over_25"]),
        ("O/U 3.5",  res["over_35"],  1 - res["over_35"]),
        ("O/U 4.5",  res["over_45"],  1 - res["over_45"]),
    ]
    btts_y = res["btts"]
    btts_n = 1 - btts_y

    rows = ""
    for label, ov, un in lines:
        rows += (
            f"<tr>"
            f"  <td>{_h(label)}</td>"
            f"  <td>Over: {_pct(ov)} &nbsp; ({_odds(ov)})</td>"
            f"  <td>Under: {_pct(un)} &nbsp; ({_odds(un)})</td>"
            f"</tr>"
        )

    rows += (
        f"<tr>"
        f"  <td>BTTS</td>"
        f"  <td>Yes: {_pct(btts_y)} &nbsp; ({_odds(btts_y)})</td>"
        f"  <td>No: {_pct(btts_n)} &nbsp; ({_odds(btts_n)})</td>"
        f"</tr>"
    )

    table = (
        f'<table class="ou-table">'
        f'  <tr><th>Market</th><th>Over / Yes</th><th>Under / No</th></tr>'
        f'  {rows}'
        f'</table>'
    )

    return '<div class="sec-title">3. Goals Markets</div>' + table


def _ah_section(home: str, away: str, res: dict) -> str:
    lines_to_show = [
        -2.5, -2.0, -1.5, -1.0, -0.75, -0.5, -0.25,
        0.0,
        0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5,
    ]

    # Find fair line (home cover ≈ 50%)
    best_line = None
    best_dist = 999.0
    for line in lines_to_show:
        if line in res["ah_home"]:
            dist = abs(res["ah_home"][line] - 0.50)
            if dist < best_dist:
                best_dist = dist
                best_line = line

    header = (
        f"<tr>"
        f"  <th>Line</th>"
        f"  <th>{_h(home)} Cover</th>"
        f"  <th>Push</th>"
        f"  <th>{_h(away)} Cover</th>"
        f"</tr>"
    )

    rows = ""
    for line in lines_to_show:
        hc = res["ah_home"].get(line, 0.0)
        pu = res["ah_push"].get(line, 0.0)
        ac = res["ah_away"].get(line, 0.0)
        fair_cls = " fair-line" if line == best_line else ""
        sign = "+" if line > 0 else ""
        line_str = f"{sign}{line:g}"
        rows += (
            f'<tr class="{fair_cls}">'
            f"  <td><strong>{line_str}</strong></td>"
            f"  <td>{_pct(hc)}</td>"
            f"  <td>{_pct(pu)}</td>"
            f"  <td>{_pct(ac)}</td>"
            f"</tr>"
        )

    table = (
        f'<table class="ah-table">'
        f"  {header}"
        f"  {rows}"
        f"</table>"
    )

    return '<div class="sec-title">4. Asian Handicap</div>' + table


def _scorers_section(home: str, away: str, res: dict) -> str:
    h_lam = res["lambda_home"]
    a_lam = res["lambda_away"]

    h_players = scorer_probs(home, h_lam, top_n=5)
    a_players = scorer_probs(away, a_lam, top_n=5)

    def player_rows(players: list) -> str:
        html = ""
        for p in players:
            bar_w = int(min(100, p["prob"] * 100 / 0.7 * 100))
            html += (
                f'<div class="scorer-row">'
                f'  <span class="scorer-name">{_h(p["name"])}</span>'
                f'  <div class="scorer-bar-wrap">'
                f'    <div class="scorer-bar" style="width:{bar_w}%"></div>'
                f'  </div>'
                f'  <span class="scorer-pct">{_pct(p["prob"])}</span>'
                f'</div>'
            )
        if not html:
            html = '<div style="color:var(--sub);font-size:11px;">No player data</div>'
        return html

    content = (
        f'<div class="scorers-wrap">'
        f'  <div>'
        f'    <div class="scorer-team-label">{_flag(home)} {_h(home)}</div>'
        f'    {player_rows(h_players)}'
        f'  </div>'
        f'  <div>'
        f'    <div class="scorer-team-label">{_flag(away)} {_h(away)}</div>'
        f'    {player_rows(a_players)}'
        f'  </div>'
        f'</div>'
    )

    return '<div class="sec-title">5. Anytime Scorers</div>' + content


def _market_section(home: str, away: str, res: dict, mo: dict) -> str:
    from .model import find_value

    rows_data = [
        ("Home Win", res["home_win"], mo["home"]),
        ("Draw",     res["draw"],     mo["draw"]),
        ("Away Win", res["away_win"], mo["away"]),
    ]

    header = (
        "<tr>"
        "  <th>Outcome</th>"
        "  <th>Model %</th>"
        "  <th>Market Implied</th>"
        "  <th>Decimal Odds</th>"
        "  <th>Edge</th>"
        "</tr>"
    )

    rows = ""
    for label, model_p, mkt_odds in rows_data:
        edge, is_val = find_value(model_p, mkt_odds)
        implied = 1.0 / mkt_odds
        val_cls = "val-bet" if is_val else "no-val"
        edge_cls = "edge-pos" if is_val else "edge-neg"
        star = " ★" if is_val else ""
        rows += (
            f'<tr class="{val_cls}">'
            f"  <td>{_h(label)}{star}</td>"
            f"  <td>{_pct(model_p)}</td>"
            f"  <td>{_pct(implied)}</td>"
            f"  <td>{mkt_odds:.2f}</td>"
            f'  <td><span class="{edge_cls}">{_edge_pct(edge)}</span></td>'
            f"</tr>"
        )

    table = (
        f'<table class="market-table">'
        f"  {header}"
        f"  {rows}"
        f"</table>"
    )

    return '<div class="sec-title">6. Market Comparison</div>' + table


def _elevenify_section() -> str:
    return (
        '<div class="sec-title">7. Elevenify Benchmark</div>'
        '<div class="elevenify-box">'
        '  <div class="elevenify-label">Elevenify Benchmark</div>'
        '  <div class="elevenify-notice">'
        '    Add Elevenify predictions to data/elevenify.py to populate this section'
        '  </div>'
        '</div>'
    )


# ── Full match card ───────────────────────────────────────────────────────────

def _value_badge(has_value: bool) -> str:
    if has_value:
        return '<div style="color:var(--green);font-size:10px;">★ Value Bet Found</div>'
    return ""


def _match_card(home: str, away: str, matchday: int, date_str: str,
                group: str, res: dict) -> str:
    mo = MARKET_ODDS.get((home, away))

    # Check for any value bet to style card border
    has_value = False
    if mo:
        from .model import find_value
        for prob, mkt_k in [(res["home_win"], "home"), (res["draw"], "draw"), (res["away_win"], "away")]:
            _, is_val = find_value(prob, mo[mkt_k])
            if is_val:
                has_value = True
                break

    card_cls = "match-card value-bet" if has_value else "match-card"

    lam_h = res["lambda_home"]
    lam_a = res["lambda_away"]

    header = (
        f'<div class="card-header">'
        f'  <div>'
        f'    <div class="teams-row">'
        f'      <span class="team-name">{_flag(home)} {_h(home)}</span>'
        f'      <span class="vs-sep">vs</span>'
        f'      <span class="team-name">{_flag(away)} {_h(away)}</span>'
        f'    </div>'
        f'    <div>'
        f'      <span class="lambda-badge">λ home: {lam_h:.2f}</span>'
        f'      <span class="lambda-badge">λ away: {lam_a:.2f}</span>'
        f'    </div>'
        f'  </div>'
        f'  <div class="match-meta">'
        f'    <div>Group {_h(group)} · MD{matchday}</div>'
        f'    <div>{_h(date_str)}</div>'
        f'    {_value_badge(has_value)}'
        f'  </div>'
        f'</div>'
    )

    body_parts = [
        _result_section(home, away, res, mo),
        _score_grid_section(res),
        _goals_section(res),
        _ah_section(home, away, res),
        _scorers_section(home, away, res),
    ]

    if mo:
        body_parts.append(_market_section(home, away, res, mo))

    body_parts.append(_elevenify_section())

    body_inner = "".join(body_parts)
    body = f'<div class="card-body">{body_inner}</div>'

    return f'<div class="{card_cls}">{header}{body}</div>'


# ── Group qual table ──────────────────────────────────────────────────────────

def _qual_table(group: str, gr: dict) -> str:
    teams = GROUPS[group]
    rows = ""
    for team in sorted(teams, key=lambda t: gr["qualification"][t], reverse=True):
        q   = gr["qualification"][team]
        w   = gr["win_group"][team]
        tp  = gr["third_place"][team]
        pts = gr["points_avg"][team]
        rows += (
            f"<tr>"
            f'  <td>{_flag(team)} {_h(team)}</td>'
            f'  <td class="{_prob_colour(q)}">{_pct(q)}</td>'
            f'  <td class="{_prob_colour(w)}">{_pct(w)}</td>'
            f'  <td>{_pct(tp)}</td>'
            f'  <td>{pts:.1f}</td>'
            f"</tr>"
        )

    return (
        '<table class="qual-table">'
        "  <tr>"
        "    <th>Team</th>"
        "    <th>Qualify (Top 2) %</th>"
        "    <th>Win Group %</th>"
        "    <th>3rd Place %</th>"
        "    <th>Avg Pts</th>"
        "  </tr>"
        f"  {rows}"
        "</table>"
    )


# ── Overview section ──────────────────────────────────────────────────────────

def _overview_section(group_results: dict[str, dict]) -> str:
    cards = ""
    for group in sorted(group_results.keys()):
        gr = group_results[group]
        teams = GROUPS[group]
        rows = ""
        for team in sorted(teams, key=lambda t: gr["qualification"][t], reverse=True):
            q   = gr["qualification"][team]
            w   = gr["win_group"][team]
            pts = gr["points_avg"][team]
            rows += (
                f"<tr>"
                f'  <td style="padding:3px 6px">{_flag(team)} {_h(team)}</td>'
                f'  <td style="padding:3px 6px" class="{_prob_colour(q)}">{_pct(q)}</td>'
                f'  <td style="padding:3px 6px" class="{_prob_colour(w)}">{_pct(w)}</td>'
                f'  <td style="padding:3px 6px;color:var(--sub)">{pts:.1f}</td>'
                f"</tr>"
            )
        table = (
            f'<table class="qual-table" style="margin-bottom:0">'
            f'  <tr><th>Team</th><th>Qual%</th><th>Win%</th><th>Pts</th></tr>'
            f"  {rows}"
            f"</table>"
        )
        cards += (
            f'<div class="overview-card">'
            f'  <div class="overview-card-title">Group {_h(group)}</div>'
            f"  {table}"
            f"</div>"
        )

    return (
        f'<div class="group-header">All Groups — Qualification Overview</div>'
        f'<div class="overview-grid">{cards}</div>'
    )


# ── Main generator ────────────────────────────────────────────────────────────

def generate_report(n_sims: int = 10_000, out_path: str = "wc2026_match_pages.html") -> None:
    import numpy as np

    all_groups = sorted(GROUPS.keys())
    rng = np.random.default_rng(42)

    # ── Simulate all matches + groups ────────────────────────────────────────
    # Organise fixtures by group
    fixtures_by_group: dict[str, list] = {g: [] for g in all_groups}
    for home, away, matchday, date_str in FIXTURES:
        group = TEAMS[home]["group"]
        fixtures_by_group[group].append((home, away, matchday, date_str))

    match_results: dict[tuple[str, str], dict] = {}
    group_results: dict[str, dict] = {}

    for group in all_groups:
        print(f"  Simulating Group {group}...", flush=True)
        for home, away, matchday, date_str in fixtures_by_group[group]:
            print(f"    {home} vs {away}", flush=True)
            res = simulate_match(home, away, n_sims=n_sims, rng=rng)
            match_results[(home, away)] = res

        # Group qual simulation (smaller n_sims for speed)
        qual_sims = min(n_sims, 20_000)
        group_results[group] = simulate_group(group, n_sims=qual_sims, rng=rng)

    # ── Build HTML ───────────────────────────────────────────────────────────
    # Tab bar
    tab_buttons = (
        '<button class="tab-btn active" id="tab-ALL" onclick="showGroup(\'ALL\')">All Groups</button>'
    )
    for g in all_groups:
        tab_buttons += (
            f'<button class="tab-btn" id="tab-{g}" onclick="showGroup(\'{g}\')">'
            f'Group {g}</button>'
        )

    tab_bar = f'<div id="tab-bar">{tab_buttons}</div>'

    # All-groups overview section
    overview_html = (
        f'<div class="group-section visible" id="sec-ALL">'
        f'  {_overview_section(group_results)}'
        f'</div>'
    )

    # Per-group sections
    group_sections = ""
    for group in all_groups:
        qt = _qual_table(group, group_results[group])
        cards = ""
        for home, away, matchday, date_str in fixtures_by_group[group]:
            res = match_results[(home, away)]
            cards += _match_card(home, away, matchday, date_str, group, res)

        group_sections += (
            f'<div class="group-section" id="sec-{group}">'
            f'  <div class="group-header">Group {_h(group)}</div>'
            f'  {qt}'
            f'  {cards}'
            f'</div>'
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>WC2026 Match Prediction Report</title>
<style>
{CSS}
</style>
</head>
<body>
{tab_bar}
<div id="content">
{overview_html}
{group_sections}
</div>
<script>
{JS}
</script>
</body>
</html>"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n  Done! Report saved to: {out_path}", flush=True)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate WC2026 per-match HTML prediction report"
    )
    parser.add_argument(
        "--sims",
        type=int,
        default=10_000,
        help="Monte Carlo simulations per match (default: 10000)",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="wc2026_match_pages.html",
        help="Output HTML file path (default: wc2026_match_pages.html)",
    )
    args = parser.parse_args()

    print(f"WC2026 Match Report Generator")
    print(f"  Simulations per match : {args.sims:,}")
    print(f"  Output file           : {args.out}")
    print()

    generate_report(n_sims=args.sims, out_path=args.out)


if __name__ == "__main__":
    main()
