"""Campaign complete / victory screen."""
from __future__ import annotations
import pygame
from graphics.screens.base import Screen
from graphics.constants import C, SCREEN_W, SCREEN_H
from graphics.widgets import Button, draw_text
from graphics import fonts
from game.campaign import Campaign, delete_save
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphics.app import App


class CampaignCompleteScreen(Screen):
    def __init__(self, app: "App", campaign: Campaign):
        super().__init__(app)
        self.campaign = campaign
        delete_save()

        cx = SCREEN_W // 2
        self._menu_btn = Button("Return to Menu", cx - 120, 540, 240, 52)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._menu_btn.clicked(event.pos):
                from graphics.screens.menu import MainMenuScreen
                return MainMenuScreen(self.app)
        return None

    def update(self, mouse_pos):
        self._menu_btn.update(mouse_pos)

    def draw(self, surf: pygame.Surface):
        surf.fill(C.BG)
        for y in range(0, SCREEN_H, 80):
            pygame.draw.line(surf, C.FIELD_LINE, (0, y), (SCREEN_W, y), 1)

        cx = SCREEN_W // 2

        banner = pygame.Rect(cx - 300, 140, 600, 100)
        pygame.draw.rect(surf, C.GOAL, banner, border_radius=12)
        draw_text(surf, "SEASON COMPLETE!", "heading", C.TXT_LIGHT,
                  banner, align="center", valign="center")

        draw_text(surf, "You've beaten every team in the league.",
                  "subhead", C.TXT_GOLD,
                  pygame.Rect(0, 280, SCREEN_W, 40), align="center")

        rec = fonts.get("body").render(
            f"Final record: {self.campaign.wins}W / {self.campaign.losses}L",
            True, C.TXT_GREY)
        surf.blit(rec, (cx - rec.get_width() // 2, 340))

        deck = fonts.get("body").render(
            f"Cards in deck: {len(self.campaign.deck_ids)}",
            True, C.TXT_GREY)
        surf.blit(deck, (cx - deck.get_width() // 2, 380))

        draw_text(surf, "Champions!", "score", C.TXT_GOLD,
                  pygame.Rect(0, 430, SCREEN_W, 60), align="center")

        self._menu_btn.draw(surf)
