from __future__ import annotations
from game.card import Card, CardType
from game.deck import Deck

BASE_ENERGY   = 3
DRAW_PER_ROUND = 2
OPENING_HAND  = 5


class Player:
    def __init__(self, name: str, deck: Deck, is_human: bool = True, squad=None):
        self.name      = name
        self.deck      = deck
        self.is_human  = is_human
        self.squad     = squad   # game.squad.Squad | None
        self.goals: int = 0

        # Per-round energy
        self.energy:     int = 0
        self.max_energy: int = BASE_ENERGY

        # ── Per-round status flags (all reset in start_of_round) ───────────────
        self.next_defense_free: bool = False   # Formation Shift
        self.hand_power_bonus:  int  = 0       # Captain's Order
        self.next_attack_bonus: int  = 0       # Tactical Sub

        # ── Carry-over flags (consumed at start of NEXT round) ─────────────────
        self.reduced_draw_next:      bool = False  # Park the Bus
        self.energy_penalty_next:    int  = 0      # High Line
        self.bonus_energy_next_round: int = 0      # Injury Time Drama

    # ── Hand accessor ─────────────────────────────────────────────────────────

    @property
    def hand(self) -> list[Card]:
        return self.deck.hand

    # ── Match / round lifecycle ───────────────────────────────────────────────

    def start_of_match(self) -> None:
        self.goals = 0
        self.energy = self.max_energy   # fix: energy must be set for round 1
        self.deck.reset_for_match()
        self.deck.draw(OPENING_HAND)

    def start_of_round(self) -> None:
        # Base energy with carry-over modifiers
        self.energy = max(0, self.max_energy
                          + self.bonus_energy_next_round
                          - self.energy_penalty_next)
        self.bonus_energy_next_round = 0
        self.energy_penalty_next     = 0

        # Per-round flags reset
        self.next_defense_free = False
        self.hand_power_bonus  = 0
        self.next_attack_bonus = 0

        # Reset card power bonuses on cards left in hand
        for card in self.hand:
            card._power_bonus = 0

        # Draw up to fill hand to 5; Park the Bus penalty reduces target to 4
        target = OPENING_HAND - (1 if self.reduced_draw_next else 0)
        self.reduced_draw_next = False
        draw_n = max(0, target - len(self.hand))
        self.deck.draw(draw_n)

    def end_of_round(self) -> None:
        pass  # unplayed cards stay in hand and carry over to the next round

    # ── Playing cards ─────────────────────────────────────────────────────────

    def can_play(self, card: Card) -> bool:
        if card not in self.hand:
            return False
        return self.energy >= self._effective_cost(card)

    def _effective_cost(self, card: Card) -> int:
        if card.card_type == CardType.DEFENSE and self.next_defense_free:
            return 0
        return card.cost

    def spend_and_play(self, card: Card) -> None:
        self.energy -= self._effective_cost(card)
        if card.card_type == CardType.DEFENSE and self.next_defense_free:
            self.next_defense_free = False
        self.deck.play(card)

    def draw_cards(self, n: int) -> list[Card]:
        return self.deck.draw(n)

    def force_discard(self, card: Card) -> None:
        self.deck.discard_from_hand(card)
