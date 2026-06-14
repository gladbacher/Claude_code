#!/usr/bin/env python3
"""
World Cup 2026 Family Sweepstake Tracker.

Usage:
    python sweepstake.py          # fetch new results, update standings.html
    python sweepstake.py --reset  # wipe processed_matches.json and recalculate
    python sweepstake.py --debug  # print unrecognised team names from API
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import requests

# ── Paths ─────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
PROCESSED_FILE = SCRIPT_DIR / "processed_matches.json"
STANDINGS_HTML = SCRIPT_DIR / "standings.html"
ENV_FILE = SCRIPT_DIR / ".env"

WC_START = date(2026, 6, 11)
WC_END   = date(2026, 7, 19)   # final

# ── Player ↔ Team assignments ─────────────────────────────────────────────────
# Canonical team names match wc2026/data/teams.py exactly.

PLAYERS: dict[str, list[str]] = {
    "Luis": [
        "Qatar",        "Uzbekistan",           "England",          "Senegal",
        "Algeria",      "Uruguay",              "Jordan",           "France",
        "Morocco",      "Congo DR",             "Côte d'Ivoire",    "Mexico",
    ],
    "Isla": [
        "Saudi Arabia", "Japan",                "Tunisia",          "Paraguay",
        "United States","Brazil",               "Colombia",         "Spain",
        "Ecuador",      "Türkiye",              "Czech Republic",   "Bosnia and Herzegovina",
    ],
    "Mummy": [
        "Canada",       "Germany",              "Netherlands",      "South Africa",
        "Australia",    "Belgium",              "Cape Verde Islands","Iraq",
        "Iran",         "Egypt",                "Korea Republic",   "Austria",
    ],
    "Daddy": [
        "Sweden",       "Panama",               "Scotland",         "Ghana",
        "Haiti",        "Croatia",              "Curacao",          "Argentina",
        "Norway",       "Portugal",             "New Zealand",      "Switzerland",
    ],
}

PLAYER_ORDER = list(PLAYERS.keys())

# Reverse lookup: canonical team name → player
TEAM_OWNER: dict[str, str] = {
    team: player
    for player, teams in PLAYERS.items()
    for team in teams
}

# ── Name normalisation ─────────────────────────────────────────────────────────
# Maps API/source team names → canonical sweepstake names.
# Only non-identity mappings are needed here.

NAME_MAP: dict[str, str] = {
    # Ivory Coast
    "Ivory Coast":                  "Côte d'Ivoire",
    "Cote d'Ivoire":                "Côte d'Ivoire",
    # Turkey
    "Turkey":                       "Türkiye",
    # Czech Republic
    "Czechia":                      "Czech Republic",
    # South Korea
    "South Korea":                  "Korea Republic",
    "Republic of Korea":            "Korea Republic",
    # USA
    "USA":                          "United States",
    "US":                           "United States",
    "United States of America":     "United States",
    # Bosnia
    "Bosnia & Herzegovina":         "Bosnia and Herzegovina",
    "Bosnia-Herzegovina":           "Bosnia and Herzegovina",
    "Bosnia":                       "Bosnia and Herzegovina",
    # Congo
    "DR Congo":                     "Congo DR",
    "Democratic Republic of Congo": "Congo DR",
    "Congo, DR":                    "Congo DR",
    "DRC":                          "Congo DR",
    # Curacao
    "Curaçao":                      "Curacao",
    # Cape Verde
    "Cape Verde":                   "Cape Verde Islands",
}


def normalise(name: str) -> str:
    """Map an API team name to its canonical sweepstake name."""
    return NAME_MAP.get(name.strip(), name.strip())


# ── Environment / API key ──────────────────────────────────────────────────────

def load_api_key() -> str | None:
    """Read FOOTBALL_DATA_API_KEY from .env file or shell environment."""
    if ENV_FILE.exists():
        for raw in ENV_FILE.read_text().splitlines():
            line = raw.strip()
            if line.startswith("FOOTBALL_DATA_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("FOOTBALL_DATA_API_KEY")


def prompt_for_api_key() -> str | None:
    """Ask the user for a football-data.org key; save it to .env if supplied."""
    print("\n[INFO] No FOOTBALL_DATA_API_KEY found in .env or environment.")
    print("       Get a free key at https://www.football-data.org/client/register")
    print("       Press Enter to skip and use the ESPN fallback instead.\n")
    try:
        key = input("  Paste API key (or Enter to skip): ").strip()
    except (EOFError, KeyboardInterrupt):
        return None
    if key:
        with open(ENV_FILE, "a") as fh:
            fh.write(f"\nFOOTBALL_DATA_API_KEY={key}\n")
        print(f"  Saved to {ENV_FILE}\n")
        return key
    return None


# ── Data fetching ──────────────────────────────────────────────────────────────

_HEADERS = {"User-Agent": "wc2026-sweepstake/1.0"}


def _date_range() -> list[str]:
    """All dates from WC start to today (inclusive), as YYYYMMDD strings."""
    today   = min(date.today(), WC_END)
    current = WC_START
    out     = []
    while current <= today:
        out.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)
    return out


def fetch_espn() -> list[dict]:
    """
    Fetch completed WC 2026 matches from ESPN's unofficial JSON scoreboard API.
    Makes one request per calendar day since the tournament started.
    """
    matches: list[dict] = []
    seen: set[str] = set()

    for date_str in _date_range():
        url = (
            "https://site.api.espn.com/apis/site/v2/sports/soccer/"
            f"fifa.world/scoreboard?dates={date_str}&limit=50"
        )
        try:
            r = requests.get(url, timeout=15, headers=_HEADERS)
            r.raise_for_status()
            data = r.json()
        except Exception as exc:
            print(f"  [WARN] ESPN: {date_str} → {exc}", file=sys.stderr)
            time.sleep(1)
            continue

        for event in data.get("events", []):
            eid = f"espn_{event['id']}"
            if eid in seen:
                continue

            if not event.get("status", {}).get("type", {}).get("completed"):
                continue

            try:
                comp        = event["competitions"][0]
                competitors = comp["competitors"]
                home_c      = next(c for c in competitors if c["homeAway"] == "home")
                away_c      = next(c for c in competitors if c["homeAway"] == "away")

                hs = home_c.get("score")
                as_ = away_c.get("score")
                if hs is None or as_ is None:
                    continue

                matches.append({
                    "id":         eid,
                    "home":       home_c["team"]["displayName"],
                    "away":       away_c["team"]["displayName"],
                    "home_score": int(hs),
                    "away_score": int(as_),
                    "date":       event["date"][:10],
                })
                seen.add(eid)
            except (KeyError, StopIteration, ValueError):
                continue

        time.sleep(0.4)   # stay polite

    return matches


def fetch_football_data(api_key: str) -> list[dict]:
    """
    Fetch completed WC 2026 matches from football-data.org v4.
    Returns an empty list if the competition is not yet available under code 'WC'.
    """
    url     = "https://api.football-data.org/v4/competitions/WC/matches?status=FINISHED"
    headers = {**_HEADERS, "X-Auth-Token": api_key}
    try:
        r = requests.get(url, timeout=20, headers=headers)
        r.raise_for_status()
    except requests.HTTPError as exc:
        code = exc.response.status_code if exc.response is not None else "?"
        print(f"  [WARN] football-data.org returned HTTP {code}; falling back to ESPN.", file=sys.stderr)
        return []
    except Exception as exc:
        print(f"  [WARN] football-data.org: {exc}; falling back to ESPN.", file=sys.stderr)
        return []

    matches = []
    for m in r.json().get("matches", []):
        ft = m.get("score", {}).get("fullTime", {})
        hs, as_ = ft.get("home"), ft.get("away")
        if hs is None or as_ is None:
            continue
        matches.append({
            "id":         f"fd_{m['id']}",
            "home":       m["homeTeam"]["name"],
            "away":       m["awayTeam"]["name"],
            "home_score": int(hs),
            "away_score": int(as_),
            "date":       m["utcDate"][:10],
        })
    return matches


def fetch_results(api_key: str | None, debug: bool = False) -> list[dict]:
    """Fetch all completed WC 2026 matches; football-data.org preferred."""
    if api_key:
        print("[INFO] Fetching from football-data.org …", end=" ", flush=True)
        results = fetch_football_data(api_key)
        if results:
            print(f"{len(results)} completed match(es) found.")
            return results
        print()

    print("[INFO] Fetching from ESPN …", end=" ", flush=True)
    results = fetch_espn()
    print(f"{len(results)} completed match(es) found.")

    if debug:
        unknown = set()
        for r in results:
            for name in (r["home"], r["away"]):
                cn = normalise(name)
                if cn not in TEAM_OWNER:
                    unknown.add(name)
        if unknown:
            print(f"\n[DEBUG] Unrecognised team names: {sorted(unknown)}")

    return results


# ── State management ───────────────────────────────────────────────────────────

def load_state() -> dict:
    if PROCESSED_FILE.exists():
        return json.loads(PROCESSED_FILE.read_text(encoding="utf-8"))
    return {"matches": {}}


def save_state(state: dict) -> None:
    PROCESSED_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ── Points calculation ─────────────────────────────────────────────────────────

def _awards(home: str, away: str, hs: int, as_: int) -> list[list]:
    """Return [[player, pts, canonical_team, outcome], …] for one match."""
    hc = normalise(home)
    ac = normalise(away)

    if hs > as_:
        h_outcome, a_outcome = "W", "L"
        h_pts,     a_pts     = 3,   0
    elif hs < as_:
        h_outcome, a_outcome = "L", "W"
        h_pts,     a_pts     = 0,   3
    else:
        h_outcome = a_outcome = "D"
        h_pts     = a_pts     = 1

    out = []
    hp = TEAM_OWNER.get(hc)
    ap = TEAM_OWNER.get(ac)
    if hp:
        out.append([hp, h_pts, hc, h_outcome])
    if ap:
        out.append([ap, a_pts, ac, a_outcome])
    return out


def process_results(results: list[dict], state: dict) -> list[dict]:
    """Add new completed matches to state. Returns only newly added records."""
    new: list[dict] = []
    for r in results:
        mid = r["id"]
        if mid in state["matches"]:
            continue

        awards = _awards(r["home"], r["away"], r["home_score"], r["away_score"])

        # Skip matches where neither team is in the sweepstake
        if not awards:
            continue

        record = {
            "home":           r["home"],
            "away":           r["away"],
            "home_canonical": normalise(r["home"]),
            "away_canonical": normalise(r["away"]),
            "home_score":     r["home_score"],
            "away_score":     r["away_score"],
            "date":           r["date"],
            "awards":         awards,
        }
        state["matches"][mid] = record
        new.append(record)

    return new


# ── Standings ──────────────────────────────────────────────────────────────────

def compute_standings(state: dict) -> dict:
    scores:       dict[str, int]    = {p: 0 for p in PLAYERS}
    team_pts:     dict[str, int]    = {t: 0 for t in TEAM_OWNER}
    team_results: dict[str, list]   = {t: [] for t in TEAM_OWNER}

    for match in state["matches"].values():
        for award in match["awards"]:
            player, pts, team, outcome = award
            scores[player]   += pts
            team_pts[team]   += pts
            team_results[team].append({
                "date":    match["date"],
                "home":    match["home"],
                "away":    match["away"],
                "score":   f"{match['home_score']}-{match['away_score']}",
                "outcome": outcome,
                "pts":     pts,
            })

    return {"scores": scores, "team_pts": team_pts, "team_results": team_results}


# ── Terminal summary ───────────────────────────────────────────────────────────

def print_summary(new_matches: list[dict], standings: dict) -> None:
    sep = "─" * 55

    if new_matches:
        print(f"\n{sep}")
        print(f"  NEW RESULTS  ({len(new_matches)})")
        print(sep)
        for m in sorted(new_matches, key=lambda x: x["date"]):
            print(
                f"  {m['date']}  "
                f"{m['home']} {m['home_score']}-{m['away_score']} {m['away']}"
            )
            for award in m["awards"]:
                player, pts, team, outcome = award
                tick = "+" if pts > 0 else " "
                print(f"    {tick} {player:6}  {team}  {outcome}  +{pts}pt")
    else:
        print("\n  No new results since last run.")

    print(f"\n{sep}")
    print("  STANDINGS")
    print(sep)
    ranked = sorted(standings["scores"].items(), key=lambda x: x[1], reverse=True)
    for rank, (player, pts) in enumerate(ranked, 1):
        bar = "=" * pts
        print(f"  {rank}.  {player:<8}  {pts:3} pts  {bar}")
    print(f"{sep}\n")


# ── HTML generation ────────────────────────────────────────────────────────────

_PLAYER_COLORS = {
    "Luis":   "#e53935",
    "Isla":   "#9c27b0",
    "Mummy":  "#00897b",
    "Daddy":  "#1e88e5",
}

_OUTCOME_COLOR = {"W": "#4caf50", "D": "#ffa726", "L": "#ef5350"}


def _html_leaderboard(scores: dict) -> str:
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    rows = []
    for rank, (player, pts) in enumerate(ranked, 1):
        color = _PLAYER_COLORS.get(player, "#4db8ff")
        rows.append(
            f'<div class="lb-row">'
            f'<span class="rank">#{rank}</span>'
            f'<span class="player-name" style="color:{color}">{player}</span>'
            f'<span class="pts-val">{pts}<span class="pts-label"> pts</span></span>'
            f'</div>'
        )
    return "\n    ".join(rows)


def _html_team_card(team: str, pts: int, results: list) -> str:
    player = TEAM_OWNER.get(team, "")
    color  = _PLAYER_COLORS.get(player, "#1a3a6b")
    cls    = "team-card has-result" if results else "team-card"

    match_lines = []
    for r in sorted(results, key=lambda x: x["date"]):
        oc    = r["outcome"]
        oc_c  = _OUTCOME_COLOR.get(oc, "#8892a4")
        match_lines.append(
            f'<div class="team-match">'
            f'<span style="color:{oc_c};font-weight:700">{oc}</span> '
            f'{r["score"]} &middot; +{r["pts"]}pt'
            f'</div>'
        )

    if not match_lines:
        match_lines = ['<div class="team-match no-result">No results yet</div>']

    pts_color = color if results else "#2a4060"
    return (
        f'<div class="{cls}">'
        f'<div class="team-name">{team}</div>'
        f'<div class="team-pts" style="color:{pts_color}">{pts} pts</div>'
        + "".join(match_lines)
        + "</div>"
    )


def _html_player_section(
    player: str,
    scores: dict,
    team_pts: dict,
    team_results: dict,
) -> str:
    color  = _PLAYER_COLORS.get(player, "#1a3a6b")
    total  = scores[player]
    cards  = "".join(
        _html_team_card(t, team_pts.get(t, 0), team_results.get(t, []))
        for t in PLAYERS[player]
    )
    return (
        f'<div class="player-section">'
        f'<div class="player-header" style="border-left:4px solid {color}">'
        f'{player} &mdash; {total} pts'
        f'</div>'
        f'<div class="teams-grid">{cards}</div>'
        f'</div>'
    )


def generate_html(standings: dict, state: dict) -> str:
    from datetime import datetime

    scores       = standings["scores"]
    team_pts     = standings["team_pts"]
    team_results = standings["team_results"]

    leaderboard = _html_leaderboard(scores)
    ranked_players = sorted(PLAYER_ORDER, key=lambda p: scores[p], reverse=True)
    sections = "".join(
        _html_player_section(p, scores, team_pts, team_results)
        for p in ranked_players
    )

    n_matches = len(state["matches"])
    updated   = datetime.now().strftime("%-d %b %Y at %H:%M")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>WC 2026 Family Sweepstake</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #04101f;
      color: #c8d8f0;
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      min-height: 100vh;
    }}
    .container {{ max-width: 960px; margin: 0 auto; padding: 32px 16px 60px; }}

    /* header */
    .header {{ text-align: center; margin-bottom: 40px; }}
    .header h1 {{
      font-size: clamp(1.5rem, 4vw, 2.2rem);
      font-weight: 800;
      color: #ffd700;
      letter-spacing: -0.5px;
    }}
    .header .meta {{ color: #3a5070; font-size: 0.85rem; margin-top: 6px; }}

    /* leaderboard */
    .leaderboard-wrap {{
      background: #0a1828;
      border-radius: 14px;
      overflow: hidden;
      margin-bottom: 44px;
      border: 1px solid #162840;
    }}
    .lb-title {{
      background: #0d2040;
      padding: 11px 20px;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      color: #3a5070;
    }}
    .lb-row {{
      display: flex;
      align-items: center;
      padding: 15px 20px;
      border-bottom: 1px solid #162840;
      gap: 14px;
    }}
    .lb-row:last-child {{ border-bottom: none; }}
    .rank {{ width: 34px; font-size: 1.2rem; font-weight: 800; color: #3a5070; }}
    .lb-row:first-child .rank {{ color: #ffd700; }}
    .player-name {{ flex: 1; font-size: 1.15rem; font-weight: 700; }}
    .pts-val {{ font-size: 1.5rem; font-weight: 800; color: #4db8ff; }}
    .pts-label {{ font-size: 0.7rem; color: #3a5070; font-weight: 400; }}

    /* player sections */
    .player-section {{ margin-bottom: 28px; }}
    .player-header {{
      padding: 11px 16px;
      background: #0a1828;
      border-radius: 10px 10px 0 0;
      font-size: 1rem;
      font-weight: 700;
      color: #a0b8d0;
    }}
    .teams-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
      gap: 8px;
      padding: 10px;
      background: #060e1c;
      border-radius: 0 0 10px 10px;
      border: 1px solid #162840;
      border-top: none;
    }}
    .team-card {{
      background: #0a1828;
      border-radius: 8px;
      padding: 10px 12px;
      border-top: 3px solid #162840;
    }}
    .team-card.has-result {{ border-top-color: #4db8ff; }}
    .team-name {{ font-size: 0.82rem; font-weight: 600; color: #7090b0; margin-bottom: 3px; }}
    .team-pts {{ font-size: 1.1rem; font-weight: 800; margin-bottom: 5px; }}
    .team-match {{ font-size: 0.72rem; color: #5a7090; margin-top: 2px; }}
    .team-match.no-result {{ color: #2a3a50; }}

    /* footer */
    .footer {{ text-align: center; color: #1a2a3a; font-size: 0.75rem; margin-top: 36px; }}
  </style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>WC 2026 Family Sweepstake</h1>
    <div class="meta">{n_matches} result{'' if n_matches == 1 else 's'} processed &middot; updated {updated}</div>
  </div>

  <div class="leaderboard-wrap">
    <div class="lb-title">Current Standings</div>
    {leaderboard}
  </div>

  {sections}

  <div class="footer">Updated automatically by sweepstake.py</div>
</div>
</body>
</html>"""


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    args  = set(sys.argv[1:])
    reset = "--reset" in args
    debug = "--debug" in args

    if reset:
        if PROCESSED_FILE.exists():
            PROCESSED_FILE.unlink()
            print("[INFO] State cleared — recalculating from scratch.")

    # Load or prompt for API key
    api_key = load_api_key()
    if api_key is None and sys.stdin.isatty():
        api_key = prompt_for_api_key()

    # Fetch
    results = fetch_results(api_key, debug=debug)

    # Process
    state = load_state()
    new_matches = process_results(results, state)
    save_state(state)

    # Standings
    standings = compute_standings(state)

    # Output
    print_summary(new_matches, standings)

    html = generate_html(standings, state)
    STANDINGS_HTML.write_text(html, encoding="utf-8")
    print(f"[INFO] Standings written to {STANDINGS_HTML}")


if __name__ == "__main__":
    main()
