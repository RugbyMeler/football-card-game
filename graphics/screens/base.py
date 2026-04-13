"""Abstract base class for all screens."""
from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphics.app import App


class Screen:
    def __init__(self, app: "App"):
        self.app = app

    def handle_event(self, event: pygame.event.Event):
        """Return a Screen to transition to, 'quit' to exit, or None."""
        return None

    def update(self, mouse_pos: tuple[int, int]) -> None:
        pass

    def draw(self, surf: pygame.Surface) -> None:
        pass
