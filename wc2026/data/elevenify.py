"""
Elevenify WC2026 group stage predictions.
Source: elevenify.com/p/free-world-cup-2026-predictions

Per match, per team: xg (expected goals), cs (clean sheet prob), win (win prob).
Keys match FIXTURES (home, away) order.
draw = 1 − home_win − away_win
"""

ELEVENIFY: dict[tuple[str, str], dict] = {
    # ── Group A ─────────────────────────────────────────────────────────────
    ("Mexico", "South Africa"): {"home_xg": 1.76, "home_cs": 0.48, "home_win": 0.62, "draw": 0.23, "away_xg": 0.73, "away_cs": 0.17, "away_win": 0.15},
    ("Korea Republic", "Czech Republic"): {"home_xg": 1.01, "home_cs": 0.27, "home_win": 0.29, "draw": 0.28, "away_xg": 1.29, "away_cs": 0.37, "away_win": 0.43},
    ("Mexico", "Korea Republic"): {"home_xg": 1.54, "home_cs": 0.43, "home_win": 0.54, "draw": 0.25, "away_xg": 0.85, "away_cs": 0.21, "away_win": 0.21},
    ("South Africa", "Czech Republic"): {"home_xg": 0.86, "home_cs": 0.23, "home_win": 0.22, "draw": 0.26, "away_xg": 1.47, "away_cs": 0.42, "away_win": 0.52},
    ("Mexico", "Czech Republic"): {"home_xg": 1.34, "home_cs": 0.39, "home_win": 0.46, "draw": 0.28, "away_xg": 0.95, "away_cs": 0.26, "away_win": 0.26},
    ("South Africa", "Korea Republic"): {"home_xg": 1.00, "home_cs": 0.27, "home_win": 0.28, "draw": 0.28, "away_xg": 1.32, "away_cs": 0.37, "away_win": 0.44},
    # ── Group B ─────────────────────────────────────────────────────────────
    ("Canada", "Qatar"): {"home_xg": 1.94, "home_cs": 0.55, "home_win": 0.69, "draw": 0.20, "away_xg": 0.60, "away_cs": 0.14, "away_win": 0.11},
    ("Switzerland", "Bosnia and Herzegovina"): {"home_xg": 1.93, "home_cs": 0.39, "home_win": 0.61, "draw": 0.21, "away_xg": 0.93, "away_cs": 0.15, "away_win": 0.18},
    ("Canada", "Switzerland"): {"home_xg": 0.76, "home_cs": 0.25, "home_win": 0.20, "draw": 0.28, "away_xg": 1.40, "away_cs": 0.47, "away_win": 0.52},
    ("Qatar", "Bosnia and Herzegovina"): {"home_xg": 0.83, "home_cs": 0.09, "home_win": 0.11, "draw": 0.17, "away_xg": 2.38, "away_cs": 0.44, "away_win": 0.72},
    ("Canada", "Bosnia and Herzegovina"): {"home_xg": 1.34, "home_cs": 0.30, "home_win": 0.40, "draw": 0.27, "away_xg": 1.19, "away_cs": 0.26, "away_win": 0.33},
    ("Qatar", "Switzerland"): {"home_xg": 0.48, "home_cs": 0.06, "home_win": 0.04, "draw": 0.11, "away_xg": 2.81, "away_cs": 0.62, "away_win": 0.85},
    # ── Group C ─────────────────────────────────────────────────────────────
    ("Brazil", "Scotland"): {"home_xg": 1.92, "home_cs": 0.51, "home_win": 0.67, "draw": 0.21, "away_xg": 0.68, "away_cs": 0.15, "away_win": 0.12},
    ("Morocco", "Haiti"): {"home_xg": 2.13, "home_cs": 0.48, "home_win": 0.70, "draw": 0.18, "away_xg": 0.73, "away_cs": 0.12, "away_win": 0.12},
    ("Brazil", "Morocco"): {"home_xg": 2.05, "home_cs": 0.48, "home_win": 0.68, "draw": 0.20, "away_xg": 0.73, "away_cs": 0.13, "away_win": 0.12},
    ("Scotland", "Haiti"): {"home_xg": 1.98, "home_cs": 0.51, "home_win": 0.68, "draw": 0.20, "away_xg": 0.68, "away_cs": 0.14, "away_win": 0.12},
    ("Brazil", "Haiti"): {"home_xg": 3.78, "home_cs": 0.63, "home_win": 0.93, "draw": 0.05, "away_xg": 0.46, "away_cs": 0.02, "away_win": 0.02},
    ("Scotland", "Morocco"): {"home_xg": 1.08, "home_cs": 0.34, "home_win": 0.35, "draw": 0.30, "away_xg": 1.08, "away_cs": 0.34, "away_win": 0.35},
    # ── Group D ─────────────────────────────────────────────────────────────
    ("United States", "Paraguay"): {"home_xg": 1.34, "home_cs": 0.23, "home_win": 0.35, "draw": 0.25, "away_xg": 1.47, "away_cs": 0.26, "away_win": 0.40},
    ("Türkiye", "Australia"): {"home_xg": 1.65, "home_cs": 0.44, "home_win": 0.57, "draw": 0.25, "away_xg": 0.81, "away_cs": 0.19, "away_win": 0.18},
    ("United States", "Türkiye"): {"home_xg": 1.08, "home_cs": 0.16, "home_win": 0.22, "draw": 0.23, "away_xg": 1.82, "away_cs": 0.34, "away_win": 0.55},
    ("Paraguay", "Australia"): {"home_xg": 1.32, "home_cs": 0.36, "home_win": 0.44, "draw": 0.27, "away_xg": 1.01, "away_cs": 0.27, "away_win": 0.29},
    ("United States", "Australia"): {"home_xg": 1.49, "home_cs": 0.29, "home_win": 0.43, "draw": 0.25, "away_xg": 1.25, "away_cs": 0.22, "away_win": 0.32},
    ("Paraguay", "Türkiye"): {"home_xg": 0.95, "home_cs": 0.23, "home_win": 0.24, "draw": 0.26, "away_xg": 1.48, "away_cs": 0.39, "away_win": 0.50},
    # ── Group E ─────────────────────────────────────────────────────────────
    ("Germany", "Curacao"): {"home_xg": 4.01, "home_cs": 0.57, "home_win": 0.93, "draw": 0.05, "away_xg": 0.57, "away_cs": 0.02, "away_win": 0.02},
    ("Côte d'Ivoire", "Ecuador"): {"home_xg": 0.75, "home_cs": 0.24, "home_win": 0.20, "draw": 0.27, "away_xg": 1.42, "away_cs": 0.47, "away_win": 0.53},
    ("Germany", "Côte d'Ivoire"): {"home_xg": 2.13, "home_cs": 0.43, "home_win": 0.67, "draw": 0.19, "away_xg": 0.84, "away_cs": 0.12, "away_win": 0.14},
    ("Curacao", "Ecuador"): {"home_xg": 0.51, "home_cs": 0.07, "home_win": 0.05, "draw": 0.12, "away_xg": 2.67, "away_cs": 0.60, "away_win": 0.83},
    ("Germany", "Ecuador"): {"home_xg": 1.37, "home_cs": 0.36, "home_win": 0.45, "draw": 0.27, "away_xg": 1.01, "away_cs": 0.25, "away_win": 0.28},
    ("Curacao", "Côte d'Ivoire"): {"home_xg": 0.80, "home_cs": 0.11, "home_win": 0.12, "draw": 0.18, "away_xg": 2.21, "away_cs": 0.45, "away_win": 0.70},
    # ── Group F ─────────────────────────────────────────────────────────────
    ("Sweden", "Tunisia"): {"home_xg": 1.39, "home_cs": 0.36, "home_win": 0.46, "draw": 0.27, "away_xg": 1.02, "away_cs": 0.25, "away_win": 0.27},
    ("Netherlands", "Japan"): {"home_xg": 1.48, "home_cs": 0.35, "home_win": 0.47, "draw": 0.26, "away_xg": 1.05, "away_cs": 0.23, "away_win": 0.27},
    ("Sweden", "Netherlands"): {"home_xg": 0.99, "home_cs": 0.20, "home_win": 0.23, "draw": 0.25, "away_xg": 1.62, "away_cs": 0.37, "away_win": 0.52},
    ("Tunisia", "Japan"): {"home_xg": 0.93, "home_cs": 0.23, "home_win": 0.24, "draw": 0.26, "away_xg": 1.47, "away_cs": 0.40, "away_win": 0.50},
    ("Sweden", "Japan"): {"home_xg": 1.15, "home_cs": 0.26, "home_win": 0.32, "draw": 0.27, "away_xg": 1.34, "away_cs": 0.32, "away_win": 0.41},
    ("Tunisia", "Netherlands"): {"home_xg": 0.80, "home_cs": 0.17, "home_win": 0.16, "draw": 0.23, "away_xg": 1.78, "away_cs": 0.45, "away_win": 0.61},
    # ── Group G ─────────────────────────────────────────────────────────────
    ("Belgium", "New Zealand"): {"home_xg": 2.45, "home_cs": 0.52, "home_win": 0.77, "draw": 0.15, "away_xg": 0.65, "away_cs": 0.09, "away_win": 0.08},
    ("Egypt", "Iran"): {"home_xg": 1.27, "home_cs": 0.32, "home_win": 0.39, "draw": 0.28, "away_xg": 1.15, "away_cs": 0.28, "away_win": 0.33},
    ("Belgium", "Egypt"): {"home_xg": 1.70, "home_cs": 0.41, "home_win": 0.57, "draw": 0.24, "away_xg": 0.89, "away_cs": 0.18, "away_win": 0.19},
    ("New Zealand", "Iran"): {"home_xg": 0.93, "home_cs": 0.19, "home_win": 0.21, "draw": 0.25, "away_xg": 1.66, "away_cs": 0.39, "away_win": 0.54},
    ("Belgium", "Iran"): {"home_xg": 1.76, "home_cs": 0.44, "home_win": 0.59, "draw": 0.24, "away_xg": 0.83, "away_cs": 0.17, "away_win": 0.17},
    ("New Zealand", "Egypt"): {"home_xg": 0.90, "home_cs": 0.17, "home_win": 0.19, "draw": 0.23, "away_xg": 1.76, "away_cs": 0.41, "away_win": 0.58},
    # ── Group H ─────────────────────────────────────────────────────────────
    ("Spain", "Saudi Arabia"): {"home_xg": 3.21, "home_cs": 0.67, "home_win": 0.90, "draw": 0.08, "away_xg": 0.40, "away_cs": 0.04, "away_win": 0.02},
    ("Cape Verde Islands", "Uruguay"): {"home_xg": 0.59, "home_cs": 0.09, "home_win": 0.07, "draw": 0.15, "away_xg": 2.42, "away_cs": 0.56, "away_win": 0.78},
    ("Spain", "Cape Verde Islands"): {"home_xg": 3.67, "home_cs": 0.68, "home_win": 0.93, "draw": 0.06, "away_xg": 0.39, "away_cs": 0.03, "away_win": 0.01},
    ("Saudi Arabia", "Uruguay"): {"home_xg": 0.60, "home_cs": 0.12, "home_win": 0.09, "draw": 0.18, "away_xg": 2.12, "away_cs": 0.55, "away_win": 0.73},
    ("Spain", "Uruguay"): {"home_xg": 1.61, "home_cs": 0.50, "home_win": 0.59, "draw": 0.25, "away_xg": 0.70, "away_cs": 0.20, "away_win": 0.16},
    ("Saudi Arabia", "Cape Verde Islands"): {"home_xg": 1.38, "home_cs": 0.31, "home_win": 0.42, "draw": 0.26, "away_xg": 1.17, "away_cs": 0.25, "away_win": 0.32},
    # ── Group I ─────────────────────────────────────────────────────────────
    ("France", "Iraq"): {"home_xg": 3.27, "home_cs": 0.64, "home_win": 0.90, "draw": 0.07, "away_xg": 0.45, "away_cs": 0.04, "away_win": 0.03},
    ("Norway", "Senegal"): {"home_xg": 1.49, "home_cs": 0.39, "home_win": 0.50, "draw": 0.26, "away_xg": 0.95, "away_cs": 0.22, "away_win": 0.24},
    ("France", "Norway"): {"home_xg": 1.44, "home_cs": 0.38, "home_win": 0.48, "draw": 0.27, "away_xg": 0.96, "away_cs": 0.24, "away_win": 0.25},
    ("Iraq", "Senegal"): {"home_xg": 0.70, "home_cs": 0.12, "home_win": 0.11, "draw": 0.18, "away_xg": 2.15, "away_cs": 0.50, "away_win": 0.71},
    ("France", "Senegal"): {"home_xg": 1.78, "home_cs": 0.47, "home_win": 0.62, "draw": 0.23, "away_xg": 0.75, "away_cs": 0.17, "away_win": 0.15},
    ("Iraq", "Norway"): {"home_xg": 0.57, "home_cs": 0.06, "home_win": 0.05, "draw": 0.12, "away_xg": 2.74, "away_cs": 0.57, "away_win": 0.83},
    # ── Group J ─────────────────────────────────────────────────────────────
    ("Argentina", "Jordan"): {"home_xg": 2.62, "home_cs": 0.54, "home_win": 0.80, "draw": 0.13, "away_xg": 0.62, "away_cs": 0.07, "away_win": 0.07},
    ("Algeria", "Austria"): {"home_xg": 1.11, "home_cs": 0.19, "home_win": 0.26, "draw": 0.24, "away_xg": 1.64, "away_cs": 0.33, "away_win": 0.50},
    ("Argentina", "Algeria"): {"home_xg": 1.98, "home_cs": 0.45, "home_win": 0.65, "draw": 0.21, "away_xg": 0.80, "away_cs": 0.14, "away_win": 0.14},
    ("Jordan", "Austria"): {"home_xg": 0.86, "home_cs": 0.11, "home_win": 0.14, "draw": 0.19, "away_xg": 2.17, "away_cs": 0.42, "away_win": 0.67},
    ("Argentina", "Austria"): {"home_xg": 1.61, "home_cs": 0.38, "home_win": 0.53, "draw": 0.24, "away_xg": 0.97, "away_cs": 0.20, "away_win": 0.23},
    ("Jordan", "Algeria"): {"home_xg": 1.05, "home_cs": 0.17, "home_win": 0.22, "draw": 0.23, "away_xg": 1.79, "away_cs": 0.35, "away_win": 0.55},
    # ── Group K ─────────────────────────────────────────────────────────────
    ("Portugal", "Congo DR"): {"home_xg": 2.62, "home_cs": 0.55, "home_win": 0.80, "draw": 0.14, "away_xg": 0.61, "away_cs": 0.07, "away_win": 0.06},
    ("Colombia", "Uzbekistan"): {"home_xg": 2.14, "home_cs": 0.54, "home_win": 0.73, "draw": 0.18, "away_xg": 0.61, "away_cs": 0.12, "away_win": 0.09},
    ("Portugal", "Colombia"): {"home_xg": 1.33, "home_cs": 0.39, "home_win": 0.46, "draw": 0.27, "away_xg": 0.94, "away_cs": 0.27, "away_win": 0.27},
    ("Congo DR", "Uzbekistan"): {"home_xg": 1.37, "home_cs": 0.30, "home_win": 0.41, "draw": 0.26, "away_xg": 1.20, "away_cs": 0.25, "away_win": 0.33},
    ("Portugal", "Uzbekistan"): {"home_xg": 2.76, "home_cs": 0.57, "home_win": 0.83, "draw": 0.12, "away_xg": 0.56, "away_cs": 0.06, "away_win": 0.05},
    ("Congo DR", "Colombia"): {"home_xg": 0.66, "home_cs": 0.13, "home_win": 0.11, "draw": 0.20, "away_xg": 2.03, "away_cs": 0.52, "away_win": 0.69},
    # ── Group L ─────────────────────────────────────────────────────────────
    ("England", "Ghana"): {"home_xg": 2.09, "home_cs": 0.48, "home_win": 0.69, "draw": 0.19, "away_xg": 0.72, "away_cs": 0.12, "away_win": 0.12},
    ("Croatia", "Panama"): {"home_xg": 2.17, "home_cs": 0.44, "home_win": 0.68, "draw": 0.19, "away_xg": 0.82, "away_cs": 0.11, "away_win": 0.13},
    ("England", "Croatia"): {"home_xg": 1.54, "home_cs": 0.41, "home_win": 0.52, "draw": 0.26, "away_xg": 0.90, "away_cs": 0.21, "away_win": 0.22},
    ("Ghana", "Panama"): {"home_xg": 1.74, "home_cs": 0.33, "home_win": 0.52, "draw": 0.24, "away_xg": 1.11, "away_cs": 0.17, "away_win": 0.24},
    ("England", "Panama"): {"home_xg": 2.83, "home_cs": 0.53, "home_win": 0.83, "draw": 0.11, "away_xg": 0.63, "away_cs": 0.06, "away_win": 0.06},
    ("Ghana", "Croatia"): {"home_xg": 0.95, "home_cs": 0.20, "home_win": 0.22, "draw": 0.25, "away_xg": 1.60, "away_cs": 0.39, "away_win": 0.53},
}
