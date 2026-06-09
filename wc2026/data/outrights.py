"""
Outright "to win the World Cup 2026" market odds (decimal).

Real market levels aggregated from June 2026 reporting (FOX Sports / FanDuel /
ESPN / SI, via market round-ups just before the opening match). Used to compare
the tournament simulator's champion% against the market and flag outright value.
The full outright book carries a large favourite-longshot margin (overround
well over 100% across 48 teams), so probabilities are vig-stripped by
normalising the listed teams in `tournament.outright_value`.

Longshot prices (Korea/Australia/Egypt) vary widely between books and are
approximate. Decimal = 1 + American/100.

src: C = sourced from June 2026 market reporting.
"""

OUTRIGHT_ODDS: dict[str, dict] = {
    "Spain":         {"win": 5.5,   "src": "C"},   # +450
    "France":        {"win": 5.75,  "src": "C"},   # +475
    "England":       {"win": 7.5,   "src": "C"},   # +650 / 13-2
    "Brazil":        {"win": 9.5,   "src": "C"},   # +850
    "Argentina":     {"win": 10.0,  "src": "C"},   # +900
    "Portugal":      {"win": 11.0,  "src": "C"},   # +1000
    "Germany":       {"win": 15.0,  "src": "C"},   # +1400
    "Netherlands":   {"win": 23.0,  "src": "C"},   # +2200
    "Belgium":       {"win": 36.0,  "src": "C"},   # +3500
    "Norway":        {"win": 36.0,  "src": "C"},   # +3500
    "Colombia":      {"win": 41.0,  "src": "C"},   # +4000
    "Uruguay":       {"win": 51.0,  "src": "C"},   # +5000
    "Morocco":       {"win": 51.0,  "src": "C"},   # +5000
    "USA" :          {"win": 61.0,  "src": "C"},   # +6000  (key normalised below)
    "Japan":         {"win": 66.0,  "src": "C"},   # +6500
    "Switzerland":   {"win": 66.0,  "src": "C"},   # +6500
    "Croatia":       {"win": 81.0,  "src": "C"},   # +8000
    "Mexico":        {"win": 81.0,  "src": "C"},   # +8000
    "Ecuador":       {"win": 81.0,  "src": "C"},   # +8000
    "Senegal":       {"win": 91.0,  "src": "C"},   # +9000
    "Austria":       {"win": 101.0, "src": "C"},   # +10000
    "Egypt":         {"win": 351.0, "src": "C"},   # ~+25000-40000
    "Korea Republic":{"win": 501.0, "src": "C"},   # ~+40000-70000
    "Australia":     {"win": 751.0, "src": "C"},   # ~+25000+ (longshot, approx)
}

# Team-name reconciliation: dataset uses "United States", market uses "USA".
OUTRIGHT_ODDS["United States"] = OUTRIGHT_ODDS.pop("USA")
