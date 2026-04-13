from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CardType(Enum):
    ATTACK = "Attack"
    DEFENSE = "Defense"
    SPECIAL = "Special"


class Rarity(Enum):
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"


@dataclass
class Card:
    id: str
    name: str
    card_type: CardType
    cost: int
    power: int
    description: str
    rarity: Rarity = Rarity.COMMON
    # Transient power modifier for the current round only (reset each round)
    _power_bonus: int = field(default=0, repr=False, compare=False)
    # If True, card goes to exhausted pile instead of discard after playing
    exhaust: bool = False
    # Squad scaling: key references Squad.scale_factor(); bonus = int(scale_factor * squad_scale_mult)
    squad_scale: str | None = field(default=None, repr=False, compare=False)
    squad_scale_mult: float = field(default=1.0, repr=False, compare=False)

    def effective_power(self) -> int:
        return self.power + self._power_bonus

    def copy(self) -> Card:
        import copy
        c = copy.copy(self)
        c._power_bonus = 0
        return c

    def __str__(self) -> str:
        cost_str = f"[{self.cost}]"
        type_str = self.card_type.value[:3].upper()
        pwr_str = f"Pwr:{self.effective_power()}" if self.power > 0 else "     "
        return f"{cost_str} {self.name:<22} {type_str} {pwr_str}  {self.description}"
