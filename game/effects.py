"""
Effect resolution for cards with side effects beyond raw power.
apply_effect(card_id, actor, target, state) → list[str] (log lines)
"""
from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.player import Player


def apply_effect(card_id: str, actor: "Player", target: "Player", state) -> list[str]:
    handler = _HANDLERS.get(card_id)
    if handler is None:
        return []
    return handler(actor, target, state)


# ── Helper ────────────────────────────────────────────────────────────────────

def _draw(actor: "Player", n: int) -> list[str]:
    drawn = actor.draw_cards(n)
    if not drawn:
        return []
    names = ", ".join(c.name for c in drawn)
    return [f"{actor.name} draws: {names}."]


def _discard_random(target: "Player", n: int = 1) -> list[str]:
    logs = []
    for _ in range(n):
        if not target.hand:
            break
        card = random.choice(target.hand)
        target.force_discard(card)
        logs.append(f"{target.name} discards {card.name}.")
    return logs


# ══════════════════════════════════════════════════════════════════════════════
# ATTACK CARD EFFECTS
# ══════════════════════════════════════════════════════════════════════════════

def _chip_shot(actor, target, state):
    return _draw(actor, 1)


def _poachers_finish(actor, target, state):
    actor.energy += 1
    return [f"{actor.name} poaches — gains 1 energy (now {actor.energy})."]


def _thunderbolt(actor, target, state):
    return _discard_random(target, 1) or [f"{target.name} has no cards to discard."]


def _driven_cross(actor, target, state):
    return _draw(actor, 1)


def _false_nine(actor, target, state):
    """Discard opponent's lowest-power card (the striker drops to intercept)."""
    if not target.hand:
        return [f"{target.name} has no cards to discard."]
    card = min(target.hand, key=lambda c: c.effective_power())
    target.force_discard(card)
    return [f"False 9 intercepts — {target.name} loses {card.name}."]


def _all_out_attack(actor, target, state):
    """Squad-scale already set power bonus. Mark the engine state so defense is halved."""
    state.all_out_attack_active = True
    return [f"{actor.name} throws everyone forward! Defence exposed."]


def _late_winner(actor, target, state):
    """If not winning, boost card power to 10."""
    if actor.goals <= target.goals:
        # Find the card in played list and boost it
        state.late_winner_boosted = True
        return [f"LAST-GASP ATTEMPT! {actor.name} goes all-in!"]
    return [f"{actor.name} is already winning — steady now."]


# ══════════════════════════════════════════════════════════════════════════════
# DEFENSE CARD EFFECTS
# ══════════════════════════════════════════════════════════════════════════════

def _goalkeeper_dive(actor, target, state):
    return _draw(actor, 1)


def _sweeper_clear(actor, target, state):
    return _discard_random(target, 1) or [f"{target.name} has no cards to discard."]


def _offside_trap(actor, target, state):
    state.offside_trap_active = True
    return [f"{actor.name} springs the offside trap! Highest attack nullified."]


def _keeper_saves(actor, target, state):
    return _draw(actor, 1)


def _park_the_bus(actor, target, state):
    target.reduced_draw_next = True
    return [f"{actor.name} parks the bus! {target.name} draws one fewer card next round."]


def _high_line(actor, target, state):
    state.high_line_active = True
    return [f"{actor.name} plays a high line — risky, but effective if it holds."]


# ══════════════════════════════════════════════════════════════════════════════
# SPECIAL CARD EFFECTS
# ══════════════════════════════════════════════════════════════════════════════

def _team_press(actor, target, state):
    actor.energy += 1
    return [f"{actor.name} presses — gains 1 energy (now {actor.energy})."]


def _halftime_talk(actor, target, state):
    logs = [f"The manager's speech fires up {actor.name}!"]
    logs += _draw(actor, 3)
    return logs


def _formation_shift(actor, target, state):
    actor.next_defense_free = True
    return [f"{actor.name} shifts formation — next Defense card costs 0."]


def _captains_order(actor, target, state):
    for card in actor.hand:
        card._power_bonus += 2
    return [f"{actor.name}'s captain rallies the troops — all hand cards +2 power!"]


def _scout_report(actor, target, state):
    logs = []
    if target.hand:
        names = ", ".join(c.name for c in target.hand)
        state.peeked_hand = names
        if actor.is_human:
            logs.append(f"Scouted {target.name}'s hand: {names}")
    logs += _draw(actor, 1)
    return logs


def _injury_time(actor, target, state):
    if not state.injury_time_used:
        state.max_rounds += 1
        state.injury_time_used = True
        return [f"The referee signals INJURY TIME! One extra round ({state.max_rounds} total)."]
    return ["The referee waves away the protest."]


def _tactical_sub(actor, target, state):
    actor.next_attack_bonus = 2
    logs = [f"{actor.name} makes a tactical change — next ATK card +2."]
    logs += _draw(actor, 2)
    return logs


def _tactical_foul(actor, target, state):
    if not target.hand:
        return [f"{target.name} has an empty hand."]
    card = max(target.hand, key=lambda c: c.cost)
    target.force_discard(card)
    return [f"Tactical foul — {target.name} loses {card.name}!"]


def _gegenpress(actor, target, state):
    val = actor.squad.scale_factor("mid_att") if actor.squad else 0
    state.gegenpress_active = True
    state.gegenpress_value  = val
    return [f"Gegenpress! MID adds {val} to both attack and defense this round."]


def _pressing_trigger(actor, target, state):
    logs = _discard_random(target, 2)
    return logs or [f"{target.name} had nothing to discard."]


def _managers_gamble(actor, target, state):
    from game.card import CardType
    pile = actor.deck.draw_pile
    top3 = pile[-3:] if len(pile) >= 3 else pile[:]
    atk_cards = [c for c in top3 if c.card_type == CardType.ATTACK]
    rest       = [c for c in top3 if c.card_type != CardType.ATTACK]
    # Move attack cards to hand, discard the rest
    for c in top3:
        if c in pile:
            pile.remove(c)
    actor.hand.extend(atk_cards)
    actor.deck.discard_pile.extend(rest)
    names = ", ".join(c.name for c in atk_cards) if atk_cards else "nothing useful"
    return [f"Manager's gamble reveals: kept {names}."]


def _pressing_trap(actor, target, state):
    val = actor.squad.scale_factor("mid_total") if actor.squad else 0
    state.pressing_trap_active = True
    state.pressing_trap_value  = val
    return [f"Pressing trap set — if {target.name} plays no defense, {val} bonus attack!"]


def _injury_time_drama(actor, target, state):
    if not state.injury_time_used:
        state.max_rounds += 1
        state.injury_time_used = True
    actor.bonus_energy_next_round += 2
    return [f"DRAMA! Extra time and {actor.name} gets +2 energy next round!"]


def _cup_final_spirit(actor, target, state):
    # Boost all already-played cards by +1
    state.cup_final_spirit_active = True
    logs = [f"{actor.name} digs deep — all played cards get +1 power!"]
    logs += _draw(actor, 1)
    return logs


# ── Dispatch table ─────────────────────────────────────────────────────────────

_HANDLERS: dict = {
    # Attack
    "chip_shot":         _chip_shot,
    "poachers_finish":   _poachers_finish,
    "thunderbolt":       _thunderbolt,
    "driven_cross":      _driven_cross,
    "false_nine":        _false_nine,
    "all_out_attack":    _all_out_attack,
    "late_winner":       _late_winner,
    # Defense
    "goalkeeper_dive":   _goalkeeper_dive,
    "sweeper_clear":     _sweeper_clear,
    "offside_trap":      _offside_trap,
    "keeper_saves":      _keeper_saves,
    "park_the_bus":      _park_the_bus,
    "high_line":         _high_line,
    # Special
    "team_press":        _team_press,
    "halftime_talk":     _halftime_talk,
    "formation_shift":   _formation_shift,
    "captains_order":    _captains_order,
    "scout_report":      _scout_report,
    "injury_time":       _injury_time,
    "tactical_sub":      _tactical_sub,
    "tactical_foul":     _tactical_foul,
    "gegenpress":        _gegenpress,
    "pressing_trigger":  _pressing_trigger,
    "managers_gamble":   _managers_gamble,
    "pressing_trap":     _pressing_trap,
    "injury_time_drama": _injury_time_drama,
    "cup_final_spirit":  _cup_final_spirit,
}
