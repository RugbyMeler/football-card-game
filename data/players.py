"""Player catalog — all football players available in the game."""
from game.squad import FootballPlayer, Position, Squad
from game.card import Rarity

C = Rarity.COMMON
U = Rarity.UNCOMMON
R = Rarity.RARE
GK  = Position.GK
DEF = Position.DEF
MID = Position.MID
ATT = Position.ATT

ALL_PLAYERS: list[FootballPlayer] = [
    # ── GOALKEEPERS ──────────────────────────────────────────────────────────
    # def_power is both passive defense and GK-card scaling
    FootballPlayer("gk_novak",    "Pavel Novak",    GK,  0, 2, "Reliable and composed. A solid base.", C),
    FootballPlayer("gk_santos",   "Renaldo Santos", GK,  0, 3, "Strong hands, wins the crosses.", C),
    FootballPlayer("gk_brauer",   "Karl Brauer",    GK,  1, 4, "Reads the game early. Starts attacks.", U),
    FootballPlayer("gk_osei",     "Kwame Osei",     GK,  0, 5, "Incredible reflexes. Nothing gets past.", U),
    FootballPlayer("gk_varga",    "Tibor Varga",    GK,  1, 6, "Command the box. The last line.", R),

    # ── DEFENDERS ────────────────────────────────────────────────────────────
    # def_power scales DEF-type cards (man_marking, high_line, set_piece etc.)
    FootballPlayer("def_mills",   "Terry Mills",    DEF, 1, 2, "Gets stuck in. Never hides.", C),
    FootballPlayer("def_petrov",  "Ivan Petrov",    DEF, 1, 3, "Positionally sound. Rarely beaten.", C),
    FootballPlayer("def_acosta",  "Marco Acosta",   DEF, 2, 4, "Ball-playing defender. Links the play.", U),
    FootballPlayer("def_ngozi",   "Emeka Ngozi",    DEF, 1, 5, "Aerial monster. Dominant at set pieces.", U),
    FootballPlayer("def_blake",   "Aaron Blake",    DEF, 2, 6, "The General. Organises everything.", R),

    # ── MIDFIELDERS ──────────────────────────────────────────────────────────
    # att_power → passive attack each round
    # def_power → MID-card scaling (gegenpress, drop_deep, etc.)
    FootballPlayer("mid_chen",    "Wei Chen",       MID, 1, 1, "Works hard. Covers ground.", C),
    FootballPlayer("mid_reyes",   "Luis Reyes",     MID, 2, 1, "Creative spark in the middle.", C),
    FootballPlayer("mid_okafor",  "Chidi Okafor",   MID, 2, 2, "Equally comfortable in both halves.", U),
    FootballPlayer("mid_strand",  "Erik Strand",    MID, 3, 2, "Box-to-box engine. Never stops.", U),
    FootballPlayer("mid_silva",   "Bruno Silva",    MID, 3, 3, "Sees passes nobody else does.", R),
    FootballPlayer("mid_dragan",  "Dragan Kovac",   MID, 4, 2, "A midfield general. Dictates tempo.", R),

    # ── ATTACKERS ────────────────────────────────────────────────────────────
    # att_power → passive attack each round AND ATK-card scaling
    FootballPlayer("att_wade",    "Leon Wade",      ATT, 2, 0, "Willing runner. Never stops pressing.", C),
    FootballPlayer("att_marco",   "Marco Riva",     ATT, 3, 0, "Technical and clever. Good movement.", C),
    FootballPlayer("att_obi",     "Chukwu Obi",     ATT, 3, 1, "Physical presence. Hard to dispossess.", U),
    FootballPlayer("att_laval",   "Pierre Laval",   ATT, 4, 1, "Lethal in the box. Clinical finisher.", U),
    FootballPlayer("att_storm",   "Jack Storm",     ATT, 5, 1, "Pace and power. Defenders' nightmare.", R),
    FootballPlayer("att_diallo",  "Moussa Diallo",  ATT, 5, 2, "World-class movement. Creates from nothing.", R),
]

PLAYER_BY_ID: dict[str, FootballPlayer] = {p.id: p for p in ALL_PLAYERS}


# ── Starter squad ─────────────────────────────────────────────────────────────

STARTER_SQUAD_IDS = {
    "gk":    "gk_novak",
    "def":   "def_mills",
    "mid":   "mid_chen",
    "att":   "att_wade",
    "bench": [],
}


def build_starter_squad() -> Squad:
    return Squad.from_dict(STARTER_SQUAD_IDS, PLAYER_BY_ID)


# ── Opponent squad by difficulty ──────────────────────────────────────────────

_OPP_SQUADS = {
    1: {"gk": "gk_novak",  "def": "def_mills",  "mid": "mid_chen",   "att": "att_wade"},
    2: {"gk": "gk_santos", "def": "def_petrov", "mid": "mid_reyes",  "att": "att_marco"},
    3: {"gk": "gk_brauer", "def": "def_acosta", "mid": "mid_okafor", "att": "att_obi"},
    4: {"gk": "gk_osei",   "def": "def_ngozi",  "mid": "mid_strand", "att": "att_laval"},
    5: {"gk": "gk_varga",  "def": "def_blake",  "mid": "mid_silva",  "att": "att_storm"},
}


def build_opponent_squad(difficulty: int) -> Squad:
    ids = _OPP_SQUADS.get(max(1, min(5, difficulty)), _OPP_SQUADS[1])
    return Squad.from_dict({**ids, "bench": []}, PLAYER_BY_ID)
