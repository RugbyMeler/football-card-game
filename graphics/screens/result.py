"""Match result screen shown after full time."""
from __future__ import annotations
import pygame
from graphics.screens.base import Screen
from graphics.constants import C, SCREEN_W, SCREEN_H
from graphics.widgets import Button, draw_text
from graphics import fonts
from graphics.engine import MatchEngine
from game.campaign import Campaign, save_campaign
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphics.app import App


class MatchResultScreen(Screen):
    def __init__(self, app: "App", campaign: Campaign, engine: MatchEngine):
        super().__init__(app)
        self.campaign = campaign
        self.won      = engine.player_won
        self.draw_    = engine.is_draw
        self.p_goals  = engine.player.goals
        self.o_goals  = engine.opponent.goals

        if self.won or self.draw_:
            campaign.wins += 1
        else:
            campaign.losses += 1

        cx = SCREEN_W // 2
        bw, bh = 240, 52

        if self.won:
            self._action_btn = Button("Collect Reward  →", cx - bw // 2, 500, bw, bh)
        elif self.draw_:
            self._action_btn = Button("Continue  →", cx - bw // 2, 500, bw, bh)
        else:
            self._action_btn = Button("Try Again", cx - bw // 2, 500, bw, bh)

        self._menu_btn = Button("Main Menu", cx - bw // 2, 568, bw, bh, style="grey")

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._action_btn.clicked(event.pos):
                return self._advance()
            if self._menu_btn.clicked(event.pos):
                from graphics.screens.menu import MainMenuScreen
                return MainMenuScreen(self.app)
        return None

    def _advance(self):
        from graphics.screens.reward import CardRewardScreen
        from graphics.screens.prematch import PreMatchScreen
        from data.opponents import OPPONENT_ROSTER

        if self.won or self.draw_:
            opp_def = OPPONENT_ROSTER[self.campaign.opponent_index]
            if opp_def.reward_pool:
                return CardRewardScreen(self.app, self.campaign)
            else:
                # Final opponent — no reward
                self.campaign.opponent_index += 1
                save_campaign(self.campaign.player_name, self.campaign.deck_ids,
                              self.campaign.opponent_index,
                              self.campaign.wins, self.campaign.losses)
                if self.campaign.opponent_index >= len(OPPONENT_ROSTER):
                    from graphics.screens.complete import CampaignCompleteScreen
                    return CampaignCompleteScreen(self.app, self.campaign)
                return PreMatchScreen(self.app, self.campaign)
        else:
            # Loss — retry same opponent
            save_campaign(self.campaign.player_name, self.campaign.deck_ids,
                          self.campaign.opponent_index,
                          self.campaign.wins, self.campaign.losses)
            return PreMatchScreen(self.app, self.campaign)

    def update(self, mouse_pos):
        self._action_btn.update(mouse_pos)
        self._menu_btn.update(mouse_pos)

    def draw(self, surf: pygame.Surface):
        surf.fill(C.BG)
        for y in range(0, SCREEN_H, 80):
            pygame.draw.line(surf, C.FIELD_LINE, (0, y), (SCREEN_W, y), 1)

        cx = SCREEN_W // 2

        # Result banner
        if self.won:
            banner_col = C.GOAL
            banner_txt = "YOU WIN!"
        elif self.draw_:
            banner_col = C.TXT_GOLD
            banner_txt = "DRAW"
        else:
            banner_col = C.CONCEDE
            banner_txt = "YOU LOSE"

        pygame.draw.rect(surf, banner_col,
                         pygame.Rect(cx - 200, 160, 400, 80), border_radius=10)
        draw_text(surf, banner_txt, "heading", C.TXT_LIGHT,
                  pygame.Rect(cx - 200, 160, 400, 80), align="center", valign="center")

        # Score
        score_str = f"{self.p_goals}  –  {self.o_goals}"
        ss = fonts.get("score").render(score_str, True, C.TXT_GOLD)
        surf.blit(ss, (cx - ss.get_width() // 2, 280))

        draw_text(surf, "FULL TIME", "subhead", C.TXT_GREY,
                  pygame.Rect(0, 350, SCREEN_W, 30), align="center")

        self._action_btn.draw(surf)
        self._menu_btn.draw(surf)
