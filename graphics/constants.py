"""Layout constants, colours, and card dimensions."""

SCREEN_W = 1280
SCREEN_H = 768
FPS      = 60
TITLE    = "Football Card Game"

# ── Card geometry ────────────────────────────────────────────────────────────
CARD_W   = 100
CARD_H   = 145
CARD_GAP = 10     # horizontal gap between cards in a row


# ── Colour palette ───────────────────────────────────────────────────────────
class C:
    # Backgrounds
    BG          = (18, 50, 18)
    BG_PANEL    = (12, 35, 12)
    BG_STRIPE   = (22, 62, 22)   # alternating stripe for areas
    FIELD_LINE  = (30, 78, 30)

    # Cards
    CARD_BG          = (248, 238, 215)
    CARD_BG_HOVER    = (255, 250, 228)
    CARD_BG_DISABLED = (168, 160, 148)
    CARD_BORDER      = (172, 154, 118)
    CARD_BORDER_SEL  = (255, 215,   0)   # gold
    CARD_BORDER_HOV  = (255, 245, 150)
    CARD_BACK        = ( 30,  60, 120)
    CARD_BACK_LINE   = ( 42,  75, 140)

    # Card-type stripe (top of card)
    ATK  = (185, 42,  42)
    DEF  = ( 42, 85, 185)
    SPC  = (130, 52, 185)

    # Rarity indicator dot
    COMMON   = (180, 180, 180)
    UNCOMMON = (100, 200, 100)
    RARE     = (255, 185,   0)

    # Text
    TXT_DARK   = ( 25,  18,   8)
    TXT_LIGHT  = (242, 238, 225)
    TXT_GOLD   = (255, 215,   0)
    TXT_RED    = (225,  55,  55)
    TXT_GREEN  = ( 80, 210,  80)
    TXT_BLUE   = (100, 155, 255)
    TXT_GREY   = (160, 160, 160)

    # Buttons
    BTN_BG     = ( 45,  75,  45)
    BTN_HOV    = ( 65, 105,  65)
    BTN_BORDER = ( 90, 150,  90)
    BTN_DNG    = (110,  38,  38)   # danger / destructive
    BTN_DNG_H  = (150,  55,  55)
    BTN_GREY   = ( 55,  55,  55)
    BTN_GREY_H = ( 75,  75,  75)

    # Energy dots
    EN_FULL  = (255, 205,  50)
    EN_EMPTY = ( 55,  68,  55)

    # Status bar accents
    GOAL     = ( 60, 160,  60)
    CONCEDE  = (160,  40,  40)
    NEUTRAL  = ( 40,  60,  40)


# ── Match-screen layout (y positions, heights) ───────────────────────────────
# Total: STATUS_H + OPP_H + LOG_H + PLY_H + HAND_H + ACTION_H = 768
STATUS_H  = 55
OPP_H     = CARD_H + 30    # 175
LOG_H     = 80
PLY_H     = CARD_H + 30    # 175
HAND_H    = CARD_H + 30    # 175
ACTION_H  = SCREEN_H - STATUS_H - OPP_H - LOG_H - PLY_H - HAND_H  # 108

STATUS_Y  = 0
OPP_Y     = STATUS_Y + STATUS_H             # 55
LOG_Y     = OPP_Y    + OPP_H               # 230
PLY_Y     = LOG_Y    + LOG_H               # 310
HAND_Y    = PLY_Y    + PLY_H               # 485
ACTION_Y  = HAND_Y   + HAND_H              # 660
