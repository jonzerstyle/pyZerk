# Project Record: pyZerk (Python & Pygame Berzerk Port)

## 📌 Overview
This document tracks all features, architectural changes, audio updates, and deployment workflows implemented in the **pyZerk** project located at `/home/mjones/agy/pyzerk`.

---

## 🗂️ Project Structure & Tracking Locations

```text
/home/mjones/agy/
├── GAD.md                                    # Reference / research document
├── OXY.md                                    # Reference / research document
├── gemini_website_setup/
│   └── GEMINI.md                             # GoDaddy deployment & SSL setup tracking record
├── gemini_integrated_website/
│   └── DEPLOY_GODADDY.md                     # Deployment guide for GoDaddy hosting
└── pyzerk/
    ├── GEMINI.md                             # This action & project tracking record
    ├── README.md                             # Upstream Berzerk game documentation
    ├── main.py                               # Main game loop & state transitions (Menu <-> Playing)
    ├── menu.py                               # Start Menu with settings, volume sliders & instructions
    ├── globals.py                            # Game state flags (STATE_MENU, STATE_PLAYING, etc.)
    ├── keybo.py                              # Keyboard input handling & Enter key detection
    ├── sounds.py                             # Audio mixer manager, channel reservation & volume scaling
    ├── player.py                             # Player character logic & animation
    ├── robots.py                             # Enemy robot logic & pathfinding
    ├── otto.py                               # Evil Otto bouncing enemy logic
    ├── maze.py                               # Maze generation & collision
    ├── bullets.py                            # Player & robot projectiles
    ├── walls.py                              # Wall rendering & collision
    ├── sounds/                               # Sound effects & soundtrack assets
    │   ├── BMUSIC.ogg                        # Background music / ambient soundscape
    │   ├── BMUSIC.wav                        # Fallback PCM audio
    │   └── ... (gameover, otto, etc.)
    ├── webdeploy/                            # Pygbag WebAssembly deployment package
    │   ├── index.html                        # Web player HTML5 template
    │   ├── pyzerk.apk                        # Packaged Python / Pygame WASM archive
    │   ├── pyzerk.tar.gz                     # Web bundle archive
    │   └── server.py                         # Local web preview server
    └── scratch/                              # Test harnesses, sound prototypes & candidate audio
```

---

## 🚀 Chronological Record of Actions & Changes

### 1. Start Menu System Implementation
* **File Created**: [`menu.py`](file:///home/mjones/agy/pyzerk/menu.py)
* **Features Implemented**:
  * **1.0 Start Game**: Launches game session from menu.
  * **2.0 Music Volume Control**: Slider (0% to 100%) with instant live playback feedback.
  * **3.0 Other Sounds (SFX) Volume Control**: Slider (0% to 100%) with sample audio feedback (`player_gun` / `robot_explode`).
  * **Return to Menu**: Pressing `ENTER` at any time during gameplay seamlessly returns the player to the Start Menu.
  * **Controls Legend**: Visual display of controls on menu screen (Arrow keys / WASD to move, Space / F to fire, Enter to pause/return to menu).
* **State Management**:
  * Extended [`globals.py`](file:///home/mjones/agy/pyzerk/globals.py) with `STATE_MENU = 0` and `STATE_PLAYING = 1`.
  * Updated [`keybo.py`](file:///home/mjones/agy/pyzerk/keybo.py) to capture navigation (`UP`/`DOWN` to select, `LEFT`/`RIGHT` to adjust volume, `ENTER` to trigger/return).
  * Updated [`main.py`](file:///home/mjones/agy/pyzerk/main.py) to render the menu when in `STATE_MENU` and transition smoothly into `play()` upon selection.

### 2. Audio Architecture & Volume Control Updates
* **File Modified**: [`sounds.py`](file:///home/mjones/agy/pyzerk/sounds.py)
* **Changes**:
  * **Dedicated Soundtrack Channel**: Reserved channel 0 (`SOUNDTRACK_CHAN = 0`) exclusively for background music/ambience so game sound effects never interrupt or truncate the music.
  * **Dynamic Volume Functions**: Added `set_music_volume(vol)`, `get_music_volume()`, `set_sfx_volume(vol)`, `get_sfx_volume()`, `play_music_sample()`, and `play_sfx_sample()`.
  * **Audio Pre-initialization**: Standardized mixer to 44.1 kHz, 16-bit stereo, buffer 4096.

### 4. Background Soundtrack Iterations (Star Trek Soundscape)
* **Original Asset**:  (original fast-paced synth music, preserved).
* **Iteration 1 (Synthetic Hum)**: Generated 60s Enterprise bridge hum; sounded too much like 60 Hz electrical transformer buzz.
* **Iteration 2 (1950s Relays)**: Generated 50s mechanical relay clicks; sounded dry.
* **Iteration 3 (Space Trek Sound 01)**: Initial loop from Envato Elements; user requested backdrop switch.
* **Iteration 4 (Envisioning Science Fiction + Randomized Short Sounds)**:
  * **Backdrop Bed**: Sourced **Envisioning Science Fiction Starship Ambience** () from Envato Elements as requested by the user.
  * **Layered Bridge FX**: Randomly overlaid authentic shorter bridge and computer sounds on top:
    *  (Trek communicator chirp)
    *  (shuttle/bridge telemetry)
    * , , , , , 
    * , 
  * **Seamless Equal-Power Loop**: Engineered a 64.0-second seamless loop with exact 0.0 seam boundary error (mathematically continuous derivative).
  * **Chunked Vorbis Encoding**: Encoded  (813 KB, OGG Vorbis) in safe 1-second chunks to ensure zero buffer overflow, plus fallback  (PCM 16-bit).
  * **Normalization**: Peak normalized to -1.0 dBFS (RMS ~0.061) for optimal dynamic range and smooth integration with the Start Menu volume slider.

### 5. Direct Game Start Audio Fix (Channel 0 Isolation)
* **Problem**: Starting a game directly from the Start Menu without first touching the Music Volume slider caused silence (no background music).
* **Root Cause Analysis**:
  * Pygame's `mixer.find_channel(False)` was returning Channel 0 (the reserved soundtrack channel) whenever Channel 0 was idle.
  * On game boot, `welcomeSound` was played on Channel 0, making it busy when `start_game_music()` was first called.
  * When starting a new game, `startNewLevel()` played `nextLevelSound` via `playSound()`, which seized idle Channel 0 right before `start_game_music()` ran.
  * `start_game_music()` saw `chan.get_busy() == True` and skipped starting the music.
* **Resolution in `sounds.py`**:
  * **Channel Isolation**: Updated `playSound()` to strictly search and allocate from channels 1 through 15, ensuring Channel 0 (`SOUNDTRACK_CHAN`) is never hijacked by SFX.
  * **Soundtrack Verification**: Updated `start_game_music()` and `set_music_volume()` to check `if not chan.get_busy() or chan.get_sound() != soundTrack0Sound:`, guaranteeing that the music channel stops any foreign sound and reliably starts looping `soundTrack0Sound`.
  * **Automated Test**: Created `scratch/test_direct_start_music.py` to simulate boot, immediate game start without menu adjustment, and heavy SFX traffic. Verified 100% passing.

### 6. WebAssembly (Pygbag) & Website Deployment
* Packaged game assets into WASM bundles using `pygbag --build .`.
* Synchronized `pyzerk.apk` and `pyzerk.tar.gz` into [`webdeploy/`](file:///home/mjones/agy/pyzerk/webdeploy) and [`../gemini_integrated_website/pyzerk/`](file:///home/mjones/agy/gemini_integrated_website/pyzerk).

---

## 🔍 Tracking Logs & History Locations

1. **Workspace Project Records**:
   - `pyzerk/GEMINI.md`: This file, documenting all pyZerk specific changes and technical notes.
   - `gemini_website_setup/GEMINI.md`: Record for the web hosting and SSL configurations.
2. **Git Version Control**:
   - Repository: `/home/mjones/agy/pyzerk/.git`
   - Active Branch: `agy_1`
   - View recent changes: `git status`, `git diff`, `git log -n 5`
3. **CLI System Logs & Conversation Transcripts**:
   - Full JSONL execution transcript: `~/.gemini/antigravity-cli/brain/<conversation-id>/.system_generated/logs/transcript.jsonl`


### 7. Player Lives System, 10-Level Bonus Awards, Level Loop Around & HUD Status Bar
* **Player Lives Management**:
  * Added `INITIAL_LIVES = 3`, `LIVES = INITIAL_LIVES`, and `LEVELS_PASSED = 0` in `globals.py`.
  * Initialized upon fresh game start in `main.py:startNewGame()`.
* **Death & Respawn Handling**:
  * Separated room generation into `setupRoom(level_num)` and `respawnCurrentLevel()`.
  * When player is destroyed, `globals.LIVES` decrements by 1.
  * If `globals.LIVES > 0`, activates `respawn_timer` (~1s pause) displaying `PLAYER DESTROYED! LIVES REMAINING: X`, and respawns player safely in the current level room without losing level progress or score.
  * If `globals.LIVES == 0`, activates `game_over_timer` (~3s pause), plays `sounds.gameOverSound`, displays a centered retro modal with final score and levels passed, and returns cleanly to Start Menu upon expiration or ENTER keypress.
* **10-Level Passing Bonus Award**:
  * Tracked monotonic level clears via `globals.LEVELS_PASSED`.
  * When `globals.LEVELS_PASSED % 10 == 0`, awards `globals.LIVES += 1` and triggers an on-screen celebratory banner: `★ 10 LEVELS PASSED! +1 EXTRA LIFE! ★`.
* **Level Loop Around (Max Level Surpassed)**:
  * Defined `MAX_LEVELS = 50` and `LEVEL_LOOP = 0` in `globals.py`.
  * When level 50 is cleared and surpassed in `startNewLevel()`:
    * `globals.LEVEL` cleanly wraps back to **Level 1** (fixing the legacy bug where it set `LEVEL = 0`).
    * `globals.LEVEL_LOOP` increments (+1 loop cycle).
    * `globals.LEVELS_PASSED` continues monotonically across all loops (50, 51, 60...), guaranteeing seamless bonus life awards across loops.
    * Activates celebratory milestone banner: `★ MAX LEVEL SURPASSED! ENTERING LOOP X! ★`.
  * Top bar status HUD dynamically displays `LEVEL: X [LOOP Y]` during subsequent loops.
  * `startNewGame()` resets `LEVEL_LOOP` back to 0.
* **HUD Status Top Bar**:
  * Updated in-game top bar with `SCORE: X` (white, x=15), `LIVES: X` (green if >1, warning red if 1, x=190), `LEVEL: X [LOOP Y]` (cyan, x=340), and `[ENTER: MENU]` (yellow, x=655).
  * Added lives explanation to Start Menu key controls panel in `menu.py`.
* **Automated Verification**:
  * Created `scratch/test_lives_system.py` verifying:
    1. Initial 3 lives, score 0, level 1.
    2. Death decrements and room preservation on respawn.
    3. Game Over trigger at 0 lives.
    4. +1 life at level 10 and 20 passed.
    5. Top bar status HUD rendering.
    6. Surpassing Level 50 cleanly loops to Level 1, increments loop counter, awards 50-level and 60-level bonus lives, renders Loop HUD, and resets cleanly on new game. (100% PASS).
* **WebAssembly Bundle**:
  * Rebuilt via Pygbag and synced `pyzerk.apk` to `webdeploy/` and `../gemini_integrated_website/pyzerk/`.


### 8. High Score Persistence & 3-Letter Initials Entry System
* **Architecture & Storage (`highscore.py`, `highscore.json`)**:
  * Implemented dedicated high score manager with dual persistence:
    * **Desktop**: Local JSON file persistence (`highscore.json`).
    * **WebDeploy (WebAssembly / Pygbag)**: Browser `window.localStorage` persistence with **ZERO disk file writes**, ensuring full persistence across browser page reloads without filesystem access errors.
  * Default record: `100` points by `CPU`.
  * Safe environment detection via `is_web_env()` ensuring file operations are never attempted in browser mode.
* **Interactive 3-Letter Initials Entry (`Class_HighScoreEntry`)**:
  * Triggers when the player surpasses the active high score upon Game Over or manual Menu return.
  * Retro arcade dialog modal rendered centered on screen with double gold borders.
  * Supports direct letter typing (`A–Z`, `0–9`), `BACKSPACE`, `LEFT`/`RIGHT` cursor navigation, and `UP`/`DOWN` character cycling.
  * Active letter slot features pulsing indicator and directional chevrons (`▲`/`▼`).
  * Pressing `ENTER` commits initials, updates `globals.HIGH_SCORE` and `globals.HIGH_SCORE_INITIALS`, saves to `highscore.json`, and plays confirmation sound.
* **HUD & Menu Display**:
  * In-game top status bar now displays `HI: <score> (<initials>)` alongside `SCORE`, `LIVES`, `LEVEL`, and `[ENTER: MENU]`.
  * Start Menu header showcases high score marquee: `★ HIGH SCORE: <score> [<initials>] ★`.
* **Automated Unit & Regression Tests**:
  * `scratch/test_high_score.py`: 100% PASS (default loading, qualification checks, persistence, keyboard typing, arrow cycling, confirmation, and surface rendering).
* **WebAssembly Bundle**:
  * Rebuilt via Pygbag and synced `pyzerk.apk` to `webdeploy/` and `../gemini_integrated_website/pyzerk/`.


### 9. Escape Routes, Grey Maze Scrolling Transition, & Robot Startle System
* **Escape Routes & Green Exit Fields (`maze.py`, `walls.py`)**:
  * Added non-electrified **GREEN energy exits** (`Class_ExitField`) along the perimeter of the maze.
  * Dimensions: Wall segment length is **exactly twice the width of the player character** ($2 \times 15 = 30$ pixels).
  * Random generation: Every level is guaranteed between **1 and 4 exits** covering cardinal boundaries (`UP`, `DOWN`, `LEFT`, `RIGHT`).
  * **Entrance Wall Last Allocation Rule**: When generating green exits, the wall location closest to where the player entered on the level is **always allocated LAST** (only when 4 exits are generated, ensuring forward and lateral escape paths take priority).
  * Non-exit border segments remain standard **BLUE electrified walls** (lethal to touch).
  * Touching green exit safely initiates level transition without damaging the player (`globals.PENDING_EXIT`).
* **Player Spawn Positioning on Next Maze**:
  * Exiting through a green field spawns the player at the corresponding opposite entrance on the next maze:
    * Exit `UP` $\to$ Spawns at `BOTTOM` ($X=400, Y=435$, facing `UP`).
    * Exit `DOWN` $\to$ Spawns at `TOP` ($X=400, Y=45$, facing `DOWN`).
    * Exit `LEFT` $\to$ Spawns on `RIGHT` ($X=755, Y=240$, facing `LEFT`).
    * Exit `RIGHT` $\to$ Spawns on `LEFT` ($X=45, Y=240$, facing `RIGHT`).
  * Clearance zones ensure the player never collides with boundary walls or robots upon entrance.
* **5-Second Robot Startle Period (`globals.ROBOT_STARTLE_TIMER`)**:
  * Upon entering the new maze, a 5-second startle cooldown is activated (150 frames @ 30 FPS).
  * Robots can move, navigate, and track the player normally, but **cannot fire bullets**.
  * A dedicated in-game HUD banner (`★ ROBOTS STARTLED! NO FIRING (Xs) ★`) gives players clear visual countdown feedback.
* **Seamless Scrolling Maze Transition with Grey Walls**:
  * Incoming maze is pre-generated with its walls displayed in **GREY** (`#A0A0A0`) to signify an active room transition.
  * The camera smoothly scrolls the old maze out and the new grey maze into place (24 frames with smoothstep easing) in the direction of player travel.
  * Gameplay entities (player, robots, Otto, bullets) are suppressed during the scroll.
  * Upon arrival at $(0, 0)$, walls activate their normal BLUE and GREEN colors, entities appear and activate, and the 5-second robot startle timer begins.
* **Automated Unit & Flow Tests**:
  * `scratch/test_escape_routes.py`: 100% PASS (exit bounds, 30px dimensions, collision safety, opposite spawning, startle gating, and grey surface rendering).
  * `scratch/test_escape_route_flow.py`: 100% PASS (full simulated interactive flow across room escape, scroll transition, and Level 2 activation).
* **WebAssembly Bundle**:
  * Rebuilt via Pygbag and synced `pyzerk.apk` to `webdeploy/` and `../gemini_integrated_website/pyzerk/`.

### 10. Web Deployment UI Cleanup: Debug Terminal & Log Overlay Suppression
* **Issue Addressed**:
  * In the browser deployment, Pygbag's xterm.js terminal (`#pyconsole` / `#terminal`) and the on-screen debug log overlay (`#debug_overlay`) were visible over or below the game screen.
* **Changes Applied to [`webdeploy/index.html`](file:///home/mjones/agy/pyzerk/webdeploy/index.html) and [`../gemini_integrated_website/pyzerk/index.html`](file:///home/mjones/agy/gemini_integrated_website/pyzerk/index.html)**:
  * **CSS Hard Suppression**: Added `#debug_overlay, #pyconsole, #terminal, .xterm { display: none !important; visibility: hidden !important; }`.
  * **DOM Attributes**: Set `hidden` and inline `style="display: none !important;"` on `#debug_overlay`, `#pyconsole`, and `#terminal`.
  * **Pygbag Engine Configuration**:
    * Configured `xtermjs : "0"` in the root Pygbag script tag.
    * Configured `gui_debug : 0` and `gui_divider : 1` in `PyConfig`.
  * **Runtime Enforcer**: Explicitly set `pyconsole.hidden = true`, `pyconsole.style.display = "none"`, and `terminal.hidden = true` inside `custom_onload()`.
* **Result**:
  * The web game canvas displays cleanly in full focus with no terminal windows, split screens, or debug log boxes.

---

## 💾 Current Session State & Handoff Summary (Ready to Resume)

### Current Status
* **Web UI Cleanup**: Debug terminal, xterm console, and status log overlay completely hidden and suppressed in both `webdeploy/` and `gemini_integrated_website/pyzerk/`.
* **Escape Routes & Transitions**:
  * 1 to 4 perimeter green exits (30px wide, twice player character width) allowing safe room escape.
  * Smooth 24-frame scrolling transition with incoming maze walls displayed in GREY.
  * Opposite side spawn positioning for player on next maze.
  * 5-second robot startle window (robots move but cannot fire) with countdown banner.
  * Entrance wall allocated last when assigning green exits.
* **High Score System**:
  * Persistent high score with interactive 3-letter initials entry upon beating records.
  * Dual storage: local JSON on desktop, `window.localStorage` on WebAssembly with zero disk file writes.
  * In-game top status bar `HI` indicator and Start Menu marquee.
* **Lives System & Status Bar**:
  * 3 starting lives, respawn pause on death preserving room progress, and Game Over sequence when out of lives.
  * +1 extra life awarded every 10 levels passed with celebratory on-screen banner.
  * Level loop around when surpassing max level (50) wrapping cleanly to Level 1 with loop milestones (`[LOOP 2]`).
* **Start Menu System**: Fully implemented in `menu.py` with volume sliders, live sound auditioning, high score marquee, and controls legend.
* **Audio Engine**: Channel 0 reserved exclusively for soundtrack looping; SFX isolated to channels 1–15; unwatermarked Star Trek ambient soundscape in place.
* **WebAssembly**: Pygbag package rebuilt and synchronized to `webdeploy/` and `../gemini_integrated_website/pyzerk/`.
* **All Test Suites Passing (100%)**:
  * `scratch/test_escape_routes.py`: PASSED (100%)
  * `scratch/test_escape_route_flow.py`: PASSED (100%)
  * `scratch/test_high_score.py`: PASSED (100%)
  * `scratch/test_lives_system.py`: PASSED (100%)
  * `scratch/test_game.py`: PASSED (100%)
  * `scratch/test_start_menu_features.py`: PASSED (100%)
  * `scratch/test_interactive_flow.py`: PASSED (100%)
  * `scratch/test_direct_start_music.py`: PASSED (100%)

### Next Steps
1. Commit tracking documentation to branch `agy_1`.
2. Push branch `agy_1` to GitHub (`git push origin agy_1`).


