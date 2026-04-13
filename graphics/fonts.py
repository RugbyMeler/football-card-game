"""Centralised font cache.  Call init() once after pygame.init()."""
import pygame

_f: dict = {}


def init() -> None:
    def sf(name: str, size: int, bold: bool = False) -> pygame.font.Font:
        # Prefer Segoe UI on Windows; fall back to any available sans-serif
        for family in ("segoeui", "calibri", "arial", None):
            try:
                return pygame.font.SysFont(family, size, bold=bold)
            except Exception:
                pass
        return pygame.font.Font(None, size)

    _f.update({
        "title":      sf("segoeui", 48, bold=True),
        "heading":    sf("segoeui", 28, bold=True),
        "subhead":    sf("segoeui", 20, bold=True),
        "body":       sf("segoeui", 17),
        "small":      sf("segoeui", 13),
        "cost":       sf("segoeui", 15, bold=True),
        "card_name":  sf("segoeui", 12, bold=True),
        "card_desc":  sf("segoeui", 10),
        "card_pwr":   sf("segoeui", 24, bold=True),
        "button":     sf("segoeui", 18, bold=True),
        "score":      sf("segoeui", 34, bold=True),
        "ui":         sf("segoeui", 17),
        "log":        sf("segoeui", 14),
    })


def get(name: str) -> pygame.font.Font:
    return _f.get(name, _f.get("body"))
