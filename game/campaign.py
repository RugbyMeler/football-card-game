"""Campaign state — shared between graphical and text modes."""
from __future__ import annotations
import json
import random
from pathlib import Path

from game.card import Card
from game.deck import Deck
from game.player import Player
from game.squad import Squad
from data.opponents import OPPONENT_ROSTER, OpponentDef, Strategy
from data.cards import get as get_card, CARD_BY_ID
from data.players import build_starter_squad, build_opponent_squad, PLAYER_BY_ID

SAVE_FILE = Path("save.json")

# ── Starter deck ──────────────────────────────────────────────────────────────

STARTER_DECK_IDS: list[str] = [
    "long_shot",      "long_shot",
    "header",         "header",
    "tap_in",         "tap_in",
    "standard_block", "standard_block", "standard_block",
    "sliding_tackle", "sliding_tackle",
    "strikers_run",
    "team_press",
    "halftime_talk",
]


def build_deck_from_ids(ids: list[str]) -> Deck:
    return Deck([get_card(cid) for cid in ids])


def build_opponent_player(opp_def: OpponentDef) -> Player:
    deck  = build_deck_from_ids(opp_def.deck_ids)
    squad = build_opponent_squad(opp_def.difficulty)
    p = Player(opp_def.name, deck, is_human=False, squad=squad)
    p._strategy = opp_def.strategy  # type: ignore[attr-defined]
    return p


# ── Save / load ───────────────────────────────────────────────────────────────

def save_campaign(player_name: str, deck_ids: list[str], opponent_index: int,
                  wins: int, losses: int, squad: Squad | None = None) -> None:
    data: dict = {
        "player_name":     player_name,
        "deck_ids":        deck_ids,
        "opponent_index":  opponent_index,
        "wins":            wins,
        "losses":          losses,
    }
    if squad is not None:
        data["squad"] = squad.to_dict()
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass  # no writable filesystem in web build — saves are silently skipped


def load_campaign() -> dict | None:
    try:
        if not SAVE_FILE.exists():
            return None
        with open(SAVE_FILE) as f:
            return json.load(f)
    except OSError:
        return None


def delete_save() -> None:
    try:
        if SAVE_FILE.exists():
            SAVE_FILE.unlink()
    except OSError:
        pass


# ── Campaign ──────────────────────────────────────────────────────────────────

class Campaign:
    def __init__(self, player_name: str, deck_ids: list[str],
                 opponent_index: int = 0, wins: int = 0, losses: int = 0,
                 squad: Squad | None = None):
        self.player_name    = player_name
        self.deck_ids       = list(deck_ids)
        self.opponent_index = opponent_index
        self.wins           = wins
        self.losses         = losses
        self.squad: Squad   = squad or build_starter_squad()

    @classmethod
    def new(cls, player_name: str) -> Campaign:
        return cls(player_name, STARTER_DECK_IDS, squad=build_starter_squad())

    @classmethod
    def from_save(cls, data: dict) -> Campaign:
        squad = None
        if "squad" in data:
            try:
                squad = Squad.from_dict(data["squad"], PLAYER_BY_ID)
            except Exception:
                pass
        return cls(
            player_name    = data["player_name"],
            deck_ids       = data["deck_ids"],
            opponent_index = data["opponent_index"],
            wins           = data.get("wins", 0),
            losses         = data.get("losses", 0),
            squad          = squad,
        )

    def save(self) -> None:
        save_campaign(self.player_name, self.deck_ids, self.opponent_index,
                      self.wins, self.losses, self.squad)

    # ── Text-mode run (unchanged behaviour, squad not shown in text mode) ─────

    def run(self) -> None:
        from game import ui
        from game.match import Match

        ui.clear_screen()
        print(f"\n  Welcome back, {self.player_name}!")
        print(f"  Record: {self.wins}W / {self.losses}L")
        if self.opponent_index < len(OPPONENT_ROSTER):
            print(f"  Next opponent: {OPPONENT_ROSTER[self.opponent_index].team}\n")
        ui.pause("  [Press Enter to begin...]")

        while self.opponent_index < len(OPPONENT_ROSTER):
            opp_def = OPPONENT_ROSTER[self.opponent_index]
            self._pre_match_screen(opp_def)

            player   = Player(self.player_name, build_deck_from_ids(self.deck_ids),
                               squad=self.squad)
            opponent = build_opponent_player(opp_def)

            match = Match(player, opponent)
            won = match.play()

            if won:
                self.wins += 1
                self._post_match_win(opp_def)
                self.opponent_index += 1
            else:
                self.losses += 1
                print("\n  Back to the training ground. Try again.")
                ui.pause()

            self.save()

        self._campaign_complete()

    def _pre_match_screen(self, opp_def: OpponentDef) -> None:
        from game import ui
        ui.clear_screen()
        print(ui.HEAVY)
        print(f"  NEXT MATCH".center(ui.WIDTH))
        print(ui.HEAVY)
        print(f"\n  {opp_def.team}  |  Manager: {opp_def.name}")
        print(f"  Difficulty: {'*' * opp_def.difficulty}")
        print(f"\n  \"{opp_def.description}\"")
        print(f"\n  Record: {self.wins}W / {self.losses}L  |  Deck: {len(self.deck_ids)} cards")
        print()
        ui.pause("  [Press Enter to kick off...]")

    def _post_match_win(self, opp_def: OpponentDef) -> None:
        from game import ui
        print("\n  Great result!")
        if opp_def.reward_pool:
            pool = [get_card(cid) for cid in random.sample(
                opp_def.reward_pool, min(3, len(opp_def.reward_pool)))]
            ui.print_card_reward(pool)
            choice = ui.get_card_index(len(pool))
            self.deck_ids.append(pool[choice].id)
            print(f"\n  Added {pool[choice].name} to your deck!")
        all_cards = [CARD_BY_ID[cid] for cid in self.deck_ids]
        ui.print_deck_thinning(all_cards)
        remove_idx = ui.get_card_index(len(all_cards), allow_skip=True)
        if remove_idx is not None:
            removed = self.deck_ids.pop(remove_idx)
            print(f"\n  Removed {CARD_BY_ID[removed].name} from deck.")
        ui.pause()

    def _campaign_complete(self) -> None:
        from game import ui
        ui.clear_screen()
        print(ui.HEAVY)
        print("  SEASON COMPLETE!".center(ui.WIDTH))
        print(ui.HEAVY)
        print(f"\n  Final record: {self.wins}W / {self.losses}L")
        print("\n  Champions!")
        delete_save()
        ui.pause("  [Press Enter to return to main menu...]")
