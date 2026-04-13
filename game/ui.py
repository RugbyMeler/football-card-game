"""All user-facing display and input functions."""
from __future__ import annotations
from game.card import Card, CardType, Rarity
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.player import Player

WIDTH = 60
DIVIDER = "─" * WIDTH
HEAVY = "═" * WIDTH


# ── Helpers ──────────────────────────────────────────────────────────────────

def _rarity_tag(r: Rarity) -> str:
    return {"Common": " ", "Uncommon": "*", "Rare": "**"}[r.value]


def clear_screen() -> None:
    import os
    os.system("cls" if os.name == "nt" else "clear")


def pause(prompt: str = "  [Press Enter to continue...]") -> None:
    input(prompt)


# ── Title / menus ────────────────────────────────────────────────────────────

def print_title() -> None:
    print()
    print(HEAVY)
    print("  FOOTBALL CARD GAME".center(WIDTH))
    print("  Build your deck. Outscore the opposition.".center(WIDTH))
    print(HEAVY)
    print()


def print_main_menu() -> None:
    print("  [1] New Campaign")
    print("  [2] Load Campaign")
    print("  [3] Quit")
    print()


def get_menu_choice(options: list[str]) -> str:
    while True:
        choice = input("  > ").strip().lower()
        if choice in options:
            return choice
        print(f"  Please enter one of: {', '.join(options)}")


# ── Match display ────────────────────────────────────────────────────────────

def print_match_header(player_name: str, opp_name: str, opp_team: str) -> None:
    print()
    print(HEAVY)
    print(f"  MATCH: {player_name}  vs  {opp_name} ({opp_team})".center(WIDTH))
    print(HEAVY)
    print()


def print_round_header(round_num: int, max_rounds: int,
                        p_goals: int, o_goals: int,
                        p_name: str, o_name: str) -> None:
    half = "1st Half" if round_num <= max_rounds // 2 else "2nd Half"
    print()
    print(DIVIDER)
    print(f"  Round {round_num}/{max_rounds}  |  {half}  |  "
          f"{p_name} {p_goals} - {o_goals} {o_name}")
    print(DIVIDER)


def print_halftime(p_goals: int, o_goals: int, p_name: str, o_name: str) -> None:
    print()
    print(HEAVY)
    print("  HALF TIME".center(WIDTH))
    print(f"  {p_name} {p_goals}  -  {o_goals} {o_name}".center(WIDTH))
    print(HEAVY)
    pause()


def print_score_line(p_name: str, p_goals: int, o_name: str, o_goals: int) -> None:
    print(f"\n  SCORE: {p_name} {p_goals} - {o_goals} {o_name}")


# ── Player turn display ───────────────────────────────────────────────────────

def print_player_turn_header(player: "Player") -> None:
    print(f"\n  YOUR TURN  |  Energy: {player.energy}/{player.max_energy}  |  "
          f"Deck: {player.deck.size()} remaining")


def print_hand(player: "Player", played_this_turn: list[Card] | None = None) -> None:
    played_this_turn = played_this_turn or []
    print("\n  Your hand:")
    if not player.hand:
        print("    (empty)")
        return
    for i, card in enumerate(player.hand):
        cost = card.cost
        # Check if formation_shift makes this free
        if card.card_type == CardType.DEFENSE and player.next_defense_free:
            cost = 0
        affordable = "+" if player.energy >= cost else " "
        rarity = _rarity_tag(card.rarity)
        print(f"    [{i}]{affordable}{rarity} {card}")
    print()
    print(f"  Energy remaining: {player.energy}  |  [d] Done playing")


def print_played_cards(player_name: str, cards: list[Card]) -> None:
    if not cards:
        print(f"  {player_name} plays nothing.")
        return
    print(f"\n  {player_name} plays:")
    for card in cards:
        pwr = f"  (Power {card.effective_power()})" if card.power > 0 else ""
        print(f"    - {card.name}{pwr}")


def print_resolution(
    p_name: str, p_atk: int, p_def: int,
    o_name: str, o_atk: int, o_def: int,
    log: list[str],
) -> None:
    print(f"\n  {DIVIDER}")
    print("  ROUND RESOLUTION")
    print(f"  {DIVIDER}")

    # Special card log
    for line in log:
        print(f"  > {line}")

    print(f"\n  {p_name} attacks:  {p_atk:>3}  vs  {o_name} defends: {o_def:>3}", end="  ")
    if p_atk > o_def:
        print(f"=> GOAL! {p_name} scores!")
    else:
        print(f"=> Saved / Cleared")

    print(f"  {o_name} attacks:  {o_atk:>3}  vs  {p_name} defends: {p_def:>3}", end="  ")
    if o_atk > p_def:
        print(f"=> GOAL! {o_name} scores!")
    else:
        print(f"=> Saved / Cleared")


def print_match_result(p_name: str, p_goals: int, o_name: str, o_goals: int) -> None:
    print()
    print(HEAVY)
    print("  FULL TIME".center(WIDTH))
    print(f"  {p_name} {p_goals}  -  {o_goals} {o_name}".center(WIDTH))
    print(HEAVY)
    if p_goals > o_goals:
        print("\n  YOU WIN! Outstanding result.")
    elif o_goals > p_goals:
        print("\n  YOU LOSE. Regroup and try again.")
    else:
        print("\n  IT'S A DRAW. A point each.")
    print()


# ── Card reward / deck management ────────────────────────────────────────────

def print_card_reward(cards: list[Card]) -> None:
    print()
    print(DIVIDER)
    print("  CARD REWARD — Choose 1 card to add to your deck:")
    print(DIVIDER)
    for i, card in enumerate(cards):
        rarity = _rarity_tag(card.rarity)
        print(f"    [{i}]{rarity} {card}")
    print()


def print_deck_thinning(deck_cards: list[Card]) -> None:
    print()
    print(DIVIDER)
    print("  DECK MANAGEMENT — Remove 1 card (or skip):")
    print(DIVIDER)
    for i, card in enumerate(deck_cards):
        print(f"    [{i}] {card}")
    print("    [s] Skip")
    print()


def get_card_index(max_idx: int, allow_skip: bool = False) -> int | None:
    options = [str(i) for i in range(max_idx)]
    if allow_skip:
        options.append("s")
    while True:
        choice = input("  > ").strip().lower()
        if allow_skip and choice == "s":
            return None
        if choice.isdigit() and int(choice) in range(max_idx):
            return int(choice)
        print(f"  Enter a number 0-{max_idx - 1}" + (" or 's' to skip" if allow_skip else "") + ".")


def get_play_choice(player: "Player") -> int | str:
    """Returns a card index or 'done'."""
    while True:
        raw = input("  Play card #  (or d=done): ").strip().lower()
        if raw == "d":
            return "done"
        if raw.isdigit():
            idx = int(raw)
            if 0 <= idx < len(player.hand):
                return idx
        print("  Invalid choice.")
