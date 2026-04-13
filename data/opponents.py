"""Opponent roster for the campaign."""
from dataclasses import dataclass, field
from enum import Enum


class Strategy(Enum):
    AGGRESSIVE = "aggressive"
    DEFENSIVE  = "defensive"
    BALANCED   = "balanced"


@dataclass
class OpponentDef:
    id:          str
    name:        str
    team:        str
    difficulty:  int
    strategy:    Strategy
    deck_ids:    list[str]
    reward_pool: list[str]        # card IDs offered on win
    player_reward_pool: list[str] = field(default_factory=list)  # player IDs offered on win
    description: str = ""


OPPONENT_ROSTER: list[OpponentDef] = [
    # ── TIER 1 ────────────────────────────────────────────────────────────────
    OpponentDef(
        id="minnow_fc", name="Coach Potts", team="Minnow FC",
        difficulty=1, strategy=Strategy.DEFENSIVE,
        deck_ids=[
            "long_shot", "long_shot", "tap_in", "tap_in",
            "standard_block", "standard_block", "standard_block",
            "sliding_tackle", "sliding_tackle",
            "man_marking", "team_press",
        ],
        reward_pool=["chip_shot", "sliding_tackle", "drop_deep"],
        player_reward_pool=["def_petrov", "gk_santos", "att_marco"],
        description="A cautious side. Lots of blocks, few ambition.",
    ),
    OpponentDef(
        id="riverside", name="Manager Walsh", team="Riverside Rovers",
        difficulty=2, strategy=Strategy.BALANCED,
        deck_ids=[
            "long_shot", "long_shot",
            "header", "header",
            "counter_attack",
            "standard_block", "standard_block",
            "sliding_tackle", "sliding_tackle",
            "wall_of_steel", "team_press", "formation_shift",
        ],
        reward_pool=["counter_attack", "wall_of_steel", "driven_cross"],
        player_reward_pool=["mid_reyes", "def_acosta", "att_obi"],
        description="A balanced outfit. Expect them to adapt.",
    ),
    OpponentDef(
        id="thornfield", name="Gaffer Morton", team="Thornfield Town",
        difficulty=2, strategy=Strategy.AGGRESSIVE,
        deck_ids=[
            "long_shot", "long_shot",
            "header", "header",
            "strikers_run", "strikers_run",
            "counter_attack", "counter_attack",
            "standard_block", "sliding_tackle",
            "team_press", "one_two",
        ],
        reward_pool=["bicycle_kick", "back_four", "halftime_talk"],
        player_reward_pool=["mid_okafor", "gk_brauer", "att_laval"],
        description="They come at you hard. You'll need solid defence.",
    ),

    # ── TIER 2 ────────────────────────────────────────────────────────────────
    OpponentDef(
        id="irongate", name="Director Kane", team="Irongate City",
        difficulty=3, strategy=Strategy.BALANCED,
        deck_ids=[
            "long_shot", "header",
            "strikers_run", "counter_attack",
            "bicycle_kick", "set_piece",
            "standard_block", "sliding_tackle",
            "wall_of_steel", "goalkeeper_dive",
            "formation_shift", "team_press", "high_line",
        ],
        reward_pool=["penalty_strike", "offside_trap", "gegenpress"],
        player_reward_pool=["mid_strand", "def_ngozi", "att_storm"],
        description="Well-organised. They exploit every mistake.",
    ),
    OpponentDef(
        id="wanderers", name="Sir Douglas", team="The Wanderers",
        difficulty=3, strategy=Strategy.DEFENSIVE,
        deck_ids=[
            "long_shot", "tap_in",
            "counter_attack", "bicycle_kick",
            "standard_block", "standard_block",
            "sliding_tackle", "wall_of_steel",
            "goalkeeper_dive", "keeper_saves",
            "offside_trap", "sweeper_clear", "park_the_bus",
        ],
        reward_pool=["thunderbolt", "injury_time", "scout_report"],
        player_reward_pool=["gk_osei", "mid_silva", "att_diallo"],
        description="Park the bus. One goal on the counter. Infuriating.",
    ),

    # ── TIER 3 ────────────────────────────────────────────────────────────────
    OpponentDef(
        id="harrow", name="Boss Harrow", team="Harrow Athletic",
        difficulty=4, strategy=Strategy.AGGRESSIVE,
        deck_ids=[
            "strikers_run", "strikers_run",
            "counter_attack", "counter_attack",
            "bicycle_kick", "bicycle_kick",
            "false_nine", "penalty_strike",
            "thunderbolt", "all_out_attack",
            "wall_of_steel", "goalkeeper_dive",
            "offside_trap", "captains_order",
        ],
        reward_pool=["thunderbolt", "captains_order", "late_winner"],
        player_reward_pool=["gk_varga", "def_blake", "mid_dragan"],
        description="The most feared attack in the league.",
    ),
    OpponentDef(
        id="champions", name="The Legend", team="FC Champions",
        difficulty=5, strategy=Strategy.BALANCED,
        deck_ids=[
            "long_shot", "header",
            "strikers_run", "counter_attack",
            "bicycle_kick", "penalty_strike",
            "thunderbolt", "false_nine",
            "all_out_attack",
            "standard_block", "sliding_tackle",
            "wall_of_steel", "sweeper_keeper",
            "offside_trap", "captains_order", "pressing_trap",
        ],
        reward_pool=[],
        description="The champions. They have everything. So must you.",
    ),
]
