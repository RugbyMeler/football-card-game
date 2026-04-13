"""Card catalog — all 40 cards available in the game."""
from game.card import Card, CardType, Rarity

A = CardType.ATTACK
D = CardType.DEFENSE
S = CardType.SPECIAL
C = Rarity.COMMON
U = Rarity.UNCOMMON
R = Rarity.RARE

ALL_CARDS: list[Card] = [
    # ══════════════════════════════════════════════════════════════════════════
    # ATTACK CARDS
    # ══════════════════════════════════════════════════════════════════════════

    # ── Basic / no scaling ────────────────────────────────────────────────────
    Card("tap_in",         "Tap-In",            A, 0, 2,  "Simple finish from close range.", C),
    Card("long_shot",      "Long Shot",          A, 1, 3,  "Strike from outside the box.", C),
    Card("header",         "Header",             A, 1, 4,  "Meet a cross with your head.", C),
    Card("counter_attack", "Counter Attack",     A, 2, 6,  "Exploit space on the break.", C),
    Card("bicycle_kick",   "Bicycle Kick",       A, 3, 9,  "Spectacular overhead attempt.", U),
    Card("thunderbolt",    "Thunderbolt",        A, 3, 10, "Screamer. Opponent discards 1.", R),
    Card("penalty_strike", "Penalty Strike",     A, 2, 7,
         "Spot kick. Hard to stop. Exhaust.", U, exhaust=True),
    Card("volley",         "First-Time Volley",  A, 2, 5,  "No time to think — pure instinct.", U),
    Card("breakaway",      "Breakaway",          A, 2, 7,
         "Clear run on goal. Exhaust.", U, exhaust=True),
    Card("chip_shot",      "Chip Shot",          A, 1, 3,  "Delicate lob over the keeper. Draw 1.", C),
    Card("overhead_kick",  "Overhead Kick",      A, 3, 8,  "Acrobatic. No goalkeeper expected this.", U),
    Card("poachers_finish","Poacher's Finish",   A, 0, 3,  "Right place, right time. Gain 1 energy.", C),

    # ── Squad-scaling attack ──────────────────────────────────────────────────
    Card("strikers_run",   "Striker's Run",      A, 1, 3,
         "Attacker breaks free. +ATT power.",
         C, squad_scale="att", squad_scale_mult=1.0),
    Card("driven_cross",   "Driven Cross",       A, 1, 2,
         "MID whips one in. +MID att power. Draw 1.",
         C, squad_scale="mid_att", squad_scale_mult=1.0),
    Card("one_two",        "One-Two Pass",       A, 1, 3,
         "Quick exchange with the MID. Bonus from MID.",
         C, squad_scale="mid_att", squad_scale_mult=0.5),
    Card("set_piece",      "Set Piece",          A, 2, 4,
         "DEF joins the attack from a corner. +½ DEF power.",
         U, squad_scale="def", squad_scale_mult=0.5),
    Card("box_to_box_run", "Box-to-Box Run",     A, 2, 4,
         "MID joins the attack. +½ MID total.",
         U, squad_scale="mid_total", squad_scale_mult=0.5),
    Card("false_nine",     "False 9",            A, 2, 4,
         "Striker drops deep, MID overlaps. Discard opp. low card.",
         U, squad_scale="mid_total", squad_scale_mult=0.75),
    Card("all_out_attack", "All Out Attack",     A, 3, 0,
         "Total attack. +2×ATT this round. Exposed next.",
         R, squad_scale="att", squad_scale_mult=2.0),
    Card("late_winner",    "Late Winner",        A, 2, 6,
         "Rounds 7+: power becomes 10. Exhaust.",
         R, exhaust=True),

    # ══════════════════════════════════════════════════════════════════════════
    # DEFENSE CARDS
    # ══════════════════════════════════════════════════════════════════════════

    # ── Basic / no scaling ────────────────────────────────────────────────────
    Card("standard_block", "Standard Block",     D, 1, 3,  "Get your body in the way.", C),
    Card("sliding_tackle", "Sliding Tackle",     D, 1, 4,  "Win the ball on the floor.", C),
    Card("wall_of_steel",  "Wall of Steel",      D, 2, 6,  "Compact defensive shape.", C),
    Card("goalkeeper_dive","Goalkeeper Dive",    D, 2, 7,  "Diving save. Draw 1 card.", U),
    Card("sweeper_clear",  "Sweeper Clear",      D, 1, 3,  "Hoof it clear. Discard opp. card.", U),
    Card("offside_trap",   "Offside Trap",       D, 2, 0,  "Nullify opponent's highest attack.", R),
    Card("last_ditch",     "Last Ditch Tackle",  D, 1, 5,
         "Emergency block. Single use. Exhaust.", U, exhaust=True),
    Card("back_four",      "Back Four",          D, 2, 6,  "Organised unit. Hard to break down.", U),

    # ── Squad-scaling defense ─────────────────────────────────────────────────
    Card("man_marking",    "Man Marking",        D, 1, 2,
         "DEF shadows the striker. +¾ DEF power.",
         C, squad_scale="def", squad_scale_mult=0.75),
    Card("high_line",      "High Line",          D, 2, 4,
         "Risky press. +½ DEF power. Penalise opp. energy if they score.",
         U, squad_scale="def", squad_scale_mult=0.5),
    Card("drop_deep",      "Drop Deep",          D, 1, 2,
         "MID tracks back. +½ MID total.",
         C, squad_scale="mid_total", squad_scale_mult=0.5),
    Card("keeper_saves",   "Keeper's Saves",     D, 2, 0,
         "GK makes key saves. Power = GK's stat. Draw 1.",
         U, squad_scale="gk", squad_scale_mult=1.0),
    Card("sweeper_keeper", "Sweeper Keeper",     D, 3, 0,
         "GK storms out. Power = 2× GK's stat.",
         R, squad_scale="gk", squad_scale_mult=2.0),
    Card("park_the_bus",   "Park the Bus",       D, 2, 0,
         "All-in defence. +DEF+GK power. Opp draws one fewer card.",
         R, squad_scale="def_gk", squad_scale_mult=1.0),

    # ══════════════════════════════════════════════════════════════════════════
    # SPECIAL CARDS
    # ══════════════════════════════════════════════════════════════════════════
    Card("team_press",     "Team Press",         S, 0, 0,  "Gain 1 extra energy this round.", C),
    Card("halftime_talk",  "Halftime Talk",      S, 0, 0,  "Draw 3 cards.", U),
    Card("formation_shift","Formation Shift",    S, 1, 0,  "Next Defense card costs 0 this round.", U),
    Card("captains_order", "Captain's Order",    S, 2, 0,  "All cards in hand get +2 power.", R),
    Card("scout_report",   "Scout Report",       S, 1, 0,  "Peek at opponent's hand. Draw 1.", U),
    Card("injury_time",    "Injury Time",        S, 0, 0,  "Add 1 bonus round to the match.", R),
    Card("tactical_sub",   "Tactical Sub",       S, 1, 0,  "Draw 2 cards. Your next ATK card gets +2.", C),
    Card("tactical_foul",  "Tactical Foul",      S, 1, 0,  "Discard opponent's highest-cost card.", C),
    Card("gegenpress",     "Gegenpress",         S, 2, 0,
         "MID covers both ends. +MID att to your ATK and DEF totals.",
         U, squad_scale="mid_att", squad_scale_mult=1.0),
    Card("pressing_trigger","Pressing Trigger",  S, 2, 0,  "Opponent discards 2 cards.", U),
    Card("managers_gamble","Manager's Gamble",   S, 1, 0,  "Reveal top 3. Add ATK cards to hand; discard rest.", R),
    Card("pressing_trap",  "Pressing Trap",      S, 2, 0,
         "If opp. plays no defense this round, deal +MID total ATK.",
         R, squad_scale="mid_total", squad_scale_mult=1.0),
    Card("injury_time_drama","Injury Time Drama",S, 0, 0,
         "Add 1 round AND gain 2 energy next round. Exhaust.", R, exhaust=True),
    Card("cup_final_spirit","Cup Final Spirit",  S, 0, 0,  "All played cards +1. Draw 1.", U),
]

CARD_BY_ID: dict[str, Card] = {c.id: c for c in ALL_CARDS}


def get(card_id: str) -> Card:
    return CARD_BY_ID[card_id].copy()
