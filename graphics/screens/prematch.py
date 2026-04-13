"""Pre-match briefing screen shown before each fixture."""
from __future__ import annotations
import pygame
from graphics.screens.base import Screen
from graphics.constants import C, SCREEN_W, SCREEN_H
from graphics.widgets import Button, draw_text, blit_wrapped
from graphics import fonts
from game.campaign import Campaign
from data.opponents import OPPONENT_ROSTER
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphics.app import App


class PreMatchScreen(Screen):
    def __init__(self, app: "App", campaign: Campaign):
        super().__init__(app)
        self.campaign    = campaign
        self._view_open  = False
        self._deck_scroll = 0

        cx = SCREEN_W // 2
        self._kick_off   = Button("Kick Off!",      cx - 130, 520, 260, 52)
        self._squad_btn  = Button("Manage Squad",   cx - 130, 584, 260, 46, style="grey")
        self._view_btn   = Button("View Deck",      cx - 130, 642, 260, 46, style="grey")

    def handle_event(self, event: pygame.event.Event):
        if self._view_open:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._view_open = False
                elif event.button == 4:
                    self._deck_scroll = max(0, self._deck_scroll - 1)
                elif event.button == 5:
                    self._deck_scroll += 1
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._kick_off.clicked(event.pos):
                return self._start_match()
            if self._squad_btn.clicked(event.pos):
                from graphics.screens.squad import SquadScreen
                return SquadScreen(self.app, self.campaign, return_screen=self)
            if self._view_btn.clicked(event.pos):
                self._view_open = True
        return None

    def _start_match(self):
        from graphics.screens.match import MatchScreen
        from graphics.screens.complete import CampaignCompleteScreen
        if self.campaign.opponent_index >= len(OPPONENT_ROSTER):
            return CampaignCompleteScreen(self.app, self.campaign)
        return MatchScreen(self.app, self.campaign)

    def update(self, mouse_pos):
        if not self._view_open:
            self._kick_off.update(mouse_pos)
            self._squad_btn.update(mouse_pos)
            self._view_btn.update(mouse_pos)

    def draw(self, surf: pygame.Surface):
        surf.fill(C.BG)

        if self._view_open:
            self._draw_deck_overlay(surf)
            return

        idx = self.campaign.opponent_index
        if idx >= len(OPPONENT_ROSTER):
            draw_text(surf, "All opponents defeated!", "heading", C.TXT_GOLD,
                      pygame.Rect(0, 300, SCREEN_W, 50), align="center")
            self._kick_off.draw(surf)
            return

        opp = OPPONENT_ROSTER[idx]
        squad = self.campaign.squad
        cx = SCREEN_W // 2

        # Header
        pygame.draw.rect(surf, C.BG_PANEL, pygame.Rect(0, 0, SCREEN_W, 80))
        draw_text(surf, "NEXT MATCH", "heading", C.TXT_GOLD,
                  pygame.Rect(0, 20, SCREEN_W, 40), align="center")

        # Opponent info box
        box = pygame.Rect(cx - 280, 100, 560, 340)
        pygame.draw.rect(surf, C.BG_PANEL, box, border_radius=10)
        pygame.draw.rect(surf, C.FIELD_LINE, box, 2, border_radius=10)

        y = 118
        ts = fonts.get("heading").render(opp.team, True, C.TXT_LIGHT)
        surf.blit(ts, (cx - ts.get_width() // 2, y));  y += ts.get_height() + 6

        mgr = fonts.get("body").render(f"Manager: {opp.name}", True, C.TXT_GREY)
        surf.blit(mgr, (cx - mgr.get_width() // 2, y));  y += mgr.get_height() + 8

        diff = fonts.get("subhead").render("Difficulty: " + "★" * opp.difficulty, True, C.TXT_GOLD)
        surf.blit(diff, (cx - diff.get_width() // 2, y));  y += diff.get_height() + 14

        pygame.draw.line(surf, C.FIELD_LINE, (cx - 220, y), (cx + 220, y), 1);  y += 14
        blit_wrapped(surf, f'"{opp.description}"', "body", C.TXT_GREY,
                     box.x + 28, y, box.w - 56, max_lines=3)

        # Your squad summary (below box)
        sq_y = box.bottom + 14
        summary = (f"Squad: GK {squad.gk.name}  |  DEF {squad.defender.name}  |  "
                   f"MID {squad.midfielder.name}  |  ATT {squad.attacker.name}")
        ss = fonts.get("small").render(summary, True, C.TXT_GREY)
        surf.blit(ss, (cx - ss.get_width() // 2, sq_y))

        base_str = (f"Base ATK {squad.base_attack}  |  Base DEF {squad.base_defense}  "
                    f"(passive each round)")
        bs = fonts.get("small").render(base_str, True, C.TXT_GOLD)
        surf.blit(bs, (cx - bs.get_width() // 2, sq_y + 20))

        rec = fonts.get("body").render(
            f"Record: {self.campaign.wins}W / {self.campaign.losses}L",
            True, C.TXT_GREY)
        surf.blit(rec, (cx - rec.get_width() // 2, sq_y + 46))

        self._kick_off.draw(surf)
        self._squad_btn.draw(surf)
        self._view_btn.draw(surf)

    def _draw_deck_overlay(self, surf: pygame.Surface):
        from data.cards import CARD_BY_ID
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))

        panel = pygame.Rect(SCREEN_W // 2 - 300, 60, 600, SCREEN_H - 120)
        pygame.draw.rect(surf, C.BG_PANEL, panel, border_radius=10)
        pygame.draw.rect(surf, C.FIELD_LINE, panel, 2, border_radius=10)

        draw_text(surf, "Your Deck", "heading", C.TXT_GOLD,
                  pygame.Rect(panel.x, panel.y + 14, panel.w, 36), align="center")

        y = panel.y + 62
        for cid in self.campaign.deck_ids[self._deck_scroll:]:
            if y + 22 > panel.bottom - 40:
                break
            card = CARD_BY_ID[cid]
            ts = fonts.get("body").render(f"  {card.name}", True, C.TXT_LIGHT)
            surf.blit(ts, (panel.x + 20, y))
            y += ts.get_height() + 4

        close = fonts.get("small").render("Click anywhere to close", True, C.TXT_GREY)
        surf.blit(close, (panel.x + (panel.w - close.get_width()) // 2, panel.bottom - 30))
