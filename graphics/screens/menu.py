"""Main menu and name-entry screens."""
from __future__ import annotations
import pygame
from graphics.screens.base import Screen
from graphics.constants import C, SCREEN_W, SCREEN_H
from graphics.widgets import Button, draw_text
from graphics import fonts
from game.campaign import Campaign, load_campaign, delete_save
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphics.app import App


class MainMenuScreen(Screen):
    def __init__(self, app: "App"):
        super().__init__(app)
        cx = SCREEN_W // 2
        bw, bh = 260, 52
        self._btns = {
            "new":  Button("New Campaign",  cx - bw // 2, 340, bw, bh),
            "load": Button("Load Campaign", cx - bw // 2, 410, bw, bh),
            "quit": Button("Quit",          cx - bw // 2, 480, bw, bh, style="danger"),
        }
        save = load_campaign()
        self._btns["load"].enabled = save is not None
        self._title_surf = fonts.get("title").render("FOOTBALL CARD GAME", True, C.TXT_GOLD)
        self._sub_surf   = fonts.get("subhead").render(
            "Build your deck.  Outscore the opposition.", True, C.TXT_GREY)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self._btns["new"].clicked(pos):
                return NameEntryScreen(self.app)
            if self._btns["load"].clicked(pos):
                data = load_campaign()
                if data:
                    from graphics.screens.prematch import PreMatchScreen
                    campaign = Campaign.from_save(data)
                    return PreMatchScreen(self.app, campaign)
            if self._btns["quit"].clicked(pos):
                return "quit"
        return None

    def update(self, mouse_pos):
        for btn in self._btns.values():
            btn.update(mouse_pos)

    def draw(self, surf: pygame.Surface):
        surf.fill(C.BG)
        # Decorative field lines
        for y in range(0, SCREEN_H, 80):
            pygame.draw.line(surf, C.FIELD_LINE, (0, y), (SCREEN_W, y), 1)

        cx = SCREEN_W // 2
        surf.blit(self._title_surf, (cx - self._title_surf.get_width() // 2, 200))
        surf.blit(self._sub_surf,   (cx - self._sub_surf.get_width()  // 2, 270))

        for btn in self._btns.values():
            btn.draw(surf)


class NameEntryScreen(Screen):
    MAX_LEN = 20

    def __init__(self, app: "App"):
        super().__init__(app)
        self._name = ""
        self._cursor_vis = True
        self._cursor_tick = 0
        cx = SCREEN_W // 2
        self._confirm = Button("Start Campaign", cx - 130, 460, 260, 52)
        self._back    = Button("Back",           cx - 130, 528, 260, 52, style="grey")

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self._name = self._name[:-1]
            elif event.key == pygame.K_RETURN:
                return self._start()
            elif event.key == pygame.K_ESCAPE:
                return MainMenuScreen(self.app)
            elif len(self._name) < self.MAX_LEN and event.unicode.isprintable():
                self._name += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._confirm.clicked(event.pos):
                return self._start()
            if self._back.clicked(event.pos):
                return MainMenuScreen(self.app)
        return None

    def _start(self):
        name = self._name.strip() or "The Gaffer"
        delete_save()
        from graphics.screens.prematch import PreMatchScreen
        campaign = Campaign.new(name)
        return PreMatchScreen(self.app, campaign)

    def update(self, mouse_pos):
        self._cursor_tick += 1
        if self._cursor_tick >= 30:
            self._cursor_vis = not self._cursor_vis
            self._cursor_tick = 0
        self._confirm.update(mouse_pos)
        self._back.update(mouse_pos)

    def draw(self, surf: pygame.Surface):
        surf.fill(C.BG)
        cx = SCREEN_W // 2

        draw_text(surf, "Enter Your Manager Name", "heading", C.TXT_GOLD,
                  pygame.Rect(0, 220, SCREEN_W, 40), align="center")

        # Input box
        box = pygame.Rect(cx - 200, 310, 400, 52)
        pygame.draw.rect(surf, C.BG_PANEL, box, border_radius=8)
        pygame.draw.rect(surf, C.BTN_BORDER, box, 2, border_radius=8)
        display = self._name + ("|" if self._cursor_vis else " ")
        ts = fonts.get("heading").render(display, True, C.TXT_LIGHT)
        surf.blit(ts, (box.x + 14, box.y + (box.h - ts.get_height()) // 2))

        self._confirm.draw(surf)
        self._back.draw(surf)
