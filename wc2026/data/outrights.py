"""
Outright "to win the World Cup 2026" market odds (decimal).

These are approximate pre-tournament market levels for the leading contenders,
used to compare the tournament simulator's champion% against the market and
flag outright value. They are estimates [E] of typical bookmaker prices, not a
live scrape — the outright book also carries a large favourite-longshot margin
(overround ~130–160% across the full 48), so probabilities are vig-stripped by
normalising the listed teams in `tournament.outright_value`.

src: E = estimated market level.
"""

OUTRIGHT_ODDS: dict[str, dict] = {
    "Spain":         {"win": 6.0,   "src": "E"},
    "France":        {"win": 6.5,   "src": "E"},
    "England":       {"win": 7.0,   "src": "E"},
    "Argentina":     {"win": 8.0,   "src": "E"},
    "Brazil":        {"win": 9.0,   "src": "E"},
    "Germany":       {"win": 13.0,  "src": "E"},
    "Portugal":      {"win": 15.0,  "src": "E"},
    "Netherlands":   {"win": 15.0,  "src": "E"},
    "Belgium":       {"win": 29.0,  "src": "E"},
    "Uruguay":       {"win": 34.0,  "src": "E"},
    "Morocco":       {"win": 34.0,  "src": "E"},
    "Croatia":       {"win": 41.0,  "src": "E"},
    "United States": {"win": 41.0,  "src": "E"},
    "Colombia":      {"win": 51.0,  "src": "E"},
    "Mexico":        {"win": 51.0,  "src": "E"},
    "Japan":         {"win": 67.0,  "src": "E"},
    "Switzerland":   {"win": 67.0,  "src": "E"},
    "Senegal":       {"win": 67.0,  "src": "E"},
    "Norway":        {"win": 67.0,  "src": "E"},
    "Austria":       {"win": 81.0,  "src": "E"},
    "Ecuador":       {"win": 101.0, "src": "E"},
    "Korea Republic":{"win": 151.0, "src": "E"},
    "Australia":     {"win": 151.0, "src": "E"},
    "Egypt":         {"win": 151.0, "src": "E"},
}
