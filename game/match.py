"""Match orchestration — runs a single match between a human player and an AI opponent."""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from game.card import Card, CardType
from game.player import Player
from game import effects, ui

BASE_ROUNDS = 9


@dataclass
class MatchState:
    max_rounds: int = BASE_ROUNDS
    offside_trap_active: bool = False   # Set by Offside Trap card; consumed in resolution
    injury_time_used: bool = False
    peeked_hand: str | None = None      # Set by Scout Report for display


class Match:
    def __init__(self, player: Player, opponent: Player):
        self.player = player
        self.opponent = opponent
        self.state = MatchState()

    def play(self) -> bool:
        """Run the full match. Returns True if the player wins or draws."""
        self.player.start_of_match()
        self.opponent.start_of_match()

        for round_num in range(1, self.state.max_rounds + 1):
            # Halftime pause between rounds 4→5 in a 9-round match
            if round_num == BASE_ROUNDS // 2 + 2:
                ui.print_halftime(
                    self.player.goals, self.opponent.goals,
                    self.player.name, self.opponent.name,
                )

            ui.print_round_header(
                round_num, self.state.max_rounds,
                self.player.goals, self.opponent.goals,
                self.player.name, self.opponent.name,
            )

            self.player.start_of_round()
            self.opponent.start_of_round()

            # Reset per-round match state flags
            self.state.offside_trap_active = False
            self.state.peeked_hand = None

            # Player and AI plan their plays
            p_played = self._human_turn(self.player, self.opponent)
            o_played = self._ai_turn(self.opponent, self.player)

            # Reveal AI cards
            ui.print_played_cards(self.opponent.name, o_played)

            # Collect special-card effect logs (applied during play phase)
            # Resolution: total up attack vs defense
            p_atk = sum(c.effective_power() for c in p_played if c.card_type == CardType.ATTACK)
            p_def = sum(c.effective_power() for c in p_played if c.card_type == CardType.DEFENSE)
            o_atk = sum(c.effective_power() for c in o_played if c.card_type == CardType.ATTACK)
            o_def = sum(c.effective_power() for c in o_played if c.card_type == CardType.DEFENSE)

            # Offside Trap: zero out the opponent's highest-power attack card
            if self.state.offside_trap_active:
                atk_cards = [c for c in o_played if c.card_type == CardType.ATTACK]
                if atk_cards:
                    top = max(atk_cards, key=lambda c: c.effective_power())
                    o_atk -= top.effective_power()

            # Determine goals
            if p_atk > o_def:
                self.player.goals += 1
            if o_atk > p_def:
                self.opponent.goals += 1

            ui.print_resolution(
                self.player.name, p_atk, p_def,
                self.opponent.name, o_atk, o_def,
                log=[],  # Effects already printed inline during play
            )
            ui.print_score_line(
                self.player.name, self.player.goals,
                self.opponent.name, self.opponent.goals,
            )

            self.player.end_of_round()
            self.opponent.end_of_round()

            # Injury Time can extend the match mid-loop
            if round_num == self.state.max_rounds and self.state.max_rounds > BASE_ROUNDS:
                pass  # Already extended; loop condition handles it

            ui.pause()

        ui.print_match_result(
            self.player.name, self.player.goals,
            self.opponent.name, self.opponent.goals,
        )
        return self.player.goals >= self.opponent.goals

    # ── Human turn ────────────────────────────────────────────────────────────

    def _human_turn(self, player: Player, opponent: Player) -> list[Card]:
        played: list[Card] = []
        ui.print_player_turn_header(player)
        while True:
            ui.print_hand(player, played)
            choice = ui.get_play_choice(player)
            if choice == "done":
                break
            idx = int(choice)
            card = player.hand[idx]
            if not player.can_play(card):
                print("  Not enough energy!")
                continue
            player.spend_and_play(card)
            played.append(card)
            print(f"  Played: {card.name}", end="")
            if card.power > 0:
                print(f"  (Power {card.effective_power()})", end="")
            print()
            # Apply side effects immediately
            logs = effects.apply_effect(card.id, player, opponent, self.state)
            for line in logs:
                print(f"  > {line}")
        ui.print_played_cards(player.name, played)
        return played

    # ── AI turn ───────────────────────────────────────────────────────────────

    def _ai_turn(self, ai: Player, human: Player) -> list[Card]:
        """Simple AI: play cards according to strategy, spending energy greedily."""
        from data.opponents import Strategy
        strategy = getattr(ai, "_strategy", Strategy.BALANCED)

        played: list[Card] = []
        hand = list(ai.hand)  # snapshot

        # Sort candidates by type preference
        def priority(card: Card) -> tuple:
            type_order = {
                CardType.SPECIAL: 0,
                CardType.ATTACK: 1 if strategy == Strategy.AGGRESSIVE else 2,
                CardType.DEFENSE: 1 if strategy == Strategy.DEFENSIVE else 2,
            }
            return (type_order.get(card.card_type, 3), -card.effective_power())

        candidates = sorted(hand, key=priority)

        for card in candidates:
            if ai.can_play(card):
                ai.spend_and_play(card)
                played.append(card)
                logs = effects.apply_effect(card.id, ai, human, self.state)
                for line in logs:
                    print(f"  > {line}")
                if ai.energy <= 0:
                    break

        return played
