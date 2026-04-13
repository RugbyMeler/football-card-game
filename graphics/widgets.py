"""Reusable UI widgets: CardWidget, Button, EnergyBar, helpers."""
from __future__ import annotations
import pygame
from graphics.constants import C, CARD_W, CARD_H, CARD_GAP
from graphics import fonts
from game.card import CardType, Rarity


# ── Text helpers ─────────────────────────────────────────────────────────────

def draw_text(surf: pygame.Surface, text: str, font_name: str,
              color, rect: pygame.Rect,
              align: str = "left", valign: str = "top") -> None:
    f = fonts.get(font_name)
    s = f.render(text, True, color)
    w, h = s.get_size()
    x = (rect.x + (rect.w - w) // 2 if align == "center"
         else rect.right - w if align == "right" else rect.x)
    y = (rect.y + (rect.h - h) // 2 if valign == "center"
         else rect.bottom - h if valign == "bottom" else rect.y)
    surf.blit(s, (x, y))


def wrap_text(text: str, font_name: str, max_w: int) -> list[str]:
    f = fonts.get(font_name)
    words = text.split()
    lines: list[str] = []
    cur: list[str] = []
    for w in words:
        test = " ".join(cur + [w])
        if f.size(test)[0] <= max_w:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def blit_wrapped(surf: pygame.Surface, text: str, font_name: str,
                 color, x: int, y: int, max_w: int,
                 max_lines: int = 99, line_gap: int = 2) -> int:
    """Draw wrapped text; returns the y coordinate after the last line."""
    f = fonts.get(font_name)
    for line in wrap_text(text, font_name, max_w)[:max_lines]:
        surf.blit(f.render(line, True, color), (x, y))
        y += f.get_height() + line_gap
    return y


# ── Card widget ───────────────────────────────────────────────────────────────

_TYPE_COLOR   = {CardType.ATTACK: C.ATK, CardType.DEFENSE: C.DEF, CardType.SPECIAL: C.SPC}
_RARITY_COLOR = {Rarity.COMMON: C.COMMON, Rarity.UNCOMMON: C.UNCOMMON, Rarity.RARE: C.RARE}
_STRIPE_H = 12


class CardWidget:
    """Renders a single Card; tracks hover/selected/disabled state."""

    def __init__(self, card, x: int, y: int,
                 face_up: bool = True, clickable: bool = True):
        self.card = card
        self.rect = pygame.Rect(x, y, CARD_W, CARD_H)
        self.face_up   = face_up
        self.clickable = clickable
        self.hovered   = False
        self.selected  = False
        self.disabled  = False   # not enough energy

    def update(self, mouse_pos: tuple[int, int]) -> None:
        self.hovered = self.rect.collidepoint(mouse_pos) if self.clickable else False

    def draw(self, surf: pygame.Surface) -> None:
        draw_r = self.rect.move(0, -14 if (self.hovered and not self.disabled) else 0)

        if not self.face_up:
            self._draw_back(surf, draw_r)
            return

        bg = (C.CARD_BG_DISABLED if self.disabled
              else C.CARD_BG_HOVER if self.hovered else C.CARD_BG)
        pygame.draw.rect(surf, bg, draw_r, border_radius=6)

        border_c = (C.CARD_BORDER_SEL if self.selected
                    else C.CARD_BORDER_HOV if self.hovered else C.CARD_BORDER)
        border_w = 3 if (self.selected or self.hovered) else 1
        pygame.draw.rect(surf, border_c, draw_r, border_w, border_radius=6)

        # Type stripe
        stripe = pygame.Rect(draw_r.x + 2, draw_r.y + 2, draw_r.w - 4, _STRIPE_H)
        pygame.draw.rect(surf, _TYPE_COLOR.get(self.card.card_type, C.TXT_GREY),
                         stripe, border_radius=4)

        # Cost circle
        cx, cy = draw_r.x + 14, draw_r.y + 2 + _STRIPE_H + 11
        pygame.draw.circle(surf, C.EN_FULL, (cx, cy), 11)
        pygame.draw.circle(surf, C.TXT_DARK, (cx, cy), 11, 1)
        f_cost = fonts.get("cost")
        cs = f_cost.render(str(self.card.cost), True, C.TXT_DARK)
        surf.blit(cs, (cx - cs.get_width() // 2, cy - cs.get_height() // 2))

        # Card name
        nr = pygame.Rect(draw_r.x + 4, draw_r.y + _STRIPE_H + 26, draw_r.w - 8, 36)
        y = nr.y
        for line in wrap_text(self.card.name, "card_name", nr.w)[:2]:
            s = fonts.get("card_name").render(line, True, C.TXT_DARK)
            surf.blit(s, (nr.x + (nr.w - s.get_width()) // 2, y))
            y += fonts.get("card_name").get_height() + 1

        # Description
        txt_c = C.TXT_GREY if self.disabled else (80, 70, 55)
        blit_wrapped(surf, self.card.description, "card_desc", txt_c,
                     draw_r.x + 5, draw_r.y + 70, draw_r.w - 10, max_lines=3)

        # Power value + stat label (ATT / DEF)
        if self.card.power > 0 or self.card._power_bonus > 0:
            pwr = self.card.effective_power()
            pwr_str = f"+{pwr}" if self.card._power_bonus > 0 else str(pwr)
            pwr_c = C.TXT_GREEN if self.card._power_bonus > 0 else C.TXT_DARK
            ps = fonts.get("card_pwr").render(pwr_str, True, pwr_c)
            px = draw_r.x + (draw_r.w - ps.get_width()) // 2
            py = draw_r.bottom - ps.get_height() - 5
            surf.blit(ps, (px, py))

            stat_label = {
                CardType.ATTACK:  "ATT",
                CardType.DEFENSE: "DEF",
                CardType.SPECIAL: "SPC",
            }.get(self.card.card_type, "PWR")
            stat_col = _TYPE_COLOR.get(self.card.card_type, C.TXT_GREY)
            lbl = fonts.get("card_desc").render(stat_label, True, stat_col)
            surf.blit(lbl, (draw_r.x + (draw_r.w - lbl.get_width()) // 2,
                             py - lbl.get_height() - 1))

        # Rarity dot
        pygame.draw.circle(surf, _RARITY_COLOR.get(self.card.rarity, C.COMMON),
                            (draw_r.right - 8, draw_r.bottom - 8), 5)

    def _draw_back(self, surf: pygame.Surface, r: pygame.Rect) -> None:
        pygame.draw.rect(surf, C.CARD_BACK, r, border_radius=6)
        pygame.draw.rect(surf, C.CARD_BACK_LINE, r, 2, border_radius=6)
        for i in range(r.x + 12, r.right, 12):
            pygame.draw.line(surf, C.CARD_BACK_LINE, (i, r.y), (i, r.bottom), 1)

    def clicked(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos) and self.clickable and not self.disabled


# ── Button ────────────────────────────────────────────────────────────────────

class Button:
    def __init__(self, text: str, x: int, y: int,
                 w: int = 180, h: int = 46,
                 style: str = "normal"):
        self.text    = text
        self.rect    = pygame.Rect(x, y, w, h)
        self.style   = style    # "normal" | "danger" | "grey"
        self.hovered = False
        self.enabled = True

    def update(self, mouse_pos: tuple[int, int]) -> None:
        self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled

    def draw(self, surf: pygame.Surface) -> None:
        if self.style == "danger":
            bg = C.BTN_DNG_H if self.hovered else C.BTN_DNG
        elif self.style == "grey":
            bg = C.BTN_GREY_H if self.hovered else C.BTN_GREY
        else:
            bg = C.BTN_HOV if self.hovered else C.BTN_BG

        pygame.draw.rect(surf, bg, self.rect, border_radius=7)
        pygame.draw.rect(surf, C.BTN_BORDER, self.rect, 2, border_radius=7)

        tc = C.TXT_LIGHT if self.enabled else C.TXT_GREY
        ts = fonts.get("button").render(self.text, True, tc)
        surf.blit(ts, (self.rect.x + (self.rect.w - ts.get_width()) // 2,
                        self.rect.y + (self.rect.h - ts.get_height()) // 2))

    def clicked(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos) and self.enabled


# ── Energy dots ───────────────────────────────────────────────────────────────

class EnergyBar:
    R = 9
    GAP = 24

    def __init__(self, x: int, y: int, max_e: int = 3):
        self.x = x
        self.y = y
        self.max_e = max_e
        self.current = max_e

    def draw(self, surf: pygame.Surface) -> None:
        for i in range(self.max_e):
            cx = self.x + i * self.GAP
            col = C.EN_FULL if i < self.current else C.EN_EMPTY
            pygame.draw.circle(surf, col, (cx, self.y), self.R)
            pygame.draw.circle(surf, C.TXT_DARK, (cx, self.y), self.R, 1)


# ── Helpers ───────────────────────────────────────────────────────────────────

def card_row_x(n: int, area_w: int = 1280, margin: int = 20) -> int:
    """Left x for a centred row of n cards."""
    total = n * CARD_W + max(0, n - 1) * CARD_GAP
    return max(margin, (area_w - total) // 2)


def build_card_row(cards: list, y: int, face_up: bool = True,
                   clickable: bool = False) -> list[CardWidget]:
    """Build a list of CardWidgets centred horizontally."""
    x0 = card_row_x(len(cards))
    widgets = []
    for i, card in enumerate(cards):
        w = CardWidget(card, x0 + i * (CARD_W + CARD_GAP), y,
                       face_up=face_up, clickable=clickable)
        widgets.append(w)
    return widgets
