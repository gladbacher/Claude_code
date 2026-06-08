"""
WC2026 best-bets summary page generator.

Produces a standalone HTML page listing one best bet per fixture (72 total),
with model probability, fair odds in UK fractional format, and market odds
where available.

Usage:
    python -m wc2026.report_bestbets --sims 10000 --out wc2026_best_bets.html
"""

from __future__ import annotations

import argparse
import html as html_mod
import sys

from .data import FIXTURES, TEAMS
from .data.odds import MARKET_ODDS
from .model import simulate_match
from .commentary import get_bet_data, decimal_to_uk

_h = html_mod.escape


_CATEGORY_COLOUR = {
    "value":  "#22c55e",
    "btts":   "#a78bfa",
    "goals":  "#38bdf8",
    "ah":     "#fb923c",
    "scorer": "#facc15",
    "win":    "#94a3b8",
    "draw":   "#94a3b8",
}

_CATEGORY_LABEL = {
    "value":  "VALUE",
    "btts":   "BTTS",
    "goals":  "GOALS",
    "ah":     "HANDICAP",
    "scorer": "SCORER",
    "win":    "MATCH",
    "draw":   "MATCH",
}


def _pct(f: float) -> str:
    return f"{f * 100:.1f}%"


def _edge_str(edge) -> str:
    if edge is None:
        return "—"
    colour = "#22c55e" if edge >= 0.08 else ("#eab308" if edge >= 0.05 else "#3b82f6")
    star = " ★" if edge >= 0.08 else (" ·" if edge >= 0.05 else "")
    return f'<span style="color:{colour};font-weight:700">+{edge*100:.1f}pp{star}</span>'


_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: system-ui, -apple-system, sans-serif;
  background: #0f172a;
  color: #e2e8f0;
  max-width: 1300px;
  margin: 0 auto;
  padding: 1.5rem 1rem;
}
h1 { font-size: 1.5rem; color: #f8fafc; margin-bottom: 0.25rem; }
.subtitle { color: #64748b; font-size: 0.85rem; margin-bottom: 1.5rem; }
.legend {
  display: flex; flex-wrap: wrap; gap: 1rem;
  font-size: 0.78rem; color: #94a3b8;
  margin-bottom: 1.2rem;
}
.legend-item { display: flex; align-items: center; gap: 0.3rem; }
.dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }

.controls {
  display: flex; gap: 0.75rem; flex-wrap: wrap;
  margin-bottom: 1rem;
}
.filter-btn {
  background: #1e293b; border: 1px solid #334155;
  color: #94a3b8; padding: 0.3rem 0.8rem;
  border-radius: 20px; cursor: pointer; font-size: 0.8rem;
  transition: all 0.15s;
}
.filter-btn:hover, .filter-btn.active {
  background: #334155; color: #f8fafc; border-color: #475569;
}

table { width: 100%; border-collapse: collapse; font-size: 0.83rem; }
thead th {
  background: #1e293b; color: #94a3b8;
  padding: 0.55rem 0.7rem; text-align: left;
  position: sticky; top: 0; z-index: 10;
  cursor: pointer; user-select: none;
  white-space: nowrap;
}
thead th:hover { color: #e2e8f0; }
thead th.sort-asc::after  { content: " ▲"; font-size: 0.7rem; }
thead th.sort-desc::after { content: " ▼"; font-size: 0.7rem; }

tbody tr { border-bottom: 1px solid #1e293b; }
tbody tr:hover td { background: rgba(255,255,255,0.03); }
td { padding: 0.45rem 0.7rem; vertical-align: middle; }

.match-cell { font-weight: 600; color: #f1f5f9; }
.flag { font-size: 1rem; }
.vs { color: #475569; font-size: 0.75rem; margin: 0 0.3rem; }

.cat-badge {
  display: inline-block; font-size: 0.65rem; font-weight: 700;
  padding: 2px 6px; border-radius: 3px; letter-spacing: 0.04em;
}
.bet-label { font-weight: 600; }
.model-pct { font-weight: 700; color: #f8fafc; }
.fair-uk {
  font-weight: 700; font-size: 0.95rem; color: #fbbf24;
  letter-spacing: 0.02em;
}
.market-odds { color: #94a3b8; }
.src-c { color: #22c55e; font-size: 0.7rem; }
.src-e { color: #475569; font-size: 0.7rem; }

.group-cell { color: #64748b; font-size: 0.8rem; }
.date-cell  { color: #64748b; font-size: 0.8rem; white-space: nowrap; }

.summary-bar {
  display: flex; gap: 1.5rem; flex-wrap: wrap;
  background: #1e293b; border-radius: 8px;
  padding: 0.8rem 1rem; margin-bottom: 1.2rem;
  font-size: 0.82rem;
}
.summary-stat strong { color: #f8fafc; font-size: 1rem; }
"""


_JS = """
const rows = Array.from(document.querySelectorAll('#bet-tbody tr'));
let currentSort = {col: null, asc: true};
let activeFilter = 'ALL';

function filterRows() {
  rows.forEach(r => {
    const cat = r.dataset.cat || '';
    const grp = r.dataset.group || '';
    const show = activeFilter === 'ALL' ||
                 activeFilter === cat.toUpperCase() ||
                 activeFilter === grp;
    r.style.display = show ? '' : 'none';
  });
}

document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.dataset.filter;
    filterRows();
  });
});

document.querySelectorAll('thead th[data-col]').forEach(th => {
  th.addEventListener('click', () => {
    const col = th.dataset.col;
    const asc = currentSort.col === col ? !currentSort.asc : true;
    currentSort = {col, asc};
    document.querySelectorAll('thead th').forEach(t => t.classList.remove('sort-asc','sort-desc'));
    th.classList.add(asc ? 'sort-asc' : 'sort-desc');
    const tbody = document.getElementById('bet-tbody');
    const sorted = [...rows].sort((a, b) => {
      const va = a.dataset[col] || '';
      const vb = b.dataset[col] || '';
      const na = parseFloat(va), nb = parseFloat(vb);
      const cmp = isNaN(na) ? va.localeCompare(vb) : na - nb;
      return asc ? cmp : -cmp;
    });
    sorted.forEach(r => tbody.appendChild(r));
  });
});
"""


def _flag(team: str) -> str:
    flags = {
        "Mexico": "🇲🇽", "South Africa": "🇿🇦", "Korea Republic": "🇰🇷",
        "Czech Republic": "🇨🇿", "Canada": "🇨🇦", "Qatar": "🇶🇦",
        "Switzerland": "🇨🇭", "Bosnia and Herzegovina": "🇧🇦", "Brazil": "🇧🇷",
        "Morocco": "🇲🇦", "Haiti": "🇭🇹", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
        "United States": "🇺🇸", "Paraguay": "🇵🇾", "Türkiye": "🇹🇷",
        "Australia": "🇦🇺", "Germany": "🇩🇪", "Curacao": "🇨🇼",
        "Côte d'Ivoire": "🇨🇮", "Ecuador": "🇪🇨", "Sweden": "🇸🇪",
        "Netherlands": "🇳🇱", "Japan": "🇯🇵", "Tunisia": "🇹🇳",
        "Belgium": "🇧🇪", "Egypt": "🇪🇬", "Spain": "🇪🇸",
        "Saudi Arabia": "🇸🇦", "Cape Verde Islands": "🇨🇻", "Uruguay": "🇺🇾",
        "France": "🇫🇷", "Iraq": "🇮🇶", "Norway": "🇳🇴",
        "Senegal": "🇸🇳", "Argentina": "🇦🇷", "Jordan": "🇯🇴",
        "Algeria": "🇩🇿", "Austria": "🇦🇹", "Portugal": "🇵🇹",
        "Congo DR": "🇨🇩", "Colombia": "🇨🇴", "Uzbekistan": "🇺🇿",
        "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Ghana": "🇬🇭", "Croatia": "🇭🇷",
        "Panama": "🇵🇦", "New Zealand": "🇳🇿", "Iran": "🇮🇷",
        "Peru": "🇵🇪",
    }
    return flags.get(team, "🏳️")


def generate_bestbets(n_sims: int = 10_000, out_path: str = "wc2026_best_bets.html") -> None:
    import numpy as np

    rng = np.random.default_rng(42)

    print("WC2026 Best-Bets Report Generator", flush=True)
    print(f"  Simulations per match : {n_sims:,}", flush=True)

    bets: list[dict] = []

    for i, (home, away, matchday, date_str) in enumerate(FIXTURES):
        print(f"  [{i+1:02d}/72] {home} vs {away}", flush=True)
        res = simulate_match(home, away, n_sims=n_sims, rng=rng)
        bet = get_bet_data(home, away, res, seed=i)
        group = TEAMS[home]["group"]
        mo = MARKET_ODDS.get((home, away), {})
        bets.append({
            **bet,
            "home": home,
            "away": away,
            "matchday": matchday,
            "date": date_str,
            "group": group,
            "mo_home":  mo.get("home"),
            "mo_draw":  mo.get("draw"),
            "mo_away":  mo.get("away"),
            "mo_src":   mo.get("src", "E"),
        })

    # ── Summary stats ────────────────────────────────────────────────────────
    value_bets = [b for b in bets if b["category"] == "value"]
    high_edge  = [b for b in value_bets if b["edge"] and b["edge"] >= 0.08]
    avg_model  = sum(b["model_p"] for b in bets) / len(bets)

    cat_counts = {}
    for b in bets:
        cat_counts[b["category"]] = cat_counts.get(b["category"], 0) + 1

    summary_bar = (
        f'<div class="summary-bar">'
        f'  <div class="summary-stat"><strong>{len(bets)}</strong> Fixtures</div>'
        f'  <div class="summary-stat"><strong>{len(value_bets)}</strong> Value Bets (edge ≥ 5%)</div>'
        f'  <div class="summary-stat"><strong>{len(high_edge)}</strong> High-edge ★ (≥ 8%)</div>'
        f'  <div class="summary-stat"><strong>{avg_model*100:.0f}%</strong> Avg model confidence</div>'
        + "".join(
            f'  <div class="summary-stat"><strong>{v}</strong> {k.title()}</div>'
            for k, v in sorted(cat_counts.items())
        )
        + f'</div>'
    )

    # ── Filter buttons ───────────────────────────────────────────────────────
    cats = sorted(cat_counts.keys())
    groups = sorted({b["group"] for b in bets})

    filter_btns = '<button class="filter-btn active" data-filter="ALL">All</button>'
    filter_btns += '<button class="filter-btn" data-filter="VALUE">★ Value</button>'
    for cat in cats:
        if cat != "value":
            lbl = _CATEGORY_LABEL.get(cat, cat.upper())
            filter_btns += f'<button class="filter-btn" data-filter="{cat.upper()}">{lbl}</button>'
    filter_btns += ' &nbsp; '
    for grp in groups:
        filter_btns += f'<button class="filter-btn" data-filter="{grp}">Grp {grp}</button>'

    # ── Table rows ───────────────────────────────────────────────────────────
    tbody = ""
    for b in bets:
        cat = b["category"]
        colour = _CATEGORY_COLOUR.get(cat, "#94a3b8")
        cat_lbl = _CATEGORY_LABEL.get(cat, cat.upper())

        match_cell = (
            f'<span class="flag">{_flag(b["home"])}</span> {_h(b["home"])}'
            f'<span class="vs">vs</span>'
            f'<span class="flag">{_flag(b["away"])}</span> {_h(b["away"])}'
        )

        src_cls = "src-c" if b["mo_src"] == "C" else "src-e"
        src_badge = f'<span class="{src_cls}">[{b["mo_src"]}]</span>'

        # For 1X2 bets that have a direct market price, show it prominently
        if b["market_odds"] and b["category"] in ("value", "win", "draw"):
            mkt_cell = (
                f'<strong>{b["market_odds"]:.2f}</strong> '
                f'<small style="color:#64748b">({decimal_to_uk(b["market_odds"])})</small> '
                f'{src_badge}'
            )
        elif b["mo_home"] and b["mo_draw"] and b["mo_away"]:
            # Show full 1X2 line as context for goals/btts/ah/scorer bets
            h_uk = decimal_to_uk(b["mo_home"])
            d_uk = decimal_to_uk(b["mo_draw"])
            a_uk = decimal_to_uk(b["mo_away"])
            mkt_cell = (
                f'<span style="color:#94a3b8;font-size:0.78rem">'
                f'H&nbsp;<strong style="color:#e2e8f0">{b["mo_home"]:.2f}</strong>'
                f'&nbsp;<span style="color:#64748b">({h_uk})</span>'
                f'&ensp;D&nbsp;<strong style="color:#e2e8f0">{b["mo_draw"]:.2f}</strong>'
                f'&nbsp;<span style="color:#64748b">({d_uk})</span>'
                f'&ensp;A&nbsp;<strong style="color:#e2e8f0">{b["mo_away"]:.2f}</strong>'
                f'&nbsp;<span style="color:#64748b">({a_uk})</span>'
                f'&ensp;{src_badge}'
                f'</span>'
            )
        else:
            mkt_cell = "—"

        edge_cell = _edge_str(b["edge"])

        edge_sort = f'{b["edge"]:.4f}' if b["edge"] else "0"
        model_sort = f'{b["model_p"]:.4f}'

        tbody += (
            f'<tr data-cat="{cat}" data-group="{b["group"]}" '
            f'    data-edge="{edge_sort}" data-model="{model_sort}" '
            f'    data-date="{b["date"]}">'
            f'  <td class="date-cell">{_h(b["date"])}</td>'
            f'  <td class="group-cell">Grp {_h(b["group"])} · MD{b["matchday"]}</td>'
            f'  <td class="match-cell">{match_cell}</td>'
            f'  <td>'
            f'    <span class="cat-badge" style="background:{colour}22;color:{colour}">{cat_lbl}</span>'
            f'    &nbsp;<span class="bet-label">{_h(b["label"])}</span>'
            f'  </td>'
            f'  <td class="model-pct">{_pct(b["model_p"])}</td>'
            f'  <td class="fair-uk">{_h(b["fair_uk"])}</td>'
            f'  <td>'
            f'    <span style="color:#94a3b8;font-size:0.8rem">'
            f'      {b["fair_dec"]:.2f}</span>'
            f'  </td>'
            f'  <td>{mkt_cell}</td>'
            f'  <td>{edge_cell}</td>'
            f'</tr>\n'
        )

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_items = "".join(
        f'<span class="legend-item"><span class="dot" style="background:{_CATEGORY_COLOUR[c]}"></span>'
        f' {_CATEGORY_LABEL[c]}</span>'
        for c in ["value", "btts", "goals", "ah", "scorer", "win"]
    )
    legend_items += (
        '<span class="legend-item"><span style="color:#22c55e">[C]</span> confirmed odds</span>'
        '<span class="legend-item"><span style="color:#475569">[E]</span> estimated odds</span>'
        '<span class="legend-item">★ = edge ≥ 8%&nbsp; · = edge ≥ 5%</span>'
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>WC2026 Best Bets</title>
<style>{_CSS}</style>
</head>
<body>
<h1>⚽ WC2026 Group Stage — Best Bets</h1>
<p class="subtitle">
  One best bet per fixture · Fair odds in UK fractional format ·
  Dixon-Coles Poisson + FIFA rank adjustment + host advantage
</p>
{summary_bar}
<div class="legend">{legend_items}</div>
<div class="controls">{filter_btns}</div>

<table>
<thead>
<tr>
  <th data-col="date">Date</th>
  <th>Group</th>
  <th>Match</th>
  <th>Best Bet</th>
  <th data-col="model">Model%</th>
  <th>Fair (UK)</th>
  <th>Fair (Dec)</th>
  <th>Market Odds (1X2)</th>
  <th data-col="edge">Edge</th>
</tr>
</thead>
<tbody id="bet-tbody">
{tbody}
</tbody>
</table>

<script>{_JS}</script>
</body>
</html>"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n  Done! Saved to: {out_path}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate WC2026 best-bets HTML page")
    parser.add_argument("--sims", type=int, default=10_000)
    parser.add_argument("--out", type=str, default="wc2026_best_bets.html")
    args = parser.parse_args()
    generate_bestbets(n_sims=args.sims, out_path=args.out)


if __name__ == "__main__":
    main()
