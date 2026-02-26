# Telegram Mafia/Werewolf Game Bot

## Overview
This is a Persian Telegram bot that runs a Mafia/Werewolf game with multiple game modes. Players can join games, receive secret roles, use night abilities, and compete to find the bad players.

## Project Structure
```
.
├── main.py                 # Main bot application
├── players_display.py     # Player list formatting module
├── roles.json             # Role descriptions in Persian
├── night_abilities.json   # Night ability texts for each role
├── pyproject.toml         # Python dependencies
├── uv.lock               # Lock file for dependencies
└── generated-icon.png    # Bot icon
```

## Game Features

### Game Modes
The bot supports 5 different game modes:
- **Mighty (قدرتی)** - `/startmighty` 
- **Chaos (آشوب)** - `/startchaos`
- **Cultus (کاستوم)** - `/startcultus`
- **Romance (عاشقانه)** - `/startromance`
- **Max (مکس)** - `/startmax`

### Game Control Commands (Admin Only)
All control commands can only be used by group administrators:

- **`/extend [seconds]`** - Add or remove time from the join timer
  - Default: +30 seconds if no value specified
  - Range: -300 to +300 seconds
  - Example: `/extend 60` adds 1 minute, `/extend -45` removes 45 seconds
  - ⚠️ **Admin only**
  
- **`/begin`** - Start the game immediately (requires minimum 5 players)
  - Cancels the join timer and starts the game right away
  - ⚠️ **Admin only**
  
- **`/cancelgame`** - Cancel and reset the current game
  - Stops the timer, clears all players, and allows starting a new game
  - ⚠️ **Admin only**

### Game Flow
1. **Join Phase (5 minutes)**: Players join using inline keyboard buttons
2. **Night Phase (120 seconds)**: Players with night abilities make their choices
3. **Day Phase (180 seconds total)**:
   - **Discussion (90 seconds)**: Players discuss and identify suspects
   - **Voting (90 seconds)**: Players vote via private message buttons to eliminate a suspect
4. **Repeat**: Night and day phases alternate until game ends

### Player Limits
- Minimum: 5 players
- Maximum: 25 players per game

### Roles
The game includes various roles loaded from `roles.json`:
- **Wolves**: گرگ آلفا, گرگ 🐺, گرگینه, توله گرگ
- **Seers**: پیشگو 🔮, پیشگو, فالگیر
- **Protectors**: فرشته نگهبان, نگهبان 🛡️
- **Special Roles**: شکارچی, ساحره, قاتل فراری, and many more

## Technical Details

### Dependencies
- `python-telegram-bot>=22.5` - Official Telegram Bot API wrapper

### Environment Variables
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token (required)

### Key Components

#### Game State Management
```python
players = {}           # Player lists per mode
game_state = {}       # Role assignments per mode
player_status = {}    # Player status (alive/dead, actions, targets)
night_choices = {}    # Night phase choices
```

#### Timer System
- Join timer: 5 minutes with periodic updates
- Night timer: 120 seconds with early finish if all players act
- Auto-random selection for specific roles if time expires

#### Night Actions
- Wolves vote to attack a player (with conversion chance if Alpha Wolf present)
- Zombies attempt to infect players (conversion based on role susceptibility)
- Seers investigate player roles
- Protectors defend players
- Special roles use unique abilities
- Conversion system: victims may join attacker's team instead of dying

#### Day Actions
- 90 seconds discussion time for players to debate
- 90 seconds voting time with private voting buttons
- Each player votes once via private message
- Player with most votes is eliminated
- Vote results announced with player's role revealed
- Automatic transition to next night phase

## How to Use

### Setup
1. Create a Telegram bot via [@BotFather](https://t.me/BotFather)
2. Get your bot token
3. Add the token to Replit Secrets as `TELEGRAM_BOT_TOKEN`
4. Click "Run" to start the bot

### Playing
1. Add your bot to a Telegram group
2. Use a command like `/startmighty` to start a game
3. Players click "ورود به روستای آنلاین" to join
4. Wait for minimum 5 players (or use `/begin` to start early)
5. **Optional**: Use `/extend [seconds]` to add/remove time from the join timer
6. Game starts automatically after 5 minutes, or manually with `/begin`
7. Follow the bot's instructions for night and day phases

## Recent Changes
- **2026-02-24**: Restored project from backup and fixed dependency issues
  - Extracted project files from ZIP archive
  - Reorganized file structure to root directory
  - Fixed `python-telegram-bot` installation and verified `main.py`
  - Configured "Run Bot" workflow for development

- **2025-10-19**: Enhanced player list display with clickable links and emojis
  - Created new `players_display.py` module for better player list formatting
  - Player names are now clickable Telegram links (tg://user?id={user_id})
  - Added rank emojis (🥇 🥈 🥉) to player lists for visual appeal
  - Improved alive/dead player status display with better formatting
  - Integrated display module into `send_alive_list()` function
  - All player lists now use Markdown formatting for rich text display

- **2025-10-19**: Added admin-only game control commands
  - Implemented `/extend [seconds]` command to add/remove time from join timer (admin only)
  - Implemented `/begin` command to start game immediately with minimum players (admin only)
  - Implemented `/cancelgame` command to reset and cancel running games (admin only)
  - Added admin verification system using Telegram's built-in admin checking
  - Added timer task tracking system for cancellable join timers
  - Updated game state management to prevent duplicate game starts
  - Enhanced timer system to support dynamic time modifications
  - Added user ID display when players join (shows clickable name + ID number)

- **2025-10-15**: Added complete voting system for day phase
  - Implemented day phase voting with inline keyboard buttons
  - Added vote tracking and counting system
  - Players receive voting buttons in private messages
  - Most voted player is eliminated and their role revealed
  - Automatic transition from day voting back to night phase
  - Fixed username parsing to support usernames with underscores
  - Added validation to prevent votes for dead or non-existent players

- **2025-10-15**: Successfully deployed bot to Replit
  - Imported project from ZIP file
  - Fixed package conflict between `telegram` and `python-telegram-bot` packages
  - Removed conflicting `telegram` package from dependencies
  - Configured bot token in Replit Secrets
  - Bot is now running and ready to use

- **2024-10-14**: Code refactoring and improvements
  - Added cleaner `night_prompts` dictionary for better organization
  - Refactored `send_night_ability()` function with improved structure
  - Split callback handler into separate `handle_night_choice()` and `handle_join()` functions
  - Enhanced code readability and maintainability

## Development Notes
- The bot uses async/await for all Telegram interactions
- Persian language interface throughout
- Inline keyboards for interactive gameplay
- Private messages for role reveals and night actions
- Group messages for game flow and public events

### Code Organization
- **Night prompts dictionary**: Centralized role prompts with emoji icons for better UX
- **Modular callback handlers**: Separate functions for night choices and join actions
- **Clean function structure**: Well-documented, single-responsibility functions
- **Fallback system**: Uses `night_prompts` with fallback to `night_abilities.json` for compatibility
- **Player display module**: Separate `players_display.py` for formatting player lists with clickable links and emojis

## Future Enhancements
- Add voting system for day phase
- Implement win condition checking
- Add role-specific win conditions
- Create game statistics tracking
- Add multi-language support
