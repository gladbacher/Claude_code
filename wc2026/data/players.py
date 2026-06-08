"""
Top international goal scorers per team — goals per game in international matches.
Sources marked: [SS] = extracted from ScoutingStats.ai screenshots, [est] = estimated.
"""

PLAYERS: dict[str, list[dict]] = {

    # ── Group A ───────────────────────────────────────────────────────────────
    "Mexico": [  # [est]
        {"name": "Raúl Jiménez",    "gpg": 0.42},
        {"name": "Henry Martín",    "gpg": 0.35},
        {"name": "Hirving Lozano",  "gpg": 0.28},
        {"name": "Alexis Vega",     "gpg": 0.22},
    ],
    "South Africa": [  # [est]
        {"name": "Percy Tau",         "gpg": 0.30},
        {"name": "Evidence Makgopa",  "gpg": 0.28},
        {"name": "Lyle Foster",       "gpg": 0.25},
        {"name": "Bongani Zungu",     "gpg": 0.12},
    ],
    "Korea Republic": [  # [SS]
        {"name": "Son Heung-min",    "gpg": 0.50},
        {"name": "Hyeon-gyu Oh",     "gpg": 0.40},
        {"name": "Dong-gyeong Lee",  "gpg": 0.33},
        {"name": "Jae-sung Lee",     "gpg": 0.29},
        {"name": "Hee-chan Hwang",   "gpg": 0.18},
    ],
    "Czech Republic": [  # [est]
        {"name": "Patrik Schick",  "gpg": 0.52},
        {"name": "Adam Hložek",    "gpg": 0.28},
        {"name": "Tomáš Souček",   "gpg": 0.20},
        {"name": "Jakub Jankto",   "gpg": 0.15},
    ],

    # ── Group B ───────────────────────────────────────────────────────────────
    "Canada": [  # [est]
        {"name": "Jonathan David",  "gpg": 0.52},
        {"name": "Cyle Larin",      "gpg": 0.42},
        {"name": "Alphonso Davies", "gpg": 0.22},
        {"name": "Tajon Buchanan",  "gpg": 0.20},
    ],
    "Qatar": [  # [est]
        {"name": "Akram Afif",         "gpg": 0.38},
        {"name": "Almoez Ali",         "gpg": 0.35},
        {"name": "Hassan Al-Haydos",   "gpg": 0.20},
        {"name": "Abdulaziz Hatem",    "gpg": 0.15},
    ],
    "Switzerland": [  # [est]
        {"name": "Breel Embolo",   "gpg": 0.42},
        {"name": "Zeki Amdouni",   "gpg": 0.32},
        {"name": "Ruben Vargas",   "gpg": 0.25},
        {"name": "Granit Xhaka",   "gpg": 0.18},
    ],
    "Bosnia and Herzegovina": [  # [est]
        {"name": "Edin Džeko",           "gpg": 0.45},
        {"name": "Ermedin Demirović",    "gpg": 0.42},
        {"name": "Benjamin Šeško",       "gpg": 0.38},
        {"name": "Armin Hodžić",         "gpg": 0.22},
    ],

    # ── Group C ───────────────────────────────────────────────────────────────
    "Brazil": [  # [est]
        {"name": "Vinicius Jr",       "gpg": 0.45},
        {"name": "Rodrygo",           "gpg": 0.38},
        {"name": "Gabriel Martinelli","gpg": 0.32},
        {"name": "Endrick",           "gpg": 0.30},
    ],
    "Morocco": [  # [est]
        {"name": "Youssef En-Nesyri", "gpg": 0.42},
        {"name": "Hakim Ziyech",      "gpg": 0.32},
        {"name": "Sofiane Boufal",    "gpg": 0.25},
        {"name": "Azzedine Ounahi",   "gpg": 0.18},
    ],
    "Haiti": [  # [est]
        {"name": "Frantzdy Pierrot",       "gpg": 0.38},
        {"name": "Kervens Belfort",        "gpg": 0.35},
        {"name": "Wilde Donald Guerrier",  "gpg": 0.28},
        {"name": "Duckens Nazon",          "gpg": 0.22},
    ],
    "Scotland": [  # [est]
        {"name": "Lyndon Dykes",   "gpg": 0.35},
        {"name": "Ryan Christie",  "gpg": 0.22},
        {"name": "John McGinn",    "gpg": 0.20},
        {"name": "Kenny McLean",   "gpg": 0.15},
    ],

    # ── Group D ───────────────────────────────────────────────────────────────
    "United States": [  # [est]
        {"name": "Ricardo Pepi",      "gpg": 0.42},
        {"name": "Christian Pulisic", "gpg": 0.38},
        {"name": "Folarin Balogun",   "gpg": 0.32},
        {"name": "Josh Sargent",      "gpg": 0.28},
    ],
    "Türkiye": [  # [est]
        {"name": "Arda Güler",           "gpg": 0.35},
        {"name": "Kerem Aktürkoğlu",     "gpg": 0.32},
        {"name": "Baris Alper Yilmaz",   "gpg": 0.28},
        {"name": "Cenk Tosun",           "gpg": 0.22},
    ],
    "Paraguay": [  # [est]
        {"name": "Antonio Sanabria", "gpg": 0.32},
        {"name": "Miguel Almirón",   "gpg": 0.28},
        {"name": "Julio Enciso",     "gpg": 0.25},
        {"name": "Braian Romero",    "gpg": 0.20},
    ],
    "Australia": [  # [est]
        {"name": "Adam Taggart",  "gpg": 0.30},
        {"name": "Mathew Leckie", "gpg": 0.28},
        {"name": "Martin Boyle",  "gpg": 0.22},
        {"name": "Craig Goodwin", "gpg": 0.18},
    ],

    # ── Group E ───────────────────────────────────────────────────────────────
    "Germany": [  # [SS]
        {"name": "Jamal Musiala",    "gpg": 0.57},
        {"name": "Kai Havertz",      "gpg": 0.50},
        {"name": "Florian Wirtz",    "gpg": 0.47},
        {"name": "Nick Woltemade",   "gpg": 0.36},
        {"name": "Leroy Sané",       "gpg": 0.30},
    ],
    "Curacao": [  # [SS]
        {"name": "Gervane Kastaneer", "gpg": 0.62},
        {"name": "Kenji Gorré",       "gpg": 0.33},
        {"name": "Juninho Bacuna",    "gpg": 0.25},
        {"name": "Sontje Hansen",     "gpg": 0.20},
    ],
    "Côte d'Ivoire": [  # [SS]
        {"name": "Amad Diallo",    "gpg": 0.40},
        {"name": "Evann Guessand", "gpg": 0.20},
        {"name": "Guela Doué",     "gpg": 0.20},
        {"name": "Yan Diomande",   "gpg": 0.12},
    ],
    "Ecuador": [  # [SS]
        {"name": "Enner Valencia",  "gpg": 0.37},
        {"name": "Gonzalo Plata",   "gpg": 0.15},
        {"name": "Nilson Angulo",   "gpg": 0.12},
        {"name": "Félix Torres",    "gpg": 0.12},
    ],

    # ── Group F ───────────────────────────────────────────────────────────────
    "Sweden": [  # [SS]
        {"name": "Viktor Gyökeres",   "gpg": 1.08},
        {"name": "Alexander Isak",    "gpg": 0.50},
        {"name": "Ken Sema",          "gpg": 0.33},
        {"name": "Benjamin Nygren",   "gpg": 0.27},
        {"name": "Anthony Elanga",    "gpg": 0.23},
    ],
    "Netherlands": [  # [SS]
        {"name": "Memphis Depay",      "gpg": 0.82},
        {"name": "Cody Gakpo",         "gpg": 0.37},
        {"name": "Tijjani Reijnders",  "gpg": 0.38},
        {"name": "Denzel Dumfries",    "gpg": 0.38},
        {"name": "Donyell Malen",      "gpg": 0.25},
    ],
    "Japan": [  # [SS]
        {"name": "Koki Ogawa",       "gpg": 0.44},
        {"name": "Daichi Kamada",    "gpg": 0.36},
        {"name": "Takefusa Kubo",    "gpg": 0.17},
        {"name": "Keito Nakamura",   "gpg": 0.15},
        {"name": "Ko Itakura",       "gpg": 0.11},
    ],
    "Tunisia": [  # [SS]
        {"name": "Elias Achouri",     "gpg": 0.43},
        {"name": "Hazem Mastouri",    "gpg": 0.25},
        {"name": "Montassar Talbi",   "gpg": 0.22},
        {"name": "Ali Abdi",          "gpg": 0.20},
        {"name": "Eliyes Skhiri",     "gpg": 0.12},
    ],

    # ── Group G ───────────────────────────────────────────────────────────────
    "Belgium": [  # [SS]
        {"name": "Romelu Lukaku",     "gpg": 0.83},
        {"name": "Kevin De Bruyne",   "gpg": 0.62},
        {"name": "Youri Tielemans",   "gpg": 0.36},
        {"name": "Jérémy Doku",       "gpg": 0.31},
        {"name": "Dodi Lukébakio",    "gpg": 0.27},
    ],
    "Egypt": [  # [SS]
        {"name": "Mohamed Salah",       "gpg": 0.57},
        {"name": "Omar Marmoush",       "gpg": 0.40},
        {"name": "Mahmoud Trezeguet",   "gpg": 0.11},
        {"name": "Ramy Rabia",          "gpg": 0.11},
        {"name": "Yasser Ibrahim",      "gpg": 0.11},
    ],
    "Iran": [  # [SS]
        {"name": "Mohammad Mohebi", "gpg": 0.70},
        {"name": "Mehdi Taremi",    "gpg": 0.67},
        {"name": "Mehdi Ghayedi",   "gpg": 0.17},
        {"name": "Arya Yousefi",    "gpg": 0.17},
        {"name": "Saleh Hardani",   "gpg": 0.11},
    ],
    "New Zealand": [  # [SS]
        {"name": "Chris Wood",          "gpg": 0.78},
        {"name": "Elijah Just",         "gpg": 0.50},
        {"name": "Ben Waine",           "gpg": 0.30},
        {"name": "Kosta Barbarouses",   "gpg": 0.22},
        {"name": "Callum McCowatt",     "gpg": 0.20},
    ],

    # ── Group H ───────────────────────────────────────────────────────────────
    "Spain": [  # [SS]
        {"name": "Mikel Oyarzabal", "gpg": 0.80},
        {"name": "Mikel Merino",    "gpg": 0.57},
        {"name": "Ferran Torres",   "gpg": 0.40},
        {"name": "Lamine Yamal",    "gpg": 0.27},
        {"name": "Martín Zubimendi","gpg": 0.20},
    ],
    "Saudi Arabia": [  # [SS]
        {"name": "Salem Al-Dawsari",   "gpg": 0.09},
        {"name": "Firas Al-Buraikan",  "gpg": 0.06},
        {"name": "Musab Al-Juwayr",    "gpg": 0.06},
        {"name": "Saud Abdulhamid",    "gpg": 0.05},
    ],
    "Cape Verde Islands": [  # [SS]
        {"name": "Sidny Cabral",  "gpg": 0.33},
        {"name": "Ryan Mendes",   "gpg": 0.14},
        {"name": "Laros Duarte",  "gpg": 0.14},
        {"name": "Willy Semedo",  "gpg": 0.10},
    ],
    "Uruguay": [  # [SS]
        {"name": "Nicolás de la Cruz",       "gpg": 0.33},
        {"name": "Darwin Núñez",             "gpg": 0.33},
        {"name": "Rodrigo Aguirre",          "gpg": 0.30},
        {"name": "Giorgian de Arrascaeta",   "gpg": 0.27},
        {"name": "Federico Valverde",        "gpg": 0.18},
    ],

    # ── Group I ───────────────────────────────────────────────────────────────
    "France": [  # [SS]
        {"name": "Kylian Mbappé",    "gpg": 0.62},
        {"name": "Rayan Cherki",     "gpg": 0.33},
        {"name": "Adrien Rabiot",    "gpg": 0.30},
        {"name": "Michael Olise",    "gpg": 0.25},
        {"name": "Ousmane Dembélé",  "gpg": 0.22},
    ],
    "Norway": [  # [est] — Haaland dominates
        {"name": "Erling Haaland",   "gpg": 0.76},
        {"name": "Alexander Sørloth","gpg": 0.42},
        {"name": "Martin Ødegaard",  "gpg": 0.25},
        {"name": "Ola Aina",         "gpg": 0.12},
    ],
    "Iraq": [  # [est]
        {"name": "Mohanad Ali",    "gpg": 0.32},
        {"name": "Aymen Hussein",  "gpg": 0.28},
        {"name": "Amjad Attwan",   "gpg": 0.22},
        {"name": "Alaa Abbas",     "gpg": 0.15},
    ],
    "Senegal": [  # [est]
        {"name": "Nicolas Jackson",  "gpg": 0.38},
        {"name": "Sadio Mané",       "gpg": 0.35},
        {"name": "Ismaila Sarr",     "gpg": 0.28},
        {"name": "Iliman Ndiaye",    "gpg": 0.25},
    ],

    # ── Group J ───────────────────────────────────────────────────────────────
    "Argentina": [  # [SS]
        {"name": "Lionel Messi",       "gpg": 0.67},
        {"name": "Lautaro Martínez",   "gpg": 0.33},
        {"name": "Thiago Almada",      "gpg": 0.30},
        {"name": "Julián Álvarez",     "gpg": 0.25},
        {"name": "Nicolás Otamendi",   "gpg": 0.22},
    ],
    "Algeria": [  # [est]
        {"name": "Islam Slimani",  "gpg": 0.42},
        {"name": "Riyad Mahrez",   "gpg": 0.38},
        {"name": "Youcef Atal",    "gpg": 0.25},
        {"name": "Sofiane Feghouli","gpg": 0.18},
    ],
    "Austria": [  # [est]
        {"name": "Marko Arnautović",    "gpg": 0.45},
        {"name": "Michael Gregoritsch", "gpg": 0.30},
        {"name": "Marcel Sabitzer",     "gpg": 0.28},
        {"name": "Christoph Baumgartner","gpg": 0.22},
    ],
    "Jordan": [  # [est]
        {"name": "Yazan Al-Naimat",  "gpg": 0.32},
        {"name": "Musa Al-Taamari",  "gpg": 0.25},
        {"name": "Baha Faisal",      "gpg": 0.22},
        {"name": "Ahmad Abubaker",   "gpg": 0.15},
    ],

    # ── Group K ───────────────────────────────────────────────────────────────
    "Portugal": [  # [est]
        {"name": "Cristiano Ronaldo", "gpg": 0.65},
        {"name": "Gonçalo Ramos",     "gpg": 0.45},
        {"name": "Rafael Leão",       "gpg": 0.32},
        {"name": "Bernardo Silva",    "gpg": 0.25},
    ],
    "Colombia": [  # [SS]
        {"name": "Luis Suárez",      "gpg": 0.83},
        {"name": "Luis Díaz",        "gpg": 0.39},
        {"name": "James Rodríguez",  "gpg": 0.17},
        {"name": "Jhon Córdoba",     "gpg": 0.15},
        {"name": "Davinson Sánchez", "gpg": 0.12},
    ],
    "Congo DR": [  # [est]
        {"name": "Cédric Bakambu",  "gpg": 0.45},
        {"name": "Yannick Bolasie", "gpg": 0.28},
        {"name": "Silas",           "gpg": 0.25},
        {"name": "Fiston Mayele",   "gpg": 0.20},
    ],
    "Uzbekistan": [  # [est]
        {"name": "Eldor Shomurodov",      "gpg": 0.50},
        {"name": "Abbosbek Fayzullayev",  "gpg": 0.28},
        {"name": "Jamshid Iskanderov",    "gpg": 0.20},
        {"name": "Sherzod Nasrullayev",   "gpg": 0.15},
    ],

    # ── Group L ───────────────────────────────────────────────────────────────
    "England": [  # [est]
        {"name": "Harry Kane",       "gpg": 0.65},
        {"name": "Phil Foden",       "gpg": 0.32},
        {"name": "Jude Bellingham",  "gpg": 0.30},
        {"name": "Marcus Rashford",  "gpg": 0.28},
        {"name": "Bukayo Saka",      "gpg": 0.25},
    ],
    "Croatia": [  # [est]
        {"name": "Andrej Kramarić",  "gpg": 0.45},
        {"name": "Ivan Perišić",     "gpg": 0.28},
        {"name": "Marko Livaja",     "gpg": 0.25},
        {"name": "Luka Modrić",      "gpg": 0.18},
    ],
    "Ghana": [  # [est]
        {"name": "Mohammed Kudus",   "gpg": 0.38},
        {"name": "Jordan Ayew",      "gpg": 0.32},
        {"name": "Antoine Semenyo",  "gpg": 0.28},
        {"name": "Inaki Williams",   "gpg": 0.22},
    ],
    "Panama": [  # [SS]
        {"name": "José Luis Rodríguez", "gpg": 0.27},
        {"name": "José Fajardo",        "gpg": 0.27},
        {"name": "Ismael Díaz",         "gpg": 0.25},
        {"name": "Cecilio Waterman",    "gpg": 0.25},
        {"name": "Carlos Harvey",       "gpg": 0.22},
    ],
}
