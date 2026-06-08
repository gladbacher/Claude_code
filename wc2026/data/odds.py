"""
Average bookmaker 1X2 odds for all 72 WC2026 group stage matches.

Sources (where confirmed):
  C  = confirmed from FanDuel / bet365 / Betfair / Oddschecker (June 2026)
  E  = estimated from FIFA rankings, model output and typical market patterns

Decimal odds include vig (~5%).  Keys match FIXTURES tuple order (home, away).
"""

# fmt: off
MARKET_ODDS: dict[tuple[str, str], dict] = {

    # ── Group A ──────────────────────────────────────────────────────────────
    # Mexico vs SA: FanDuel -250/+360/+700, bet365 -209/+333/+550 → averaged
    ("Mexico",        "South Africa"):       {"home": 1.44, "draw": 4.38, "away": 7.50, "src": "C"},
    ("Korea Republic","Czech Republic"):     {"home": 1.75, "draw": 3.25, "away": 4.75, "src": "E"},
    ("Mexico",        "Korea Republic"):     {"home": 1.65, "draw": 3.40, "away": 5.50, "src": "E"},
    ("South Africa",  "Czech Republic"):     {"home": 2.80, "draw": 3.10, "away": 2.60, "src": "E"},
    ("Mexico",        "Czech Republic"):     {"home": 1.42, "draw": 4.20, "away": 9.00, "src": "E"},
    ("South Africa",  "Korea Republic"):     {"home": 2.80, "draw": 3.20, "away": 2.50, "src": "E"},

    # ── Group B ──────────────────────────────────────────────────────────────
    # Canada has host advantage; Canada vs Bosnia confirmed FanDuel -130/+260/+370
    ("Canada",        "Qatar"):              {"home": 1.57, "draw": 3.60, "away": 6.00, "src": "E"},
    ("Switzerland",   "Bosnia and Herzegovina"): {"home": 1.62, "draw": 3.50, "away": 5.50, "src": "E"},
    ("Canada",        "Switzerland"):        {"home": 2.40, "draw": 3.20, "away": 2.90, "src": "E"},
    ("Qatar",         "Bosnia and Herzegovina"): {"home": 2.70, "draw": 3.10, "away": 2.80, "src": "E"},
    ("Canada",        "Bosnia and Herzegovina"): {"home": 1.77, "draw": 3.60, "away": 4.70, "src": "C"},
    ("Qatar",         "Switzerland"):        {"home": 5.50, "draw": 3.80, "away": 1.60, "src": "E"},

    # ── Group C ──────────────────────────────────────────────────────────────
    # Brazil vs Scotland: Betfair 2/5 (1.40) / 7/2 (4.50) / 6/1 (7.00)
    ("Brazil",        "Scotland"):           {"home": 1.40, "draw": 4.50, "away": 7.00, "src": "C"},
    ("Morocco",       "Haiti"):              {"home": 1.25, "draw": 5.50, "away": 14.00, "src": "E"},
    ("Brazil",        "Morocco"):            {"home": 1.75, "draw": 3.60, "away": 4.80, "src": "E"},
    ("Scotland",      "Haiti"):              {"home": 1.62, "draw": 3.50, "away": 5.50, "src": "E"},
    ("Brazil",        "Haiti"):              {"home": 1.22, "draw": 5.50, "away": 14.00, "src": "E"},
    ("Scotland",      "Morocco"):            {"home": 4.50, "draw": 3.60, "away": 1.75, "src": "E"},

    # ── Group D ──────────────────────────────────────────────────────────────
    # USA vs Paraguay: FanDuel -105/+230/+310 (USA host)
    # Türkiye vs Australia: Australia rank 23 vs Türkiye rank 36; close match
    ("United States", "Paraguay"):           {"home": 1.95, "draw": 3.30, "away": 4.10, "src": "C"},
    ("Türkiye",       "Australia"):          {"home": 2.10, "draw": 3.30, "away": 3.50, "src": "E"},
    ("United States", "Türkiye"):            {"home": 2.00, "draw": 3.25, "away": 3.60, "src": "E"},
    ("Paraguay",      "Australia"):          {"home": 2.90, "draw": 3.10, "away": 2.45, "src": "E"},
    ("United States", "Australia"):          {"home": 1.80, "draw": 3.40, "away": 4.50, "src": "E"},
    ("Paraguay",      "Türkiye"):            {"home": 3.00, "draw": 3.10, "away": 2.30, "src": "E"},

    # ── Group E ──────────────────────────────────────────────────────────────
    # CIV vs Ecuador: Oddschecker 13/5 (3.60) / 192/100 (2.92) / 29/20 (2.45)
    ("Germany",       "Curacao"):            {"home": 1.10, "draw": 7.00, "away": 22.00, "src": "E"},
    ("Côte d'Ivoire", "Ecuador"):            {"home": 3.60, "draw": 2.92, "away": 2.45, "src": "C"},
    ("Germany",       "Côte d'Ivoire"):      {"home": 1.40, "draw": 4.50, "away": 8.00, "src": "E"},
    ("Curacao",       "Ecuador"):            {"home": 7.00, "draw": 4.20, "away": 1.35, "src": "E"},
    ("Germany",       "Ecuador"):            {"home": 1.45, "draw": 4.20, "away": 8.00, "src": "E"},
    ("Curacao",       "Côte d'Ivoire"):      {"home": 9.00, "draw": 5.00, "away": 1.28, "src": "E"},

    # ── Group F ──────────────────────────────────────────────────────────────
    # Sweden vs Tunisia: Oddschecker 19/20 (1.95) / 12/5 (3.40) / 17/5 (4.40)
    # Netherlands vs Japan: DraftKings Netherlands -125 → ~1.80
    ("Sweden",        "Tunisia"):            {"home": 1.95, "draw": 3.40, "away": 4.40, "src": "C"},
    ("Netherlands",   "Japan"):              {"home": 1.80, "draw": 3.50, "away": 4.50, "src": "C"},
    ("Sweden",        "Netherlands"):        {"home": 3.60, "draw": 3.40, "away": 1.90, "src": "E"},
    ("Tunisia",       "Japan"):              {"home": 3.40, "draw": 3.20, "away": 2.20, "src": "E"},
    ("Sweden",        "Japan"):              {"home": 2.50, "draw": 3.30, "away": 2.80, "src": "E"},
    ("Tunisia",       "Netherlands"):        {"home": 6.00, "draw": 4.00, "away": 1.50, "src": "E"},

    # ── Group G ──────────────────────────────────────────────────────────────
    # Belgium vs Egypt: BetMGM Belgium -240; Egypt +400 (group stage)
    ("Belgium",       "New Zealand"):        {"home": 1.15, "draw": 6.50, "away": 20.00, "src": "E"},
    ("Egypt",         "Iran"):               {"home": 2.60, "draw": 3.10, "away": 2.80, "src": "E"},
    ("Belgium",       "Egypt"):              {"home": 1.42, "draw": 4.50, "away": 8.00, "src": "E"},
    ("New Zealand",   "Iran"):               {"home": 4.00, "draw": 3.50, "away": 1.90, "src": "E"},
    ("Belgium",       "Iran"):               {"home": 1.35, "draw": 5.00, "away": 9.00, "src": "E"},
    ("New Zealand",   "Egypt"):              {"home": 3.80, "draw": 3.30, "away": 2.00, "src": "E"},

    # ── Group H ──────────────────────────────────────────────────────────────
    # Spain vs Saudi Arabia: bookmakers Spain -310 → ~1.32
    # Cape Verde vs Uruguay: Uruguay rank 17 vs Cape Verde rank 74
    ("Spain",         "Saudi Arabia"):       {"home": 1.32, "draw": 5.50, "away": 11.00, "src": "C"},
    ("Cape Verde Islands", "Uruguay"):       {"home": 5.50, "draw": 3.80, "away": 1.57, "src": "E"},
    ("Spain",         "Cape Verde Islands"): {"home": 1.18, "draw": 7.00, "away": 20.00, "src": "E"},
    ("Saudi Arabia",  "Uruguay"):            {"home": 3.50, "draw": 3.20, "away": 2.10, "src": "E"},
    ("Spain",         "Uruguay"):            {"home": 1.62, "draw": 3.60, "away": 5.50, "src": "E"},
    ("Saudi Arabia",  "Cape Verde Islands"): {"home": 2.30, "draw": 3.10, "away": 3.30, "src": "E"},

    # ── Group I ──────────────────────────────────────────────────────────────
    # France vs Norway: FanDuel France -165 → ~1.65; prediction market France 53%
    # Norway vs Senegal: Senegal rank 20 vs Norway rank 29 → close/slight Senegal fav
    ("France",        "Iraq"):               {"home": 1.12, "draw": 7.00, "away": 22.00, "src": "E"},
    ("Norway",        "Senegal"):            {"home": 2.40, "draw": 3.20, "away": 2.90, "src": "E"},
    ("France",        "Norway"):             {"home": 1.65, "draw": 3.60, "away": 5.00, "src": "C"},
    ("Iraq",          "Senegal"):            {"home": 4.50, "draw": 3.50, "away": 1.72, "src": "E"},
    ("France",        "Senegal"):            {"home": 1.62, "draw": 3.60, "away": 5.50, "src": "E"},
    ("Iraq",          "Norway"):             {"home": 6.50, "draw": 4.20, "away": 1.45, "src": "E"},

    # ── Group J ──────────────────────────────────────────────────────────────
    # Argentina vs Jordan: Argentina -550/+500/+1000 (confirmed)
    # Algeria vs Austria: very even — Algeria +200/+115 draw/+200 (Oddschecker)
    ("Argentina",     "Jordan"):             {"home": 1.18, "draw": 6.00, "away": 11.00, "src": "C"},
    ("Algeria",       "Austria"):            {"home": 3.00, "draw": 2.15, "away": 3.00, "src": "C"},
    ("Argentina",     "Algeria"):            {"home": 1.40, "draw": 4.50, "away": 8.00, "src": "E"},
    ("Jordan",        "Austria"):            {"home": 5.50, "draw": 3.80, "away": 1.55, "src": "E"},
    ("Argentina",     "Austria"):            {"home": 1.55, "draw": 3.80, "away": 6.00, "src": "E"},
    ("Jordan",        "Algeria"):            {"home": 4.00, "draw": 3.30, "away": 1.95, "src": "E"},

    # ── Group K ──────────────────────────────────────────────────────────────
    # Portugal vs Colombia: Portugal rank 6 vs Colombia rank 26 → Portugal moderate fav
    # Colombia vs Uzbekistan: Colombia rank 26 vs Uzbekistan rank 84 → Colombia big fav
    ("Portugal",      "Congo DR"):           {"home": 1.20, "draw": 6.00, "away": 18.00, "src": "E"},
    ("Colombia",      "Uzbekistan"):         {"home": 1.50, "draw": 4.00, "away": 7.00, "src": "E"},
    ("Portugal",      "Colombia"):           {"home": 1.65, "draw": 3.60, "away": 5.50, "src": "E"},
    ("Congo DR",      "Uzbekistan"):         {"home": 2.10, "draw": 3.20, "away": 3.60, "src": "E"},
    ("Portugal",      "Uzbekistan"):         {"home": 1.28, "draw": 5.50, "away": 13.00, "src": "E"},
    ("Congo DR",      "Colombia"):           {"home": 3.80, "draw": 3.30, "away": 2.00, "src": "E"},

    # ── Group L ──────────────────────────────────────────────────────────────
    # England vs Ghana: confirmed 1/3 (1.33) / 9/2 (5.50) / 11/1 (12.00) Oddschecker
    # Croatia vs Panama: Croatia rank 10 vs Panama rank 80 → Croatia big fav
    ("England",       "Ghana"):              {"home": 1.33, "draw": 5.50, "away": 12.00, "src": "C"},
    ("Croatia",       "Panama"):             {"home": 1.50, "draw": 4.00, "away": 7.00, "src": "E"},
    ("England",       "Croatia"):            {"home": 1.62, "draw": 3.50, "away": 5.50, "src": "E"},
    ("Ghana",         "Panama"):             {"home": 2.20, "draw": 3.20, "away": 3.40, "src": "E"},
    ("England",       "Panama"):             {"home": 1.30, "draw": 5.50, "away": 13.00, "src": "E"},
    ("Ghana",         "Croatia"):            {"home": 4.20, "draw": 3.40, "away": 1.85, "src": "E"},
}
# fmt: on
