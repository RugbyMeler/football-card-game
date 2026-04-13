"""The main match gameplay screen."""
from __future__ import annotations
import pygame
from graphics.screens.base import Screen
from graphics.constants import (
    C, SCREEN_W, SCREEN_H, CARD_W, CARD_H, CARD_GAP,
    STATUS_H, OPP_Y, OPP_H, LOG_Y, LOG_H, PLY_Y, PLY_H,
    HAND_Y, HAND_H, ACTION_Y, ACTION_H,
)
from graphics.widgets import (
    Button, EnergyBar, CardWidget, draw_text, blit_wrapped,
    build_card_row, card_row_x,
)
from graphics import fonts
from graphics.engine import MatchEngine, Phase
from game.campaign import Campaign
from game.player import Player
from game.campaign import build_deck_from_ids, build_opponent_player
from data.opponents import OPPONENT_ROSTER
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphics.app import App

_LOG_MAX = 4   # max log lines shown at once


class MatchScreen(Screen):
    def __init__(self, app: "App", campaign: Campaign):
        super().__init__(app)
        self.campaign = campaign

        opp_def  = OPPONENT_ROSTER[campaign.opponent_index]
        player   = Player(campaign.player_name, build_deck_from_ids(campaign.deck_ids),
                          squad=campaign.squad)
        opponent = build_opponent_player(opp_def)

        self.engine  = MatchEngine(player, opponent,
                                   player_squad   = campaign.squad,
                                   opponent_squad = opponent.squad)
        self.opp_def = opp_def

        # Persistent log (shown in log strip)
        self._log: list[str] = []

        # Buttons
        bw, bh = 200, 46
        self._end_turn_btn = Button("End Turn",  SCREEN_W - bw - 20, ACTION_Y + (ACTION_H - bh) // 2, bw, bh)
        self._continue_btn = Button("Continue ▶", SCREEN_W - bw - 20, ACTION_Y + (ACTION_H - bh) // 2, bw, bh)

        # Energy display
        self._energy = EnergyBar(20, ACTION_Y + ACTION_H // 2, max_e=3)

        # Widgets rebuilt each frame (hand changes)
        self._hand_widgets: list[CardWidget]    = []
        self._p_played_widgets: list[CardWidget] = []
        self._o_played_widgets: list[CardWidget] = []

        # Flash colour for goal/save feedback
        self._flash_col: tuple | None = None
        self._flash_ticks = 0

        # Build initial hand widgets
        self._rebuild_hand()

    # ── Event handling ────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None
        pos = event.pos

        phase = self.engine.phase

        if phase == Phase.PLAYER_SELECTING:
            if self._end_turn_btn.clicked(pos):
                self.engine.end_turn()
                self._after_end_turn()
                return None

            for w in self._hand_widgets:
                if w.clicked(pos):
                    ok, logs = self.engine.play_card(w.card)
                    if ok:
                        self._log.extend(logs)
                        self._rebuild_hand()
                        self._rebuild_played_widgets()
                    return None

        elif phase in (Phase.RESOLUTION, Phase.HALF_TIME):
            if self._continue_btn.clicked(pos):
                self.engine.advance()
                if self.engine.phase == Phase.MATCH_END:
                    return self._go_to_result()
                if self.engine.phase == Phase.PLAYER_SELECTING:
                    self._log = []
                    self._rebuild_hand()
                    self._rebuild_played_widgets()
                return None

        elif phase == Phase.MATCH_END:
            if self._continue_btn.clicked(pos):
                return self._go_to_result()

        return None

    def _after_end_turn(self) -> None:
        r = self.engine.result
        if r:
            self._log.extend(r.log)
            if r.p_scored:
                self._log.append(f"GOAL! {self.engine.player.name} scores!")
                self._flash(C.GOAL)
            if r.o_scored:
                self._log.append(f"GOAL! {self.opp_def.name} scores!")
                self._flash(C.CONCEDE)
            if not r.p_scored and not r.o_scored:
                self._flash(C.NEUTRAL)
        self._rebuild_played_widgets()

    def _flash(self, col: tuple) -> None:
        self._flash_col = col
        self._flash_ticks = 30

    def _go_to_result(self):
        from graphics.screens.result import MatchResultScreen
        return MatchResultScreen(self.app, self.campaign, self.engine)

    # ── Widget builders ───────────────────────────────────────────────────────

    def _rebuild_hand(self) -> None:
        hand = self.engine.player.hand
        x0 = card_row_x(len(hand))
        # Pin to bottom of zone leaving 18px label gap at top
        y = HAND_Y + HAND_H - CARD_H - 4
        self._hand_widgets = []
        for i, card in enumerate(hand):
            w = CardWidget(card, x0 + i * (CARD_W + CARD_GAP), y,
                           face_up=True, clickable=True)
            w.disabled = not self.engine.player.can_play(card)
            self._hand_widgets.append(w)

    def _rebuild_played_widgets(self) -> None:
        y_p = PLY_Y + PLY_H - CARD_H - 4
        self._p_played_widgets = build_card_row(
            self.engine.p_played, y_p, face_up=True, clickable=False)

        y_o = OPP_Y + OPP_H - CARD_H - 4
        face_up = self.engine.phase != Phase.PLAYER_SELECTING
        self._o_played_widgets = build_card_row(
            self.engine.o_played, y_o, face_up=face_up, clickable=False)

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, mouse_pos: tuple[int, int]) -> None:
        phase = self.engine.phase
        is_selecting = phase == Phase.PLAYER_SELECTING

        for w in self._hand_widgets:
            if is_selecting:
                w.disabled = not self.engine.player.can_play(w.card)
                w.clickable = True
            else:
                w.clickable = False
            w.update(mouse_pos)

        for w in self._p_played_widgets + self._o_played_widgets:
            w.update(mouse_pos)

        if is_selecting:
            self._end_turn_btn.update(mouse_pos)
        else:
            self._continue_btn.update(mouse_pos)

        self._energy.current = self.engine.player.energy
        self._energy.max_e   = self.engine.player.max_energy

        if self._flash_ticks > 0:
            self._flash_ticks -= 1
        else:
            self._flash_col = None

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surf: pygame.Surface) -> None:
        surf.fill(C.BG)

        # Flash overlay
        if self._flash_col and self._flash_ticks > 0:
            alpha = int(120 * self._flash_ticks / 30)
            fsurf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            fsurf.fill((*self._flash_col, alpha))
            surf.blit(fsurf, (0, 0))

        self._draw_status_bar(surf)
        self._draw_area_labels(surf)
        self._draw_played(surf)
        self._draw_log(surf)
        self._draw_hand(surf)
        self._draw_action_bar(surf)

        # Half-time overlay
        if self.engine.phase == Phase.HALF_TIME:
            self._draw_halftime_overlay(surf)

        # Match-end overlay
        if self.engine.phase == Phase.MATCH_END:
            self._draw_match_end_overlay(surf)

    def _draw_status_bar(self, surf: pygame.Surface) -> None:
        pygame.draw.rect(surf, C.BG_PANEL, pygame.Rect(0, 0, SCREEN_W, STATUS_H))
        pygame.draw.line(surf, C.FIELD_LINE, (0, STATUS_H), (SCREEN_W, STATUS_H), 1)

        eng = self.engine
        half = 1 if eng.round_num <= eng.BASE_ROUNDS // 2 else 2

        # Score centre
        score_str = f"{eng.player.goals}  –  {eng.opponent.goals}"
        ss = fonts.get("score").render(score_str, True, C.TXT_GOLD)
        surf.blit(ss, (SCREEN_W // 2 - ss.get_width() // 2,
                        STATUS_H // 2 - ss.get_height() // 2))

        # Name tags
        pn = fonts.get("subhead").render(self.campaign.player_name, True, C.TXT_LIGHT)
        on = fonts.get("subhead").render(self.opp_def.team, True, C.TXT_LIGHT)
        surf.blit(pn, (SCREEN_W // 2 - ss.get_width() // 2 - pn.get_width() - 14,
                        STATUS_H // 2 - pn.get_height() // 2))
        surf.blit(on, (SCREEN_W // 2 + ss.get_width() // 2 + 14,
                        STATUS_H // 2 - on.get_height() // 2))

        # Round info — bottom of status bar, left-aligned, small font to avoid collision
        round_str = f"Round {eng.round_num}/{eng.max_rounds}  ·  {'1st' if half == 1 else '2nd'} Half"
        rs = fonts.get("small").render(round_str, True, C.TXT_GREY)
        surf.blit(rs, (14, STATUS_H - rs.get_height() - 4))

        # Phase label — bottom of status bar, right-aligned
        phase_labels = {
            Phase.PLAYER_SELECTING: "Your turn",
            Phase.RESOLUTION:       "Resolution",
            Phase.HALF_TIME:        "Half Time",
            Phase.MATCH_END:        "Full Time",
        }
        pl = fonts.get("small").render(phase_labels.get(self.engine.phase, ""), True, C.TXT_GREY)
        surf.blit(pl, (SCREEN_W - pl.get_width() - 14, STATUS_H - pl.get_height() - 4))

    def _draw_area_labels(self, surf: pygame.Surface) -> None:
        # Opponent area background
        pygame.draw.rect(surf, C.BG_STRIPE, pygame.Rect(0, OPP_Y, SCREEN_W, OPP_H))
        pygame.draw.line(surf, C.FIELD_LINE, (0, OPP_Y), (SCREEN_W, OPP_Y), 1)
        pygame.draw.line(surf, C.FIELD_LINE, (0, OPP_Y + OPP_H), (SCREEN_W, OPP_Y + OPP_H), 1)
        lbl = fonts.get("small").render(f"{self.opp_def.name}'s played cards", True, C.TXT_GREY)
        surf.blit(lbl, (10, OPP_Y + 5))

        # Player area background
        pygame.draw.rect(surf, C.BG_STRIPE, pygame.Rect(0, PLY_Y, SCREEN_W, PLY_H))
        pygame.draw.line(surf, C.FIELD_LINE, (0, PLY_Y), (SCREEN_W, PLY_Y), 1)
        pygame.draw.line(surf, C.FIELD_LINE, (0, PLY_Y + PLY_H), (SCREEN_W, PLY_Y + PLY_H), 1)
        lbl2 = fonts.get("small").render("Your played cards", True, C.TXT_GREY)
        surf.blit(lbl2, (10, PLY_Y + 5))

        # Hand area label
        pygame.draw.line(surf, C.FIELD_LINE, (0, HAND_Y), (SCREEN_W, HAND_Y), 1)
        lbl3 = fonts.get("small").render("Your hand", True, C.TXT_GREY)
        surf.blit(lbl3, (10, HAND_Y + 5))

    def _draw_played(self, surf: pygame.Surface) -> None:
        # Draw placeholder if no cards played
        if not self._o_played_widgets:
            msg = fonts.get("small").render("No cards played yet", True, C.TXT_GREY)
            surf.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2,
                             OPP_Y + OPP_H // 2 - msg.get_height() // 2))
        else:
            for w in self._o_played_widgets:
                w.draw(surf)

        if not self._p_played_widgets:
            msg = fonts.get("small").render("No cards played yet", True, C.TXT_GREY)
            surf.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2,
                             PLY_Y + PLY_H // 2 - msg.get_height() // 2))
        else:
            for w in self._p_played_widgets:
                w.draw(surf)

    def _draw_log(self, surf: pygame.Surface) -> None:
        pygame.draw.rect(surf, C.BG_PANEL, pygame.Rect(0, LOG_Y, SCREEN_W, LOG_H))
        pygame.draw.line(surf, C.FIELD_LINE, (0, LOG_Y), (SCREEN_W, LOG_Y), 1)

        # Show resolution totals if in RESOLUTION phase
        r = self.engine.result
        if r and self.engine.phase == Phase.RESOLUTION:
            eng = self.engine
            col_p = C.TXT_GREEN if r.p_scored else C.TXT_RED
            col_o = C.TXT_RED if r.o_scored else C.TXT_GREEN

            line1 = (f"You: ATK {r.p_attack} vs DEF {r.o_defense} → "
                     + ("GOAL!" if r.p_scored else "Saved"))
            line2 = (f"{self.opp_def.name}: ATK {r.o_attack} vs DEF {r.p_defense} → "
                     + ("GOAL!" if r.o_scored else "Saved"))
            if r.offside_nullified:
                line2 += "  (Offside!)"

            s1 = fonts.get("log").render(line1, True, col_p)
            s2 = fonts.get("log").render(line2, True, col_o)
            surf.blit(s1, (14, LOG_Y + 8))
            surf.blit(s2, (14, LOG_Y + 8 + s1.get_height() + 4))

            # Remaining log lines below
            y = LOG_Y + 8 + s1.get_height() + 4 + s2.get_height() + 6
            for line in self._log[-2:]:
                ls = fonts.get("small").render(line, True, C.TXT_GREY)
                surf.blit(ls, (14, y))
                y += ls.get_height() + 2
        else:
            y = LOG_Y + 8
            for line in self._log[-_LOG_MAX:]:
                ls = fonts.get("log").render(line, True, C.TXT_GREY)
                surf.blit(ls, (14, y))
                y += ls.get_height() + 3

    def _draw_hand(self, surf: pygame.Surface) -> None:
        if not self._hand_widgets:
            msg = fonts.get("small").render("No cards in hand", True, C.TXT_GREY)
            surf.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2,
                             HAND_Y + HAND_H // 2 - msg.get_height() // 2))
        else:
            for w in self._hand_widgets:
                w.draw(surf)

    def _draw_action_bar(self, surf: pygame.Surface) -> None:
        pygame.draw.rect(surf, C.BG_PANEL, pygame.Rect(0, ACTION_Y, SCREEN_W, ACTION_H))
        pygame.draw.line(surf, C.FIELD_LINE, (0, ACTION_Y), (SCREEN_W, ACTION_Y), 1)

        phase = self.engine.phase
        row1_y = ACTION_Y + 18   # top row baseline
        row2_y = ACTION_Y + 62   # bottom row baseline
        btn_w, btn_h = 200, 46
        btn_x = SCREEN_W - btn_w - 20
        btn_y = ACTION_Y + (ACTION_H - btn_h) // 2

        if phase == Phase.PLAYER_SELECTING:
            # ── Row 1: energy dots + energy text ────────────────────────────
            self._energy.x  = 20
            self._energy.y  = row1_y + self._energy.R
            self._energy.current = self.engine.player.energy
            self._energy.max_e   = self.engine.player.max_energy
            self._energy.draw(surf)

            en_col = C.TXT_GOLD if self.engine.player.energy > self.engine.player.max_energy else C.TXT_GREY
            en_lbl = fonts.get("small").render(
                f"Energy  {self.engine.player.energy}/{self.engine.player.max_energy}",
                True, en_col)
            surf.blit(en_lbl, (20 + self._energy.max_e * self._energy.GAP + 12, row1_y))

            # ── Row 1: deck count (right-aligned before button) ─────────────
            deck_txt = (f"Deck: {self.engine.player.deck.size()}"
                        f"   Discard: {len(self.engine.player.deck.discard_pile)}")
            ds = fonts.get("small").render(deck_txt, True, C.TXT_GREY)
            surf.blit(ds, (btn_x - ds.get_width() - 20, row1_y))

            # ── Row 2: squad passive stats ───────────────────────────────────
            sq = self.engine.player_squad
            if sq:
                sq_str = (f"Squad  ATK +{sq.base_attack}  DEF +{sq.base_defense}  (passive)"
                          f"   {sq.attacker.name} · {sq.midfielder.name}"
                          f" · {sq.defender.name} · {sq.gk.name}")
                sq_s = fonts.get("small").render(sq_str, True, C.TXT_GOLD)
                surf.blit(sq_s, (20, row2_y))

            self._end_turn_btn.rect.topleft = (btn_x, btn_y)
            self._end_turn_btn.draw(surf)
        else:
            phase_msg = {
                Phase.RESOLUTION: "Review the result, then click Continue",
                Phase.HALF_TIME:  "Half Time — click Continue for the second half",
                Phase.MATCH_END:  "Full Time — click Continue",
            }.get(phase, "")
            if phase_msg:
                pm = fonts.get("small").render(phase_msg, True, C.TXT_GREY)
                surf.blit(pm, (20, ACTION_Y + (ACTION_H - pm.get_height()) // 2))
            self._continue_btn.rect.topleft = (btn_x, btn_y)
            self._continue_btn.draw(surf)

    def _draw_halftime_overlay(self, surf: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))

        eng = self.engine
        cx, cy = SCREEN_W // 2, SCREEN_H // 2
        box = pygame.Rect(cx - 220, cy - 120, 440, 240)
        pygame.draw.rect(surf, C.BG_PANEL, box, border_radius=12)
        pygame.draw.rect(surf, C.TXT_GOLD, box, 2, border_radius=12)

        draw_text(surf, "HALF TIME", "heading", C.TXT_GOLD,
                  pygame.Rect(box.x, box.y + 20, box.w, 40), align="center")
        score = f"{eng.player.goals}  –  {eng.opponent.goals}"
        draw_text(surf, score, "score", C.TXT_LIGHT,
                  pygame.Rect(box.x, box.y + 80, box.w, 60), align="center")
        draw_text(surf, "Click Continue to start the second half",
                  "small", C.TXT_GREY,
                  pygame.Rect(box.x, box.y + 160, box.w, 30), align="center")

    def _draw_match_end_overlay(self, surf: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))
        draw_text(surf, "FULL TIME  —  Click Continue",
                  "subhead", C.TXT_GOLD,
                  pygame.Rect(0, SCREEN_H // 2 - 20, SCREEN_W, 40), align="center")
