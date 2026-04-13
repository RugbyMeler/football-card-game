"""Squad management screen — swap starters and bench players before a match."""
from __future__ import annotations
import pygame
from graphics.screens.base import Screen
from graphics.constants import C, SCREEN_W, SCREEN_H
from graphics.widgets import Button, draw_text, blit_wrapped
from graphics import fonts
from game.squad import Position, Squad, FootballPlayer
from game.campaign import Campaign
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphics.app import App

_POSITIONS = [Position.GK, Position.DEF, Position.MID, Position.ATT]
_POS_LABELS = {Position.GK: "GK", Position.DEF: "DEF",
               Position.MID: "MID", Position.ATT: "ATT"}
_POS_COLORS = {
    Position.GK:  ( 40, 100, 160),
    Position.DEF: ( 40, 140,  40),
    Position.MID: (150, 120,  30),
    Position.ATT: (160,  40,  40),
}
_RARITY_COL = {"Common": C.COMMON, "Uncommon": C.UNCOMMON, "Rare": C.RARE}

# Layout
_CARD_W, _CARD_H = 240, 130
_CARD_GAP = 14


class SquadScreen(Screen):
    """
    Shows the four starting positions and the bench.
    Click a starter card, then click a bench card to swap them.
    """

    def __init__(self, app: "App", campaign: Campaign, return_screen):
        super().__init__(app)
        self.campaign = campaign
        self.return_screen = return_screen   # screen to go back to
        self._selected_pos: Position | None = None
        self._hovered_pos:  Position | None = None
        self._hovered_bench: int | None = None

        bw = 180
        self._done_btn = Button("Done  ✓", SCREEN_W - bw - 20, SCREEN_H - 66, bw, 46)

    # ── Event handling ────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self._done_btn.clicked(pos):
                return self.return_screen

            # Check starter card clicks
            for i, position in enumerate(_POSITIONS):
                r = self._starter_rect(i)
                if r.collidepoint(pos):
                    if self._selected_pos == position:
                        self._selected_pos = None   # deselect
                    else:
                        self._selected_pos = position
                    return None

            # Check bench card clicks
            squad = self.campaign.squad
            for bi, player in enumerate(squad.bench):
                r = self._bench_rect(bi)
                if r.collidepoint(pos):
                    if self._selected_pos is not None:
                        squad.swap_with_bench(self._selected_pos, bi)
                        self._selected_pos = None
                    return None

        return None

    def update(self, mouse_pos):
        self._done_btn.update(mouse_pos)
        self._hovered_pos   = None
        self._hovered_bench = None
        for i, position in enumerate(_POSITIONS):
            if self._starter_rect(i).collidepoint(mouse_pos):
                self._hovered_pos = position
        for bi in range(len(self.campaign.squad.bench)):
            if self._bench_rect(bi).collidepoint(mouse_pos):
                self._hovered_bench = bi

    def draw(self, surf: pygame.Surface):
        surf.fill(C.BG)
        for y in range(0, SCREEN_H, 80):
            pygame.draw.line(surf, C.FIELD_LINE, (0, y), (SCREEN_W, y), 1)

        # Header
        pygame.draw.rect(surf, C.BG_PANEL, pygame.Rect(0, 0, SCREEN_W, 55))
        draw_text(surf, "SQUAD MANAGEMENT", "heading", C.TXT_GOLD,
                  pygame.Rect(0, 10, SCREEN_W, 40), align="center")

        self._draw_starters(surf)
        self._draw_bench(surf)
        self._draw_instructions(surf)
        self._done_btn.draw(surf)

    # ── Draw helpers ──────────────────────────────────────────────────────────

    def _draw_starters(self, surf: pygame.Surface):
        squad = self.campaign.squad
        draw_text(surf, "STARTING XI  (select to swap with bench)",
                  "small", C.TXT_GREY, pygame.Rect(20, 60, 600, 22))

        for i, position in enumerate(_POSITIONS):
            player  = squad.get_starter(position)
            r       = self._starter_rect(i)
            selected = (self._selected_pos == position)
            hovered  = (self._hovered_pos  == position)
            self._draw_player_card(surf, player, r, position,
                                    selected=selected, hovered=hovered)

    def _draw_bench(self, surf: pygame.Surface):
        squad = self.campaign.squad
        draw_text(surf, "BENCH", "small", C.TXT_GREY,
                  pygame.Rect(20, 360, 200, 22))

        if not squad.bench:
            msg = fonts.get("body").render("No bench players yet — earn them through wins.",
                                            True, C.TXT_GREY)
            surf.blit(msg, (20, 390))
            return

        for bi, player in enumerate(squad.bench):
            r        = self._bench_rect(bi)
            hovered  = (self._hovered_bench == bi)
            selectable = self._selected_pos is not None
            self._draw_player_card(surf, player, r, player.position,
                                    hovered=hovered, selectable=selectable)

    def _draw_player_card(self, surf: pygame.Surface, player: FootballPlayer,
                           rect: pygame.Rect, position: Position,
                           selected: bool = False, hovered: bool = False,
                           selectable: bool = True):
        # Background
        draw_r = rect.move(0, -6 if hovered else 0)
        pos_col = _POS_COLORS.get(position, C.BG_PANEL)
        bg = tuple(min(255, c + 20) for c in pos_col) if hovered else pos_col
        pygame.draw.rect(surf, bg, draw_r, border_radius=8)

        # Border
        border_col = C.CARD_BORDER_SEL if selected else (
            C.CARD_BORDER_HOV if hovered else C.FIELD_LINE)
        border_w = 3 if selected else (2 if hovered else 1)
        pygame.draw.rect(surf, border_col, draw_r, border_w, border_radius=8)

        # Position badge
        badge_r = pygame.Rect(draw_r.x + 8, draw_r.y + 8, 44, 22)
        pygame.draw.rect(surf, (0, 0, 0, 120), badge_r, border_radius=4)
        draw_text(surf, _POS_LABELS[position], "small", C.TXT_GOLD, badge_r,
                  align="center", valign="center")

        # Player name
        ns = fonts.get("subhead").render(player.name, True, C.TXT_LIGHT)
        surf.blit(ns, (draw_r.x + 60, draw_r.y + 10))

        # Stats
        stat_str = f"ATK {player.att_power}   DEF {player.def_power}"
        ss = fonts.get("body").render(stat_str, True, C.TXT_GOLD)
        surf.blit(ss, (draw_r.x + 60, draw_r.y + 36))

        # Rarity dot
        rc = _RARITY_COL.get(player.rarity.value, C.COMMON)
        pygame.draw.circle(surf, rc, (draw_r.right - 14, draw_r.y + 14), 6)

        # Description
        blit_wrapped(surf, player.description, "small", C.TXT_GREY,
                     draw_r.x + 8, draw_r.y + 62, draw_r.w - 16, max_lines=2)

        # Selection cue
        if selected:
            sel_s = fonts.get("small").render("▶ Select bench player to swap",
                                               True, C.TXT_GOLD)
            surf.blit(sel_s, (draw_r.x + 8, draw_r.y + draw_r.h - 20))

    def _draw_instructions(self, surf: pygame.Surface):
        lines = [
            "ATK — passive attack bonus each round (ATT + MID att_power)",
            "DEF — scales defense cards like Man Marking, Sweeper Keeper, Park the Bus",
            "GK DEF stat is passive defense bonus each round",
        ]
        y = SCREEN_H - 100
        for line in lines:
            s = fonts.get("small").render(line, True, C.TXT_GREY)
            surf.blit(s, (20, y))
            y += s.get_height() + 2

    # ── Rect helpers ──────────────────────────────────────────────────────────

    def _starter_rect(self, index: int) -> pygame.Rect:
        """Four starter cards in a row near the top."""
        total_w = 4 * _CARD_W + 3 * _CARD_GAP
        x0 = (SCREEN_W - total_w) // 2
        return pygame.Rect(x0 + index * (_CARD_W + _CARD_GAP), 88, _CARD_W, _CARD_H)

    def _bench_rect(self, index: int) -> pygame.Rect:
        """Bench cards in a row below starters."""
        total_visible = min(5, len(self.campaign.squad.bench))
        total_w = total_visible * _CARD_W + max(0, total_visible - 1) * _CARD_GAP
        x0 = (SCREEN_W - total_w) // 2
        row = index // 5
        col = index  % 5
        return pygame.Rect(x0 + col * (_CARD_W + _CARD_GAP),
                            382 + row * (_CARD_H + _CARD_GAP),
                            _CARD_W, _CARD_H)
