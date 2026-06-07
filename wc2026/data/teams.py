"""
WC2026 team data extracted from ScoutingStats.ai nation pages.

All stats are per-game averages from international matches ranked vs WC field.
Keys: att (goals for/game), defence (goals against/game), sot (shots on target/game),
      cs (clean sheets total), shots (total shots/game), games (sample size), group.
"""

TEAMS: dict[str, dict] = {
    # ── Group A ──────────────────────────────────────────────────────────────
    "Mexico": {
        "att": 1.38, "defence": 0.94, "sot": 4.1, "cs": 9,
        "shots": 11.4, "games": 16, "group": "A", "host": True,
    },
    "South Africa": {
        "att": 1.88, "defence": 0.76, "sot": 5.5, "cs": 11,
        "shots": 15.1, "games": 25, "group": "A",
    },
    "Korea Republic": {
        "att": 1.95, "defence": 0.86, "sot": 4.5, "cs": 12,
        "shots": 11.7, "games": 22, "group": "A",
    },
    "Czech Republic": {
        "att": 1.90, "defence": 1.15, "sot": 5.2, "cs": 8,
        "shots": 14.3, "games": 20, "group": "A",
    },

    # ── Group B ──────────────────────────────────────────────────────────────
    "Canada": {
        "att": 1.25, "defence": 0.42, "sot": 4.3, "cs": 9,
        "shots": 11.2, "games": 12, "group": "B", "host": True,
    },
    "Qatar": {
        "att": 1.24, "defence": 1.90, "sot": 3.1, "cs": 3,
        "shots": 8.9, "games": 21, "group": "B",
    },
    "Switzerland": {
        "att": 2.05, "defence": 1.32, "sot": 4.8, "cs": 6,
        "shots": 11.9, "games": 19, "group": "B",
    },
    "Bosnia and Herzegovina": {
        "att": 1.47, "defence": 1.53, "sot": 4.2, "cs": 5,
        "shots": 12.6, "games": 19, "group": "B",
    },

    # ── Group C ──────────────────────────────────────────────────────────────
    "Brazil": {
        "att": 1.89, "defence": 1.00, "sot": 4.8, "cs": 7,
        "shots": 13.5, "games": 19, "group": "C",
    },
    "Morocco": {
        "att": 2.71, "defence": 0.25, "sot": 6.0, "cs": 21,
        "shots": 16.1, "games": 28, "group": "C",
    },
    "Haiti": {
        "att": 2.00, "defence": 1.07, "sot": 5.3, "cs": 7,
        "shots": 13.1, "games": 14, "group": "C",
    },
    "Scotland": {
        "att": 1.58, "defence": 1.26, "sot": 4.5, "cs": 6,
        "shots": 11.4, "games": 19, "group": "C",
    },

    # ── Group D ──────────────────────────────────────────────────────────────
    "United States": {
        "att": 1.85, "defence": 1.69, "sot": 5.2, "cs": 2,
        "shots": 12.5, "games": 13, "group": "D", "host": True,
    },
    "Türkiye": {
        "att": 2.11, "defence": 1.11, "sot": 5.2, "cs": 8,
        "shots": 16.2, "games": 19, "group": "D",
    },
    "Paraguay": {
        "att": 1.11, "defence": 0.89, "sot": 3.8, "cs": 8,
        "shots": 9.9, "games": 18, "group": "D",
    },
    "Australia": {
        "att": 1.67, "defence": 0.76, "sot": 3.2, "cs": 9,
        "shots": 8.0, "games": 21, "group": "D",
    },

    # ── Group E ──────────────────────────────────────────────────────────────
    "Germany": {
        "att": 2.63, "defence": 1.00, "sot": 6.7, "cs": 8,
        "shots": 17.8, "games": 19, "group": "E",
    },
    "Curacao": {
        "att": 2.14, "defence": 1.29, "sot": 5.7, "cs": 6,
        "shots": 13.5, "games": 14, "group": "E",
    },
    "Côte d'Ivoire": {
        "att": 1.73, "defence": 0.46, "sot": 4.3, "cs": 17,
        "shots": 11.8, "games": 26, "group": "E",
    },
    "Ecuador": {
        "att": 0.89, "defence": 0.37, "sot": 4.1, "cs": 12,
        "shots": 11.1, "games": 19, "group": "E",
    },

    # ── Group F ──────────────────────────────────────────────────────────────
    "Sweden": {
        "att": 2.15, "defence": 1.45, "sot": 6.0, "cs": 4,
        "shots": 15.2, "games": 20, "group": "F",
    },
    "Netherlands": {
        "att": 2.53, "defence": 1.00, "sot": 5.6, "cs": 6,
        "shots": 15.5, "games": 19, "group": "F",
    },
    "Japan": {
        "att": 2.52, "defence": 0.43, "sot": 4.8, "cs": 15,
        "shots": 12.3, "games": 21, "group": "F",
    },
    "Tunisia": {
        "att": 1.41, "defence": 0.85, "sot": 4.0, "cs": 11,
        "shots": 9.9, "games": 27, "group": "F",
    },

    # ── Group G ──────────────────────────────────────────────────────────────
    "Belgium": {
        "att": 2.47, "defence": 1.16, "sot": 6.5, "cs": 6,
        "shots": 17.7, "games": 19, "group": "G",
    },
    "Egypt": {
        "att": 1.52, "defence": 0.52, "sot": 4.3, "cs": 18,
        "shots": 9.4, "games": 29, "group": "G",
    },
    "Iran": {
        "att": 1.84, "defence": 0.79, "sot": 4.6, "cs": 10,
        "shots": 10.5, "games": 19, "group": "G",
    },
    "New Zealand": {
        "att": 2.38, "defence": 1.25, "sot": 4.4, "cs": 5,
        "shots": 10.1, "games": 16, "group": "G",
    },

    # ── Group H ──────────────────────────────────────────────────────────────
    "Spain": {
        "att": 2.63, "defence": 0.95, "sot": 7.8, "cs": 10,
        "shots": 19.9, "games": 19, "group": "H",
    },
    "Saudi Arabia": {
        "att": 1.00, "defence": 1.09, "sot": 3.1, "cs": 9,
        "shots": 10.1, "games": 23, "group": "H",
    },
    "Cape Verde Islands": {
        "att": 1.32, "defence": 1.05, "sot": 3.4, "cs": 9,
        "shots": 9.2, "games": 22, "group": "H",
    },
    "Uruguay": {
        "att": 0.78, "defence": 0.78, "sot": 2.6, "cs": 10,
        "shots": 9.8, "games": 18, "group": "H",
    },

    # ── Group I ──────────────────────────────────────────────────────────────
    "France": {
        "att": 2.21, "defence": 1.11, "sot": 6.5, "cs": 7,
        "shots": 17.8, "games": 19, "group": "I",
    },
    "Norway": {
        "att": 3.05, "defence": 0.84, "sot": 6.1, "cs": 9,
        "shots": 16.8, "games": 19, "group": "I",
    },
    "Iraq": {
        "att": 1.11, "defence": 0.79, "sot": 2.9, "cs": 9,
        "shots": 8.0, "games": 19, "group": "I",
    },
    "Senegal": {
        "att": 2.03, "defence": 0.60, "sot": 5.8, "cs": 18,
        "shots": 12.4, "games": 30, "group": "I",
    },

    # ── Group J ──────────────────────────────────────────────────────────────
    "Argentina": {
        "att": 2.29, "defence": 0.53, "sot": 5.2, "cs": 10,
        "shots": 12.2, "games": 17, "group": "J",
    },
    "Algeria": {
        "att": 2.33, "defence": 0.63, "sot": 5.0, "cs": 15,
        "shots": 9.7, "games": 27, "group": "J",
    },
    "Austria": {
        "att": 2.32, "defence": 0.68, "sot": 6.1, "cs": 8,
        "shots": 14.2, "games": 19, "group": "J",
    },
    "Jordan": {
        "att": 1.42, "defence": 1.17, "sot": 4.2, "cs": 8,
        "shots": 10.1, "games": 24, "group": "J",
    },

    # ── Group K ──────────────────────────────────────────────────────────────
    "Portugal": {
        "att": 2.44, "defence": 1.00, "sot": 6.2, "cs": 5,
        "shots": 18.7, "games": 18, "group": "K",
    },
    "Colombia": {
        "att": 1.89, "defence": 1.16, "sot": 5.6, "cs": 6,
        "shots": 13.7, "games": 19, "group": "K",
    },
    "Congo DR": {
        "att": 1.36, "defence": 0.48, "sot": 3.5, "cs": 16,
        "shots": 9.0, "games": 25, "group": "K",
    },
    "Uzbekistan": {
        "att": 1.25, "defence": 0.65, "sot": 4.2, "cs": 13,
        "shots": 12.4, "games": 20, "group": "K",
    },

    # ── Group L ──────────────────────────────────────────────────────────────
    "England": {
        "att": 2.39, "defence": 0.44, "sot": 6.6, "cs": 13,
        "shots": 16.9, "games": 18, "group": "L",
    },
    "Croatia": {
        "att": 2.05, "defence": 1.05, "sot": 6.5, "cs": 7,
        "shots": 17.6, "games": 19, "group": "L",
    },
    "Ghana": {
        "att": 1.52, "defence": 1.19, "sot": 3.8, "cs": 7,
        "shots": 9.3, "games": 21, "group": "L",
    },
    "Panama": {
        "att": 1.69, "defence": 1.38, "sot": 4.5, "cs": 6,
        "shots": 12.1, "games": 16, "group": "L",
    },
}

# Convenience lookup: group → list of team names
GROUPS: dict[str, list[str]] = {}
for _team, _data in TEAMS.items():
    _g = _data["group"]
    GROUPS.setdefault(_g, []).append(_team)
