"""
MatchEngine — event-driven match logic.
The pygame match screen reads properties each frame and calls methods
on mouse events.  No blocking I/O.
"""
from __future__ import annotations
import random
from enum import Enum, auto
from dataclasses import dataclass, field
from game.card import Card, CardType
from game.player import Player
from game import effects
from data.opponents import Strategy


class Phase(Enum):
    PLAYER_SELECTING = auto()
    RESOLUTION       = auto()
    HALF_TIME        = auto()
    MATCH_END        = auto()


@dataclass
class RoundResult:
    p_attack:  int = 0
    p_defense: int = 0
    o_attack:  int = 0
    o_defense: int = 0
    p_base_atk: int = 0   # squad passive contribution (display only)
    p_base_def: int = 0
    o_base_atk: int = 0
    o_base_def: int = 0
    p_scored:  bool = False
    o_scored:  bool = False
    offside_nullified: bool = False
    log: list[str] = field(default_factory=list)


class _StateProxy:
    """Duck-typed stand-in for MatchState expected by effects.py."""
    def __init__(self, engine: "MatchEngine"):
        self._e = engine

    def _prop(name, default=None):
        """Helper to define a proxied attribute."""
        def getter(self): return getattr(self._e, name, default)
        def setter(self, v): setattr(self._e, name, v)
        return property(getter, setter)

    offside_trap_active   = _prop("offside_trap_active", False)
    injury_time_used      = _prop("injury_time_used", False)
    gegenpress_active     = _prop("gegenpress_active", False)
    gegenpress_value      = _prop("gegenpress_value", 0)
    pressing_trap_active  = _prop("pressing_trap_active", False)
    pressing_trap_value   = _prop("pressing_trap_value", 0)
    all_out_attack_active = _prop("all_out_attack_active", False)
    high_line_active      = _prop("high_line_active", False)
    cup_final_spirit_active = _prop("cup_final_spirit_active", False)
    late_winner_boosted   = _prop("late_winner_boosted", False)

    @property
    def max_rounds(self): return self._e.max_rounds
    @max_rounds.setter
    def max_rounds(self, v): self._e.max_rounds = v

    @property
    def peeked_hand(self): return None
    @peeked_hand.setter
    def peeked_hand(self, v):
        if v:
            self._e.effect_log.append(f"Opponent's hand: {v}")


class MatchEngine:
    BASE_ROUNDS = 9

    def __init__(self, player: Player, opponent: Player,
                 player_squad=None, opponent_squad=None):
        self.player   = player
        self.opponent = opponent
        self.player_squad   = player_squad   or getattr(player,   "squad", None)
        self.opponent_squad = opponent_squad or getattr(opponent, "squad", None)

        self.round_num  = 1
        self.max_rounds = self.BASE_ROUNDS
        self.phase      = Phase.PLAYER_SELECTING

        # Per-round
        self.p_played: list[Card] = []
        self.o_played: list[Card] = []
        self.result:   RoundResult | None = None
        self.effect_log: list[str] = []

        # State flags (reset each round)
        self.offside_trap_active    = False
        self.injury_time_used       = False
        self.gegenpress_active      = False
        self.gegenpress_value       = 0
        self.pressing_trap_active   = False
        self.pressing_trap_value    = 0
        self.all_out_attack_active  = False
        self.high_line_active       = False
        self.cup_final_spirit_active = False
        self.late_winner_boosted    = False

        player.start_of_match()
        opponent.start_of_match()

    # ── Player actions ────────────────────────────────────────────────────────

    def play_card(self, card: Card) -> tuple[bool, list[str]]:
        if self.phase != Phase.PLAYER_SELECTING:
            return False, []
        if not self.player.can_play(card):
            return False, []

        self.player.spend_and_play(card)

        # Squad scaling bonus
        if card.squad_scale and self.player_squad:
            raw = self.player_squad.scale_factor(card.squad_scale)
            card._power_bonus = int(raw * card.squad_scale_mult)

        # Tactical Sub: next ATK card gets +2
        if card.card_type == CardType.ATTACK and self.player.next_attack_bonus:
            card._power_bonus += self.player.next_attack_bonus
            self.player.next_attack_bonus = 0

        # Late Winner: if not winning, boost to power 10
        if card.id == "late_winner" and self.player.goals <= self.opponent.goals:
            card._power_bonus = max(0, 10 - card.power)

        self.p_played.append(card)

        proxy = _StateProxy(self)
        logs = effects.apply_effect(card.id, self.player, self.opponent, proxy)
        self.effect_log.extend(logs)
        return True, logs

    def end_turn(self) -> None:
        if self.phase != Phase.PLAYER_SELECTING:
            return
        proxy = _StateProxy(self)
        self.o_played = self._ai_play(proxy)
        self._resolve_round(proxy)
        self.phase = Phase.RESOLUTION

    def advance(self) -> None:
        if self.phase == Phase.RESOLUTION:
            self.player.end_of_round()
            self.opponent.end_of_round()
            self.round_num += 1

            if self.round_num > self.max_rounds:
                self.phase = Phase.MATCH_END
            elif self.round_num == self.BASE_ROUNDS // 2 + 1:
                self.phase = Phase.HALF_TIME
            else:
                self._start_round()

        elif self.phase == Phase.HALF_TIME:
            self._start_round()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _start_round(self) -> None:
        self.player.start_of_round()
        self.opponent.start_of_round()
        self.p_played    = []
        self.o_played    = []
        self.result      = None
        self.effect_log  = []
        self.offside_trap_active    = False
        self.gegenpress_active      = False
        self.gegenpress_value       = 0
        self.pressing_trap_active   = False
        self.pressing_trap_value    = 0
        self.all_out_attack_active  = False
        self.high_line_active       = False
        self.cup_final_spirit_active = False
        self.late_winner_boosted    = False
        self.phase = Phase.PLAYER_SELECTING

    def _resolve_round(self, proxy) -> None:
        r = RoundResult()

        # Apply AI card side effects
        for card in self.o_played:
            # AI squad scaling
            if card.squad_scale and self.opponent_squad:
                raw = self.opponent_squad.scale_factor(card.squad_scale)
                card._power_bonus = int(raw * card.squad_scale_mult)
            logs = effects.apply_effect(card.id, self.opponent, self.player, proxy)
            self.effect_log.extend(logs)

        # Sum card powers
        r.p_attack  = sum(c.effective_power() for c in self.p_played
                          if c.card_type == CardType.ATTACK)
        r.p_defense = sum(c.effective_power() for c in self.p_played
                          if c.card_type == CardType.DEFENSE)
        r.o_attack  = sum(c.effective_power() for c in self.o_played
                          if c.card_type == CardType.ATTACK)
        r.o_defense = sum(c.effective_power() for c in self.o_played
                          if c.card_type == CardType.DEFENSE)

        # Cup Final Spirit: all played cards +1
        if self.cup_final_spirit_active:
            played_count = len(self.p_played)
            r.p_attack  += sum(1 for c in self.p_played if c.card_type == CardType.ATTACK)
            r.p_defense += sum(1 for c in self.p_played if c.card_type == CardType.DEFENSE)

        # Gegenpress: MID att_power added to both totals
        if self.gegenpress_active:
            r.p_attack  += self.gegenpress_value
            r.p_defense += self.gegenpress_value

        # Squad passive contributions
        if self.player_squad:
            r.p_base_atk = self.player_squad.base_attack
            r.p_base_def = self.player_squad.base_defense
            r.p_attack  += r.p_base_atk
            r.p_defense += r.p_base_def
        if self.opponent_squad:
            r.o_base_atk = self.opponent_squad.base_attack
            r.o_base_def = self.opponent_squad.base_defense
            r.o_attack  += r.o_base_atk
            r.o_defense += r.o_base_def

        # Pressing Trap: if opponent played no defense, add bonus attack
        if self.pressing_trap_active:
            if not any(c.card_type == CardType.DEFENSE for c in self.o_played):
                r.p_attack += self.pressing_trap_value
                self.effect_log.append(f"Pressing trap fires! +{self.pressing_trap_value} attack!")

        # All Out Attack: double p_attack (squad scale already set _power_bonus to 2× ATT)
        # The squad_scale_mult=2.0 on the card handles this. Nothing extra needed here.

        # Offside Trap: nullify opponent's highest attack card
        if self.offside_trap_active:
            atk_cards = [c for c in self.o_played if c.card_type == CardType.ATTACK]
            if atk_cards:
                top = max(atk_cards, key=lambda c: c.effective_power())
                r.o_attack -= top.effective_power()
                r.offside_nullified = True

        # High Line: if opponent scores, penalise their next-round energy
        r.p_scored = r.p_attack > r.o_defense
        r.o_scored = r.o_attack > r.p_defense

        if r.o_scored and self.high_line_active:
            self.opponent.energy_penalty_next += 1
            self.effect_log.append("High line beaten — opponent loses 1 energy next round.")

        if r.p_scored:
            self.player.goals  += 1
        if r.o_scored:
            self.opponent.goals += 1

        r.log = list(self.effect_log)
        self.result = r

    def _ai_play(self, proxy) -> list[Card]:
        strategy = getattr(self.opponent, "_strategy", Strategy.BALANCED)

        def priority(card: Card) -> tuple:
            order = {
                CardType.SPECIAL: 0,
                CardType.ATTACK:  1 if strategy == Strategy.AGGRESSIVE else 2,
                CardType.DEFENSE: 1 if strategy == Strategy.DEFENSIVE  else 2,
            }
            return (order.get(card.card_type, 3), -card.effective_power())

        played: list[Card] = []
        for card in sorted(list(self.opponent.hand), key=priority):
            if self.opponent.can_play(card):
                self.opponent.spend_and_play(card)
                played.append(card)
                if self.opponent.energy <= 0:
                    break
        return played

    @property
    def player_won(self) -> bool:
        return self.player.goals > self.opponent.goals

    @property
    def is_draw(self) -> bool:
        return self.player.goals == self.opponent.goals
