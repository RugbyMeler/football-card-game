from __future__ import annotations
import random
from game.card import Card

HAND_LIMIT = 7


class Deck:
    def __init__(self, cards: list[Card]):
        self.draw_pile: list[Card] = list(cards)
        self.hand: list[Card] = []
        self.discard_pile: list[Card] = []
        self.exhausted: list[Card] = []
        random.shuffle(self.draw_pile)

    # ── Drawing ──────────────────────────────────────────────────────────────

    def draw(self, n: int = 1) -> list[Card]:
        """Draw up to n cards, reshuffling discard into draw if needed."""
        drawn: list[Card] = []
        for _ in range(n):
            if len(self.hand) >= HAND_LIMIT:
                break
            if not self.draw_pile:
                if not self.discard_pile:
                    break
                self._reshuffle()
            card = self.draw_pile.pop()
            self.hand.append(card)
            drawn.append(card)
        return drawn

    def _reshuffle(self) -> None:
        self.draw_pile = self.discard_pile[:]
        self.discard_pile = []
        random.shuffle(self.draw_pile)

    # ── Playing / discarding ─────────────────────────────────────────────────

    def play(self, card: Card) -> None:
        """Move card from hand to discard (or exhausted if card.exhaust)."""
        self.hand.remove(card)
        if card.exhaust:
            self.exhausted.append(card)
        else:
            self.discard_pile.append(card)

    def discard_from_hand(self, card: Card) -> None:
        """Force-discard a card from hand (e.g. from opponent effect)."""
        if card in self.hand:
            self.hand.remove(card)
            self.discard_pile.append(card)

    def discard_all_hand(self) -> None:
        """End-of-round: move entire hand to discard."""
        self.discard_pile.extend(self.hand)
        self.hand = []

    # ── Deck editing (between matches) ───────────────────────────────────────

    def add_card(self, card: Card) -> None:
        self.discard_pile.append(card)

    def remove_card(self, card: Card) -> bool:
        """Remove a card permanently from the deck (thinning). Returns True if found."""
        for pile in (self.draw_pile, self.discard_pile, self.hand):
            if card in pile:
                pile.remove(card)
                return True
        return False

    def all_cards(self) -> list[Card]:
        """All cards in the deck (draw + discard + hand, excludes exhausted)."""
        return self.draw_pile + self.discard_pile + self.hand

    def reset_for_match(self) -> None:
        """Gather all cards, including exhausted, reshuffle for a fresh match."""
        all_cards = self.draw_pile + self.discard_pile + self.hand + self.exhausted
        self.exhausted = []
        self.hand = []
        self.discard_pile = []
        self.draw_pile = all_cards
        random.shuffle(self.draw_pile)

    def size(self) -> int:
        return len(self.draw_pile) + len(self.discard_pile)

    def __len__(self) -> int:
        return self.size()
