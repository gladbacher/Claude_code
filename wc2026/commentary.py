"""
Match commentary generator for WC2026 group stage.

Analyses model output, Elevenify benchmark, and market odds to produce
a short best-bet narrative for each fixture.

Usage:
    from wc2026.commentary import get_commentary
    text, best_bet = get_commentary("France", "Norway", res, market_odds, elevenify_entry)
"""

from __future__ import annotations
import math
import random
from typing import Optional

from .data import TEAMS
from .data.elevenify import ELEVENIFY
from .data.odds import MARKET_ODDS
from .model import scorer_probs, find_value, AH_LINES


# ── Helpers ───────────────────────────────────────────────────────────────────

def _rank(team: str) -> int:
    return TEAMS[team].get("fifa_rank", 50)

def _is_host(team: str) -> bool:
    return TEAMS[team].get("host", False)

def _att(team: str) -> float:
    return TEAMS[team]["att"]

def _def(team: str) -> float:
    return TEAMS[team]["defence"]

def _pct(v: float) -> str:
    return f"{v*100:.0f}%"

def _dec(p: float) -> str:
    return f"{1/p:.2f}" if p > 0.01 else "—"

def _best_ah_for_favourite(res: dict) -> tuple[float, float]:
    """Return (line, home_cover_prob) for line nearest 50% home cover."""
    best = min(AH_LINES, key=lambda l: abs(res["ah_home"][l] - 0.50))
    return best, res["ah_home"][best]

def _top_scorer(team: str, lam: float) -> Optional[dict]:
    players = scorer_probs(team, lam, top_n=1)
    return players[0] if players else None

def _edge_markets(home: str, away: str, res: dict) -> list[dict]:
    """Return value markets sorted by edge desc."""
    mo = MARKET_ODDS.get((home, away))
    if not mo:
        return []
    markets = [
        ("Home Win",  res["home_win"],  mo["home"]),
        ("Draw",      res["draw"],       mo["draw"]),
        ("Away Win",  res["away_win"],   mo["away"]),
    ]
    out = []
    for label, mp, odds in markets:
        edge, is_val = find_value(mp, odds)
        out.append({"label": label, "model_p": mp, "odds": odds, "edge": edge, "value": is_val})
    return sorted(out, key=lambda x: x["edge"], reverse=True)


# ── Sentence components ───────────────────────────────────────────────────────

_DOMINANCE_OPENERS = [
    "{fav} look the class act here",
    "{fav} should have too much quality",
    "{fav} enter this one in commanding form",
    "Hard to look past {fav} in this fixture",
    "{fav} are strong favourites for good reason",
]

_CLOSE_OPENERS = [
    "This looks a genuine coin-flip",
    "Difficult to separate these two on paper",
    "Expect a tight, nervy affair",
    "The numbers point to a closely-contested match",
    "Neither side holds a clear edge",
]

_GOALS_HIGH = [
    "Goals look likely — both attacks carry genuine threat.",
    "Combined xG suggests a high-scoring game.",
    "Expect goals at both ends.",
    "Attacking quality on both sides points to a lively contest.",
]

_GOALS_LOW = [
    "Defences are the story here — a tight, low-scoring game expected.",
    "Clean-sheet merchants on both sides; don't expect fireworks.",
    "Under 2.5 goals makes appeal at the fair price.",
    "Cautious, structured football likely from both managers.",
]


def _pick_opener(fav: str | None, gap: float) -> str:
    if fav and gap > 0.45:
        return random.choice(_DOMINANCE_OPENERS).format(fav=fav)
    if gap < 0.15:
        return random.choice(_CLOSE_OPENERS)
    if fav:
        return f"{fav} carry an edge but this won't be a stroll"
    return "A competitive group stage fixture"


# ── Core commentary logic ─────────────────────────────────────────────────────

def get_commentary(
    home: str,
    away: str,
    res: dict,
    seed: int = 0,
) -> tuple[str, str]:
    """
    Return (narrative, best_bet_line).

    narrative   — 2-3 sentences of context
    best_bet_line — e.g. "Best bet: France Win @ 1.65"
    """
    random.seed(seed)

    lh, la = res["lambda_home"], res["lambda_away"]
    hw, dr, aw = res["home_win"], res["draw"], res["away_win"]
    o25, u25 = res["over_25"], 1 - res["over_25"]
    o15 = res["over_15"]
    btts = res["btts"]

    e = ELEVENIFY.get((home, away), {})
    mo = MARKET_ODDS.get((home, away), {})
    edges = _edge_markets(home, away, res)

    rank_h, rank_a = _rank(home), _rank(away)
    fav = home if hw > aw else away if aw > hw else None
    gap = abs(hw - aw)

    # ── Determine narrative angle ─────────────────────────────────────────────

    # 1. Biggest value bet from confirmed/estimated odds
    top_edge = edges[0] if edges else None

    # 2. Goalscorer angle — flag if top scorer > 55%
    top_h = _top_scorer(home, lh)
    top_a = _top_scorer(away, la)
    scorer_angle = None
    if top_h and top_h["prob"] > 0.55:
        scorer_angle = (top_h["name"], top_h["prob"], home)
    elif top_a and top_a["prob"] > 0.55:
        scorer_angle = (top_a["name"], top_a["prob"], away)

    # 3. Goals angle
    high_goals = o25 > 0.62
    low_goals  = o25 < 0.38
    btts_strong = btts > 0.58

    # 4. Elevenify vs model divergence
    el_div = ""
    if e:
        e_hw = e.get("home_win", 0)
        e_aw = e.get("away_win", 0)
        el_draw = e.get("draw", 1 - e_hw - e_aw)
        # Biggest divergence
        divs = [
            (abs(hw - e_hw),  f"model is {_pct(abs(hw-e_hw))} {'more' if hw > e_hw else 'less'} bullish on {home} ({_pct(hw)} vs Elevenify {_pct(e_hw)})"),
            (abs(aw - e_aw),  f"model is {_pct(abs(aw-e_aw))} {'more' if aw > e_aw else 'less'} bullish on {away} ({_pct(aw)} vs Elevenify {_pct(e_aw)})"),
            (abs(dr - el_draw), f"draw more likely than Elevenify suggest ({_pct(dr)} vs {_pct(el_draw)})"),
        ]
        divs.sort(reverse=True)
        if divs[0][0] > 0.12:
            el_div = divs[0][1]

    # ── Build narrative ───────────────────────────────────────────────────────
    sentences = []

    # Opener
    sentences.append(_pick_opener(fav, gap) + ".")

    # xG / model context
    if e:
        xg_str = f"Elevenify project {e.get('home_xg',0):.2f} vs {e.get('away_xg',0):.2f} xG"
        if lh + la > 3.0:
            sentences.append(f"{xg_str} — our model agrees with λ {lh:.2f}/{la:.2f}, pointing to goals.")
        elif lh + la < 2.0:
            sentences.append(f"{xg_str}; our model (λ {lh:.2f}/{la:.2f}) echoes the low-scoring outlook.")
        else:
            sentences.append(f"{xg_str}; model expected goals λ {lh:.2f}/{la:.2f}.")
    else:
        sentences.append(f"Model expected goals: λ {lh:.2f} ({home}) vs λ {la:.2f} ({away}).")

    # Divergence note
    if el_div:
        sentences.append(f"Key divergence: {el_div}.")

    # Scorer note
    if scorer_angle:
        name, prob, team = scorer_angle
        sentences.append(f"{name} is the danger man — {_pct(prob)} anytime scorer given {team}'s attacking weight.")

    # ── Best bet selection ────────────────────────────────────────────────────

    best_bet = _select_best_bet(home, away, res, edges, top_h, top_a, lh, la,
                                 hw, dr, aw, o25, u25, o15, btts, e, mo, fav, gap)

    # Trim to max 3 sentences
    narrative = " ".join(sentences[:3])
    return narrative, best_bet


def _select_best_bet(
    home, away, res, edges, top_h, top_a, lh, la,
    hw, dr, aw, o25, u25, o15, btts, e, mo, fav, gap,
) -> str:
    """Pick the single strongest bet and format it."""

    mo_src = MARKET_ODDS.get((home, away), {}).get("src", "E")

    # Priority 1: confirmed market edge ≥ 8%
    conf_edges = [x for x in edges if x["value"] and x["edge"] >= 0.08
                  and mo_src == "C"]
    if conf_edges:
        b = conf_edges[0]
        odds_str = f"@ {b['odds']:.2f}" if b["odds"] else ""
        src_note = " ★ confirmed odds" if mo_src == "C" else ""
        return (f"Best bet: **{b['label']}** {odds_str} — "
                f"model {_pct(b['model_p'])} vs implied {_pct(1/b['odds'])}, "
                f"+{b['edge']*100:.0f}pp edge{src_note}")

    # Priority 2: any value edge ≥ 5% (confirmed or estimated)
    val_edges = [x for x in edges if x["value"] and x["edge"] >= 0.05]
    if val_edges:
        b = val_edges[0]
        odds_str = f"@ {b['odds']:.2f}" if b["odds"] else ""
        src_note = " [est. odds]" if mo_src == "E" else ""
        return (f"Best bet: **{b['label']}** {odds_str} — "
                f"model {_pct(b['model_p'])} vs market {_pct(1/b['odds'])}{src_note}")

    # Priority 3: strong BTTS
    if btts > 0.62 and mo:
        return (f"Best bet: **Both Teams to Score — Yes** — "
                f"model {_pct(btts)}, fair price {_dec(btts)}")

    # Priority 4: clear O/U angle
    if o25 > 0.68:
        return (f"Best bet: **Over 2.5 Goals** — "
                f"model {_pct(o25)}, fair price {_dec(o25)}")
    if u25 > 0.68:
        return (f"Best bet: **Under 2.5 Goals** — "
                f"model {_pct(u25)}, fair price {_dec(u25)}")

    # Priority 5: Asian Handicap near fair line
    ah_line, ah_prob = _best_ah_for_favourite(res)
    if fav:
        fav_is_home = hw > aw
        if abs(ah_prob - 0.50) < 0.08 and abs(ah_line) >= 0.5:
            side = home if fav_is_home else away
            display_line = ah_line if fav_is_home else -ah_line
            return (f"Best bet: **{side} AH {display_line:+.2f}** — "
                    f"model cover probability {_pct(ah_prob if fav_is_home else res['ah_away'][ah_line])}")

    # Priority 6: anytime scorer
    if top_h and top_h["prob"] > 0.50:
        return (f"Best bet: **{top_h['name']} Anytime Scorer** — "
                f"model {_pct(top_h['prob'])}, fair price {_dec(top_h['prob'])}")
    if top_a and top_a["prob"] > 0.50:
        return (f"Best bet: **{top_a['name']} Anytime Scorer** — "
                f"model {_pct(top_a['prob'])}, fair price {_dec(top_a['prob'])}")

    # Priority 7: plain win/draw recommendation
    if hw > 0.60:
        odds_str = f"@ {mo['home']:.2f}" if mo else f"(fair {_dec(hw)})"
        return f"Best bet: **{home} Win** {odds_str} — model {_pct(hw)}"
    if aw > 0.60:
        odds_str = f"@ {mo['away']:.2f}" if mo else f"(fair {_dec(aw)})"
        return f"Best bet: **{away} Win** {odds_str} — model {_pct(aw)}"
    if dr > 0.30:
        odds_str = f"@ {mo['draw']:.2f}" if mo else f"(fair {_dec(dr)})"
        return f"Best bet: **Draw** {odds_str} — model {_pct(dr)}, balanced contest"

    # Fallback
    if hw >= aw:
        odds_str = f"@ {mo['home']:.2f}" if mo else f"(fair {_dec(hw)})"
        return f"Best bet: **{home} Win** {odds_str} — model {_pct(hw)}"
    odds_str = f"@ {mo['away']:.2f}" if mo else f"(fair {_dec(aw)})"
    return f"Best bet: **{away} Win** {odds_str} — model {_pct(aw)}"


# ── Batch generate for all fixtures ──────────────────────────────────────────

def generate_all_commentary(n_sims: int = 10_000) -> dict[tuple[str, str], tuple[str, str]]:
    """
    Run simulations and generate commentary for all 72 fixtures.
    Returns dict: (home, away) → (narrative, best_bet).
    """
    from .data import FIXTURES
    from .model import simulate_match

    out: dict[tuple[str, str], tuple[str, str]] = {}
    for i, (home, away, md, date) in enumerate(FIXTURES):
        res = simulate_match(home, away, n_sims=n_sims)
        narrative, best_bet = get_commentary(home, away, res, seed=i)
        out[(home, away)] = (narrative, best_bet)
    return out
