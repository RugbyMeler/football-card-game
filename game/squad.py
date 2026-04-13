"""Squad system — FootballPlayer dataclass and Squad manager."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import copy
from game.card import Rarity


class Position(Enum):
    GK  = "GK"
    DEF = "DEF"
    MID = "MID"
    ATT = "ATT"


@dataclass
class FootballPlayer:
    id:          str
    name:        str
    position:    Position
    att_power:   int      # passive attack contribution (ATT, MID) / ATK card scaling
    def_power:   int      # passive defense (GK only) / DEF+MID card scaling
    description: str
    rarity:      Rarity = Rarity.COMMON

    def copy(self) -> FootballPlayer:
        return copy.copy(self)

    def stat_line(self) -> str:
        return f"ATK {self.att_power}  DEF {self.def_power}"


# ── Squad container ────────────────────────────────────────────────────────────

class Squad:
    """
    Starting lineup of four positions plus a bench.

    Passive round contributions:
        base_attack  = attacker.att_power + midfielder.att_power
        base_defense = gk.def_power          (only GK is passive; DEF+MID scale cards)
    """

    def __init__(self, gk: FootballPlayer, defender: FootballPlayer,
                 midfielder: FootballPlayer, attacker: FootballPlayer,
                 bench: list[FootballPlayer] | None = None):
        self.gk         = gk
        self.defender   = defender
        self.midfielder = midfielder
        self.attacker   = attacker
        self.bench: list[FootballPlayer] = bench or []

    # ── Passive stats ─────────────────────────────────────────────────────────

    @property
    def base_attack(self) -> int:
        return self.attacker.att_power + self.midfielder.att_power

    @property
    def base_defense(self) -> int:
        return self.gk.def_power

    # ── Squad-scale factor (used by MatchEngine when playing scaled cards) ────

    def scale_factor(self, key: str) -> int:
        """Return the integer bonus for a given squad_scale key."""
        table = {
            "att":       self.attacker.att_power,
            "gk":        self.gk.def_power,
            "def":       self.defender.def_power,
            "mid_att":   self.midfielder.att_power,
            "mid_def":   self.midfielder.def_power,
            "mid_total": self.midfielder.att_power + self.midfielder.def_power,
            "def_gk":    self.defender.def_power + self.gk.def_power,
        }
        return table.get(key, 0)

    # ── Roster operations ─────────────────────────────────────────────────────

    def get_starter(self, pos: Position) -> FootballPlayer:
        return {
            Position.GK:  self.gk,
            Position.DEF: self.defender,
            Position.MID: self.midfielder,
            Position.ATT: self.attacker,
        }[pos]

    def starters(self) -> list[tuple[Position, FootballPlayer]]:
        return [
            (Position.GK,  self.gk),
            (Position.DEF, self.defender),
            (Position.MID, self.midfielder),
            (Position.ATT, self.attacker),
        ]

    def swap_with_bench(self, pos: Position, bench_idx: int) -> None:
        """Swap a starter with bench[bench_idx]."""
        bench_player = self.bench[bench_idx]
        current = self.get_starter(pos)
        if pos == Position.GK:
            self.gk = bench_player
        elif pos == Position.DEF:
            self.defender = bench_player
        elif pos == Position.MID:
            self.midfielder = bench_player
        elif pos == Position.ATT:
            self.attacker = bench_player
        self.bench[bench_idx] = current

    def add_to_bench(self, player: FootballPlayer) -> None:
        self.bench.append(player)

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "gk":    self.gk.id,
            "def":   self.defender.id,
            "mid":   self.midfielder.id,
            "att":   self.attacker.id,
            "bench": [p.id for p in self.bench],
        }

    @classmethod
    def from_dict(cls, data: dict, catalog: dict[str, FootballPlayer]) -> Squad:
        return cls(
            gk         = catalog[data["gk"]].copy(),
            defender   = catalog[data["def"]].copy(),
            midfielder = catalog[data["mid"]].copy(),
            attacker   = catalog[data["att"]].copy(),
            bench      = [catalog[bid].copy() for bid in data.get("bench", [])
                          if bid in catalog],
        )
