"""Card reward, player signing, and deck-thinning screens shown after a win."""
from __future__ import annotations
import random
import pygame
from graphics.screens.base import Screen
from graphics.constants import C, SCREEN_W, SCREEN_H, CARD_W, CARD_H, CARD_GAP
from graphics.widgets import Button, CardWidget, draw_text, blit_wrapped, card_row_x
from graphics import fonts
from game.campaign import Campaign
from data.cards import get as get_card, CARD_BY_ID
from data.opponents import OPPONENT_ROSTER
from data.players import PLAYER_BY_ID
from game.squad import Position
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphics.app import App


class CardRewardScreen(Screen):
    def __init__(self, app: "App", campaign: Campaign):
        super().__init__(app)
        self.campaign = campaign

        opp_def = OPPONENT_ROSTER[campaign.opponent_index]
        pool_ids = opp_def.reward_pool
        sample = random.sample(pool_ids, min(3, len(pool_ids)))
        self._reward_cards = [get_card(cid) for cid in sample]
        self._selected: int | None = None

        y = SCREEN_H // 2 - CARD_H // 2 + 20
        x0 = card_row_x(len(self._reward_cards))
        self._card_widgets = [
            CardWidget(c, x0 + i * (CARD_W + CARD_GAP + 20), y,
                       face_up=True, clickable=True)
            for i, c in enumerate(self._reward_cards)
        ]

        cx = SCREEN_W // 2
        self._confirm = Button("Add to Deck  →", cx - 120, SCREEN_H - 110, 240, 50)
        self._confirm.enabled = False

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Card selection
            for i, w in enumerate(self._card_widgets):
                if w.clicked(event.pos):
                    self._selected = i
                    for j, ww in enumerate(self._card_widgets):
                        ww.selected = (j == i)
                    self._confirm.enabled = True
                    return None

            if self._confirm.clicked(event.pos) and self._selected is not None:
                chosen = self._reward_cards[self._selected]
                self.campaign.deck_ids.append(chosen.id)
                return DeckThinningScreen(self.app, self.campaign)
        return None

    def update(self, mouse_pos):
        for w in self._card_widgets:
            w.update(mouse_pos)
        self._confirm.update(mouse_pos)

    def draw(self, surf: pygame.Surface):
        surf.fill(C.BG)
        for y in range(0, SCREEN_H, 80):
            pygame.draw.line(surf, C.FIELD_LINE, (0, y), (SCREEN_W, y), 1)

        draw_text(surf, "CARD REWARD", "heading", C.TXT_GOLD,
                  pygame.Rect(0, 60, SCREEN_W, 50), align="center")
        draw_text(surf, "Choose one card to add to your deck",
                  "body", C.TXT_GREY,
                  pygame.Rect(0, 112, SCREEN_W, 30), align="center")

        for w in self._card_widgets:
            w.draw(surf)

        if self._selected is not None:
            card = self._reward_cards[self._selected]
            info = fonts.get("body").render(
                f"Selected: {card.name}  ({card.card_type.value})", True, C.TXT_LIGHT)
            surf.blit(info, (SCREEN_W // 2 - info.get_width() // 2, SCREEN_H - 160))

        self._confirm.draw(surf)


class DeckThinningScreen(Screen):
    def __init__(self, app: "App", campaign: Campaign):
        super().__init__(app)
        self.campaign = campaign
        self._selected: int | None = None
        self._scroll = 0
        self._build_buttons()

    def _build_buttons(self):
        cx = SCREEN_W // 2
        self._remove_btn = Button("Remove Card", cx - 250, SCREEN_H - 90, 230, 50,
                                   style="danger")
        self._skip_btn   = Button("Skip  →",     cx + 20,  SCREEN_H - 90, 230, 50)
        self._remove_btn.enabled = False

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self._scroll = max(0, self._scroll - 1)
            elif event.button == 5:
                self._scroll = min(max(0, len(self.campaign.deck_ids) - 12), self._scroll + 1)

            if event.button == 1:
                # Click a card row
                y0 = 170
                row_h = 38
                for i, cid in enumerate(self.campaign.deck_ids[self._scroll:]):
                    row = pygame.Rect(SCREEN_W // 2 - 280, y0 + i * row_h, 560, row_h - 2)
                    if y0 + i * row_h + row_h > SCREEN_H - 110:
                        break
                    if row.collidepoint(event.pos):
                        self._selected = i + self._scroll
                        self._remove_btn.enabled = True
                        return None

                if self._remove_btn.clicked(event.pos) and self._selected is not None:
                    self.campaign.deck_ids.pop(self._selected)
                    self._selected = None
                    self._remove_btn.enabled = False
                    return self._finish()

                if self._skip_btn.clicked(event.pos):
                    return self._finish()
        return None

    def _finish(self):
        from graphics.screens.prematch import PreMatchScreen
        from graphics.screens.complete import CampaignCompleteScreen

        opp_def = OPPONENT_ROSTER[self.campaign.opponent_index]
        self.campaign.opponent_index += 1
        self.campaign.save()

        # Offer a player signing if this opponent has a player reward pool
        if opp_def.player_reward_pool:
            return PlayerRewardScreen(self.app, self.campaign)

        if self.campaign.opponent_index >= len(OPPONENT_ROSTER):
            return CampaignCompleteScreen(self.app, self.campaign)
        return PreMatchScreen(self.app, self.campaign)

    def update(self, mouse_pos):
        self._remove_btn.update(mouse_pos)
        self._skip_btn.update(mouse_pos)

    def draw(self, surf: pygame.Surface):
        surf.fill(C.BG)

        draw_text(surf, "DECK MANAGEMENT", "heading", C.TXT_GOLD,
                  pygame.Rect(0, 50, SCREEN_W, 50), align="center")
        draw_text(surf, "Remove one card to thin your deck (optional)",
                  "body", C.TXT_GREY,
                  pygame.Rect(0, 102, SCREEN_W, 30), align="center")

        # Deck list
        panel = pygame.Rect(SCREEN_W // 2 - 290, 140, 580, SCREEN_H - 260)
        pygame.draw.rect(surf, C.BG_PANEL, panel, border_radius=8)
        pygame.draw.rect(surf, C.FIELD_LINE, panel, 1, border_radius=8)

        y0 = 170
        row_h = 38
        for i, cid in enumerate(self.campaign.deck_ids[self._scroll:]):
            ry = y0 + i * row_h
            if ry + row_h > SCREEN_H - 110:
                break
            card = CARD_BY_ID[cid]
            row = pygame.Rect(SCREEN_W // 2 - 280, ry, 560, row_h - 2)
            is_sel = (i + self._scroll == self._selected)
            bg = C.BTN_DNG if is_sel else C.BG_STRIPE
            pygame.draw.rect(surf, bg, row, border_radius=4)

            type_col = {
                "Attack": C.ATK, "Defense": C.DEF, "Special": C.SPC
            }.get(card.card_type.value, C.TXT_GREY)
            tag = fonts.get("small").render(f"[{card.card_type.value[:3].upper()}]",
                                             True, type_col)
            surf.blit(tag, (row.x + 8, ry + (row_h - tag.get_height()) // 2 - 1))

            name = fonts.get("body").render(card.name, True, C.TXT_LIGHT)
            surf.blit(name, (row.x + 60, ry + (row_h - name.get_height()) // 2 - 1))

            cost = fonts.get("small").render(f"Cost {card.cost}", True, C.TXT_GREY)
            surf.blit(cost, (row.right - cost.get_width() - 10,
                              ry + (row_h - cost.get_height()) // 2 - 1))

        deck_count = fonts.get("small").render(
            f"{len(self.campaign.deck_ids)} cards total", True, C.TXT_GREY)
        surf.blit(deck_count, (SCREEN_W // 2 - deck_count.get_width() // 2, SCREEN_H - 115))

        self._remove_btn.draw(surf)
        self._skip_btn.draw(surf)


# ── Player signing screen ─────────────────────────────────────────────────────

_POS_COLORS = {
    "GK":  ( 40, 100, 160), "DEF": ( 40, 140,  40),
    "MID": (150, 120,  30), "ATT": (160,  40,  40),
}


class PlayerRewardScreen(Screen):
    """Offer the player a chance to sign one new player to their bench."""

    def __init__(self, app, campaign: Campaign):
        super().__init__(app)
        self.campaign = campaign

        # Opponent index already incremented; use the one just beaten
        prev_idx = campaign.opponent_index - 1
        opp_def  = OPPONENT_ROSTER[prev_idx] if prev_idx >= 0 else None
        pool_ids = opp_def.player_reward_pool if opp_def else []
        sample   = random.sample(pool_ids, min(3, len(pool_ids)))
        self._players = [PLAYER_BY_ID[pid].copy() for pid in sample]
        self._selected: int | None = None

        cx, bw, bh = SCREEN_W // 2, 240, 50
        self._confirm = Button("Sign Player →", cx - bw // 2, SCREEN_H - 90, bw, bh)
        self._skip    = Button("No Thanks",     cx - bw // 2 + 260, SCREEN_H - 90, 180, bh,
                               style="grey")
        self._confirm.enabled = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for i, r in enumerate(self._player_rects()):
                if r.collidepoint(pos):
                    self._selected = i
                    self._confirm.enabled = True
                    return None
            if self._confirm.clicked(pos) and self._selected is not None:
                player = self._players[self._selected]
                self.campaign.squad.add_to_bench(player)
                self.campaign.save()
                return self._next()
            if self._skip.clicked(pos):
                return self._next()
        return None

    def _next(self):
        from graphics.screens.prematch import PreMatchScreen
        from graphics.screens.complete import CampaignCompleteScreen
        if self.campaign.opponent_index >= len(OPPONENT_ROSTER):
            return CampaignCompleteScreen(self.app, self.campaign)
        return PreMatchScreen(self.app, self.campaign)

    def _player_rects(self) -> list[pygame.Rect]:
        pw, ph = 340, 150
        gap = 20
        total = len(self._players) * pw + (len(self._players) - 1) * gap
        x0 = (SCREEN_W - total) // 2
        return [pygame.Rect(x0 + i * (pw + gap), 220, pw, ph)
                for i in range(len(self._players))]

    def update(self, mouse_pos):
        self._confirm.update(mouse_pos)
        self._skip.update(mouse_pos)

    def draw(self, surf: pygame.Surface):
        surf.fill(C.BG)
        for y in range(0, SCREEN_H, 80):
            pygame.draw.line(surf, C.FIELD_LINE, (0, y), (SCREEN_W, y), 1)

        draw_text(surf, "SIGN A PLAYER", "heading", C.TXT_GOLD,
                  pygame.Rect(0, 60, SCREEN_W, 50), align="center")
        draw_text(surf, "Choose one player to add to your bench",
                  "body", C.TXT_GREY, pygame.Rect(0, 112, SCREEN_W, 30), align="center")

        for i, (player, rect) in enumerate(zip(self._players, self._player_rects())):
            selected = (i == self._selected)
            pos_col  = _POS_COLORS.get(player.position.value, C.BG_PANEL)
            bg       = tuple(min(255, c + 25) for c in pos_col) if selected else pos_col
            pygame.draw.rect(surf, bg, rect, border_radius=8)
            border_c = C.CARD_BORDER_SEL if selected else C.FIELD_LINE
            pygame.draw.rect(surf, border_c, rect, 3 if selected else 1, border_radius=8)

            # Position badge
            badge = pygame.Rect(rect.x + 8, rect.y + 8, 44, 22)
            pygame.draw.rect(surf, (0, 0, 0, 100), badge, border_radius=4)
            draw_text(surf, player.position.value, "small", C.TXT_GOLD,
                      badge, align="center", valign="center")

            # Name
            ns = fonts.get("subhead").render(player.name, True, C.TXT_LIGHT)
            surf.blit(ns, (rect.x + 60, rect.y + 10))

            # Stats
            ss = fonts.get("body").render(
                f"ATK {player.att_power}   DEF {player.def_power}", True, C.TXT_GOLD)
            surf.blit(ss, (rect.x + 60, rect.y + 38))

            # Rarity
            rc = {"Common": C.COMMON, "Uncommon": C.UNCOMMON, "Rare": C.RARE}.get(
                player.rarity.value, C.COMMON)
            pygame.draw.circle(surf, rc, (rect.right - 14, rect.y + 14), 6)

            # Description
            blit_wrapped(surf, player.description, "small", C.TXT_GREY,
                         rect.x + 8, rect.y + 70, rect.w - 16, max_lines=3)

        self._confirm.draw(surf)
        self._skip.draw(surf)
