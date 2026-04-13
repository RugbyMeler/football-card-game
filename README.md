# Football Card Game ⚽🃏

A football-themed deck-building card game inspired by **Slay the Spire** — built with Python and pygame.

## Overview

Manage your squad, build your deck, and battle through a series of increasingly tough opponents to win the league. Each match is played over multiple rounds where you spend energy to play Attack and Defense cards. Your squad's stats (GK, DEF, MID, ATT) provide passive bonuses that scale your card power.

## Features

- **40 unique cards** across three types: Attack, Defense, and Special
- **Squad management** — sign players, rotate positions, scale card power with squad stats
- **Campaign mode** — 7 opponents with escalating difficulty and rewards
- **Deck building** — earn cards after victories, thin your deck to improve quality
- **Strategic gameplay** — carry unplayed cards between rounds, plan ahead

## Requirements

- Python 3.10+
- pygame 2.x

```bash
pip install pygame
```

## Running the Game

```bash
# Graphical mode (recommended)
python main.py

# Original text mode
python main.py --text
```

## How to Play

1. **Start a Campaign** — enter your manager name and kick off
2. **Play cards** each round by clicking them (costs energy shown in the circle)
3. **End the round** when happy with your plays — goals are scored based on Attack vs Defense totals
4. **Win the match** to earn new cards and player signings
5. **Manage your squad** before each match from the Pre-Match screen

## Card Types

| Type | Colour | Effect |
|------|--------|--------|
| ⚔️ Attack | Orange | Adds to your attack total |
| 🛡️ Defense | Blue | Adds to your defense total |
| ✨ Special | Purple | Utility effects (draw, energy, disruption) |

Many cards scale with your squad stats — a Striker's Run is more powerful with a high-rated attacker!
