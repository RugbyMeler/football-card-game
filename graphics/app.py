"""Main pygame application loop."""
from __future__ import annotations
import sys
import asyncio
import pygame
from graphics.constants import SCREEN_W, SCREEN_H, FPS, TITLE
from graphics import fonts
from graphics.screens.base import Screen

# In a browser (pygbag/emscripten) fullscreen isn't available.
_IS_WEB = sys.platform == "emscripten"


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        flags = pygame.SCALED if _IS_WEB else (pygame.FULLSCREEN | pygame.SCALED)
        self._surf = pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)
        self._clock = pygame.time.Clock()
        fonts.init()

        from graphics.screens.menu import MainMenuScreen
        self._screen: Screen = MainMenuScreen(self)

    async def run(self) -> None:
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                result = self._screen.handle_event(event)
                if result == "quit":
                    running = False
                    break
                elif isinstance(result, Screen):
                    self._screen = result

            if not running:
                break

            self._screen.update(mouse_pos)
            self._screen.draw(self._surf)
            pygame.display.flip()
            self._clock.tick(FPS)
            await asyncio.sleep(0)  # yield to browser / event loop each frame

        pygame.quit()
