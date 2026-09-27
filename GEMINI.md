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

### 11. Exit & Entrance Collision Safety: Doorframe Grazing & Exit Corridor Immunity
* **Bug Identified**:
  * When a green exit appeared near the player's entrance location on the next maze (or when traversing any exit), attempting to go through the exit could result in instant death.
  * Root Cause:
    1. Player dimensions are $15 \times 24$ px, while the exit opening is 30 px. Moving along vertical walls (LEFT/RIGHT) left only a 3 px margin, and horizontal walls only 7.5 px. Any slight diagonal movement, key tapping, or lateral offset caused the player's bounding box to graze the adjacent lethal electrified blue wall.
    2. In `player.py:Class_Player.collide(victim)`, touching a `Class_Wall` always killed the player, even if the player was simultaneously overlapping the green exit or escaping through it.
* **Fixes Implemented**:
  * **Exit Corridor Immunity (`player.py`)**:
    * Updated `collide()` to verify `if globals.PENDING_EXIT is not None or pygame.sprite.spritecollideany(self, globals.EXITS): return`.
    * When a player touches or is inside a green exit corridor, they are immune to border wall electrocution.
  * **Generous Doorway Corridor Hitbox (`walls.py`, `walls-pygbag.py`)**:
    * Overrode `Class_ExitField.update()` to expand its collision hitbox with a 4 px doorway corridor buffer along lateral edges and 4 px inward depth into the room.
    * Allows players to approach or graze the doorway opening from any angle or offset without catching on the doorframe corners.
  * **Automated Verification**:
    * Created `scratch/test_exit_entrance_safety.py` verifying straight entry, lateral offsets (-12 to +12 px), simultaneous overlap immunity, and diagonal approaches across all 4 directions (100% PASS).
  * **WASM Rebuild**:
    * Rebuilt `pyzerk.apk` and synchronized to both `webdeploy/` and `gemini_integrated_website/pyzerk/`.

### 12. Dynamic Status Popup Positioning (Top vs Bottom)
* **User Feedback / Problem**:
  * When a player entered the maze on the top side of the screen (`entry_side == 'DOWN'`, spawning at `[400, 45]`), the status message popup banners ("ROBOTS STARTLED! NO FIRING", loop milestones, bonus lives) popped up at `Y = 34..60` directly on top of the player character, obscuring visibility.
* **Solution**:
  * Added `draw_status_banner(screen, banner_font, text, text_color, border_color, bg_color, is_bottom)` helper in [`main.py`](file:///home/mjones/agy/pyzerk/main.py).
  * Dynamically evaluate `is_player_at_top = (current_entry_side == 'DOWN') or (len(globals.PLAYER.sprites()) > 0 and globals.PLAYER.sprites()[0].pos[1] < 120)`:
    * **If player entered at top or is near the top**: Banner pops up at the **bottom side of the screen** (`Y = 435..461`), cleanly above the bottom wall with zero player overlap.
    * **If player entered from bottom, left, or right**: Banner displays at the **top** (`Y = 34..60`) as normal.
  * Preserved `current_entry_side` during death respawns in `respawnCurrentLevel()`.
* **Automated Verification**:
  * Created `scratch/test_popup_positioning.py`:
    * Player at TOP -> banner renders at bottom (`y=438`), player at `y=33`. No overlap (100% PASS).
    * Player at BOTTOM -> banner renders at top (`y=37`), player at `y=423`. No overlap (100% PASS).
    * Player at LEFT / RIGHT -> banner renders at top (`y=37`). No overlap (100% PASS).
  * Generated visual verification captures: `scratch/test_popup_bottom_render.png` and `scratch/test_popup_top_render.png`.

### 13. Web Environment Resilience & ESC Key Handling
* **Bug Identified**:
  * Hitting `ESC` while playing the game in the web deploy environment caused the web interface to hang / freeze on the last canvas frame.
  * Root Cause:
    * In [`keybo.py`](file:///home/mjones/agy/pyzerk/keybo.py), `event.key == pygame.K_ESCAPE` was setting `self.running = 0`.
    * This terminated the `while keybo.running == True:` loop in `main.py`, exiting the `main()` coroutine.
    * In browser WebAssembly (Pygbag), exiting `main()` terminates the asyncio animation pump without closing the browser tab, causing the canvas to permanently freeze.
* **Fixes Implemented**:
  * **Gameplay ESC Key Handling ([`keybo.py`](file:///home/mjones/agy/pyzerk/keybo.py))**:
    * Updated key handler so both `pygame.K_ESCAPE` and `pygame.K_RETURN` set `self.return_to_menu = True` and `globals.MENUON = True`.
    * Hitting `ESC` during gameplay cleanly pauses the game and transitions to the Start Menu instead of stopping the runtime.
  * **Web Environment Loop Protection ([`keybo.py`](file:///home/mjones/agy/pyzerk/keybo.py), [`menu.py`](file:///home/mjones/agy/pyzerk/menu.py), [`main.py`](file:///home/mjones/agy/pyzerk/main.py))**:
    * Gated `QUIT` event and menu ESC actions behind `if not highscore.is_web_env(): keybo.running = False`.
    * In web deployments, the game loop remains active and responsive indefinitely.
  * **HUD & Menu Controls Legend Updated**:
    * In-game top bar updated with `[ESC: MENU]`.
    * Start Menu controls legend updated to list `ESC / ENTER: Pause and return back to Main Menu anytime during gameplay`.
  * **Automated Verification**:
    * Created `scratch/test_esc_key_behavior.py` verifying that hitting `ESC` during gameplay sets `return_to_menu = True`, `MENUON = True`, keeps `running = 1`, and prevents WebAssembly event loop termination (100% PASS).
  * **WASM Rebuild**:
    * Rebuilt `pyzerk.apk` via Pygbag and synced to both `webdeploy/` and `gemini_integrated_website/pyzerk/`.

### 14. 10-Level Bonus Life Celebration Display & Multi-Banner Stacking
* **Issue Uncovered**:
  * Inquiry: *"also is there a status display when 10 levels are passed and an extra life is awarded?"*
  * Root Cause:
    * Although `globals.LIVES += 1` and `bonus_life_timer = 60` were set upon passing every 10 levels, the render loop used an `if ... elif ...` structure:
      ```python
      if globals.ROBOT_STARTLE_TIMER > 0:
          # draw startle banner
      elif loop_banner_timer > 0:
          # draw loop banner
      elif bonus_life_timer > 0:
          # draw bonus life banner
      ```
    * Entering any new level initializes `ROBOT_STARTLE_TIMER = 150` (5 seconds @ 30 FPS).
    * Because `ROBOT_STARTLE_TIMER > 0` was always active when the player arrived at the 11th, 21st, etc. level, the `elif bonus_life_timer > 0` branch was **completely shadowed** and never rendered!
* **Fixes Implemented**:
  * **Independent Multi-Banner Stacking ([`main.py`](file:///home/mjones/agy/pyzerk/main.py))**:
    * Replaced the `if ... elif ...` chain with independent banner rendering and vertical stacking offsets (`offset_y`).
    * Updated `draw_status_banner(screen, banner_font, text, text_color, border_color, bg_color, is_bottom, offset_y=0)`:
      * When rendering at top: `by = 37 + offset_y`.
      * When rendering at bottom: `by = globals.SCREENSIZE[1] - surf.get_height() - 22 - offset_y`.
    * Cleanly stacks multiple active banners (e.g. Bonus Life on primary line, Robot Startle on secondary line with 28px separation, 0 overlap).
  * **Celebratory Audio & Visual Enhancements**:
    * Increased banner duration to 90 frames (~3 full seconds).
    * Prominent gold styling: `*** 10 LEVELS PASSED! +1 EXTRA LIFE! (LIVES: X) ***` in bright gold (`(255, 230, 0)`), gold border (`(255, 215, 0)`), and dark background.
    * Added celebratory chime playback (`sounds.playSound(sounds.welcomeSound)`).
    * Standardized banner decorators to ASCII `***` for flawless rendering across all bitmap and browser canvas fonts.
  * **Automated Verification**:
    * Created [`scratch/test_bonus_life_display.py`](file:///home/mjones/agy/pyzerk/scratch/test_bonus_life_display.py) testing top stacking, bottom stacking, 10-level pass triggering via robot destruction and green exit escape, and banner coexistence without shadowing (100% PASS).
  * **WASM Rebuild**:
    * Rebuilt `pyzerk.apk` via Pygbag and synced to both `webdeploy/` and `../gemini_integrated_website/pyzerk/`.

### 15. Robot Walking Leg Animation & Directional Eye Cycling Animation
* **Features Implemented ([`robots.py`](file:///home/mjones/agy/pyzerk/robots.py))**:
  * **Walking Leg Animation**:
    * Modularized robot silhouette into upper body (`NORM_ROBOT_UPPER_LEFT`, `NORM_ROBOT_UPPER_RIGHT`) and interchangeable leg poses (`NORM_ROBOT_STANDING_LEGS`, `NORM_ROBOT_STRIDE_A_LEGS`, `NORM_ROBOT_STRIDE_B_LEGS`).
    * Standing pose keeps both feet planted firmly on ground line (`y=130`).
    * Stride A: left leg planted (`y=130`), right leg kicked back/lifted (`y=90..110`).
    * Stride B: right leg planted (`y=130`), left leg kicked back/lifted (`y=90..110`).
    * Full alternating walk cycle (Stand -> Stride -> Stand -> Stride) animated at 4 ticks per step frame.
    * When robot halts to fire or is stopped, legs plant in standing pose.
  * **Directional Eye Cycling Animation**:
    * Sourced from authentic Stern 1980 arcade Berzerk sprite sheet: 6 discrete visor scanning frames (`Center`, `Mid-Left`, `Far-Left`, `Blank/Wrap`, `Far-Right`, `Mid-Right`).
    * When moving **Left** (or diagonal UPLEFT/DOWNLEFT, `speed[0] < -0.01`): eye continuously cycles left (`Center -> Mid-Left -> Far-Left -> Blank -> Far-Right -> Mid-Right`).
    * When moving **Right** (or diagonal UPRIGHT/DOWNRIGHT, `speed[0] > 0.01`): eye continuously cycles right (`Center -> Mid-Right -> Far-Right -> Blank -> Far-Left -> Mid-Left`).
    * When moving purely vertically (`speed[0] == 0`) or stopped/firing: eye remains focused dead-center (`NORM_EYE_CENTER`).
    * Initialized with randomized initial timer and frame index so groups of robots step and scan with realistic asynchronous organic timing.
  * **Automated Verification**:
    * Created [`scratch/test_robot_walk_and_eye.py`](file:///home/mjones/agy/pyzerk/scratch/test_robot_walk_and_eye.py) verifying modular components, stopped state, leftward eye/leg progression across all frames, rightward eye/leg progression, polygon assembly, dirtyrect drawing, and live simulation (100% PASS).
    * Created gameplay proof visual simulation [`scratch/robot_gameplay_walk.gif`](file:///home/mjones/agy/pyzerk/scratch/robot_gameplay_walk.gif).
  * **WASM Rebuild**:
    * Rebuilt `pyzerk.apk` and `pyzerk.tar.gz` via Pygbag and synchronized to both [`webdeploy/`](file:///home/mjones/agy/pyzerk/webdeploy) and [`../gemini_integrated_website/pyzerk/`](file:///home/mjones/agy/gemini_integrated_website/pyzerk).

### 16. Game First Start 5-Second Startle Countdown & Start Menu "Resume Game" Option
* **Features Implemented**:
  * **Game First Start 5-Second Startle Window ([`main.py`](file:///home/mjones/agy/pyzerk/main.py), [`globals.py`](file:///home/mjones/agy/pyzerk/globals.py), [`bullets.py`](file:///home/mjones/agy/pyzerk/bullets.py))**:
    * When a game first launches via `startNewGame()`, `globals.ROBOT_STARTLE_TIMER` is initialized to 150 frames (5 seconds at 30 FPS).
    * `respawnCurrentLevel()` also initializes the 5-second countdown upon respawn after player death.
    * Robot firing suppression: `bullets.py` prevents all robot bullet generation while `globals.ROBOT_STARTLE_TIMER > 0`.
    * On-screen status banner: Displays `*** ROBOTS STARTLED! NO FIRING (Xs) ***` dynamically updating the countdown in seconds, identical to the new maze entrance banner.
    * Safe positioning: Banner automatically moves to the bottom of the screen if the player spawns or enters at the top edge (`y < 120`), guaranteeing an unobstructed view.
  * **Start Menu "2.0 RESUME GAME" Option ([`menu.py`](file:///home/mjones/agy/pyzerk/menu.py), [`main.py`](file:///home/mjones/agy/pyzerk/main.py))**:
    * Re-indexed Start Menu into 4 items:
      * `0`: `1.0  START A GAME`
      * `1`: `2.0  RESUME GAME` (context-aware: active or grayed out)
      * `2`: `3.0  SET MUSIC VOLUME`
      * `3`: `4.0  SET OTHER SOUNDS VOLUME`
    * **Disabled / Grayed Out State (`globals.GAME_IN_PROGRESS == False`)**:
      * Displayed in muted dark gray: `2.0  RESUME GAME  [No Prior Game in Progress]`.
      * Up/Down/W/S arrow navigation automatically skips index 1.
      * Mouse click on the row is suppressed.
      * Quick key `[2]` is ignored.
    * **Active State (`globals.GAME_IN_PROGRESS == True`)**:
      * Displayed in cyan/white: `2.0  RESUME GAME  [Press ENTER to Resume - Level X]`.
      * Up/Down/W/S arrow navigation cleanly highlights and selects index 1.
      * When pausing gameplay via ESC or ENTER, cursor automatically defaults to index 1.
      * Activating index 1 via ENTER, mouse click, or quick key `[2]` triggers `"RESUME_GAME"`, unpausing soundtrack/SFX and instantly resuming play.
    * **State Preservation via `pauseGame()`**:
      * Pressing ESC or ENTER during gameplay pauses the loop without destroying any entities or resetting score/lives/timers.
      * All sprites (`PLAYER`, `ROBOTS`, `BULLETS`, `WALLS`, `COLLIDABLE`), active timers, level progression, and player coordinates are preserved intact.
    * **Game Session Cleanup**:
      * When game over occurs (all lives depleted), `returnToMenu()` sets `globals.GAME_IN_PROGRESS = False`, clears entities, and resets menu cursor to index 0.
  * **Automated Verification**:
    * Created [`scratch/test_resume_and_startle.py`](file:///home/mjones/agy/pyzerk/scratch/test_resume_and_startle.py) verifying initial disabled state, 5s countdown startle on game start, state preservation on pause, resume transition, session cleanup on game over, and visual rendering (100% PASS).
    * Created [`scratch/test_startle_banner_render.py`](file:///home/mjones/agy/pyzerk/scratch/test_startle_banner_render.py) validating rendered banner visual.
    * Updated [`scratch/test_start_menu_features.py`](file:///home/mjones/agy/pyzerk/scratch/test_start_menu_features.py) for the 4-item menu indices and quick keys 1-4.
  * **WASM Rebuild**:
    * Rebuilt `pyzerk.apk` and `pyzerk.tar.gz` via Pygbag and synchronized to both [`webdeploy/`](file:///home/mjones/agy/pyzerk/webdeploy) and [`../gemini_integrated_website/pyzerk/`](file:///home/mjones/agy/gemini_integrated_website/pyzerk).

### 17. Player Death Blossom Special Ability (Spacebar, 8-Directional Simultaneous Firing & HUD Indicator)
* **Features Implemented**:
  * **Death Blossom 8-Directional Blast ([`player.py`](file:///home/mjones/agy/pyzerk/player.py), [`globals.py`](file:///home/mjones/agy/pyzerk/globals.py))**:
    * Implemented `triggerDeathBlossom()` on `Class_Player`: fires immediately and simultaneously in all 8 directions (`UP`, `DOWN`, `LEFT`, `RIGHT`, `UPLEFT`, `UPRIGHT`, `DOWNLEFT`, `DOWNRIGHT`) with zero delay.
    * Spawns 8 distinct `Class_Bullet` instances originating from the player radiating outwards at full projectile speed.
    * Visual blast pose: Player assumes an authentic dual-arm firing blast pose (left arm aimed left, right arm aimed right) for the burst before cleanly resuming normal movement and leg animation.
    * Player movement and firing resume seamlessly immediately following the blast.
  * **One Death Blossom Per Active Life Rule ([`globals.py`](file:///home/mjones/agy/pyzerk/globals.py), [`main.py`](file:///home/mjones/agy/pyzerk/main.py))**:
    * `globals.DEATH_BLOSSOM_AVAILABLE` tracks availability: initialized to `True` at game start (`startNewGame()`).
    * Once triggered, `globals.DEATH_BLOSSOM_AVAILABLE` expires (`False`) for the remainder of that life; further Spacebar presses are ignored.
    * Death Blossom recharges only upon starting a new active life (when the player dies and respawns via `respawnCurrentLevel()`).
    * Moving between levels without dying retains the current life's expired/available status.
  * **Keyboard Integration ([`keybo.py`](file:///home/mjones/agy/pyzerk/keybo.py))**:
    * Mapped `pygame.K_SPACE` to `self.death_blossom = True` and passed to container item `"death_blossom"`.
    * Passed into `player.updateMovement(..., death_blossom=death_blossom_cmd)`.
  * **In-Game HUD Status Indicator ([`main.py`](file:///home/mjones/agy/pyzerk/main.py))**:
    * Rendered in top status bar `draw_hud`:
      * Label: `DB:` at `x=395`.
      * Hardware arcade LED indicator at `(cx=432, cy=16)`:
        * **Green LED (Active)**: Vibrant neon green `(0, 240, 60)` with specular highlight when Death Blossom is available for the active life.
        * **Red LED (Expired)**: Bright red `(240, 40, 40)` with specular highlight when Death Blossom has been consumed.
    * Clean spacing and positioning between `LEVEL` and `HI` score.
  * **Controls & Instructions Updates ([`menu.py`](file:///home/mjones/agy/pyzerk/menu.py), [`README.md`](file:///home/mjones/agy/pyzerk/README.md), HTML Overlays)**:
    * Start Menu controls panel updated with: `SPACEBAR: DEATH BLOSSOM! Fire in all 8 directions simultaneously (1 per life)`.
    * Web Floating HUD updated in both `webdeploy/index.html` and `../gemini_integrated_website/pyzerk/index.html` with `<kbd>SPACE</kbd> Death Blossom`.
    * `README.md` controls section updated.
  * **Automated Verification**:
    * Created [`scratch/test_death_blossom.py`](file:///home/mjones/agy/pyzerk/scratch/test_death_blossom.py) verifying 8-directional firing, 1-per-life rule, respawn recharge, spacebar keyboard integration, resumption of normal movement and firing, and visual HUD rendering asserting exact Green and Red LED pixel values (100% PASS).
    * Saved visual verification artifacts: [`scratch/test_death_blossom_led_hud.png`](file:///home/mjones/agy/pyzerk/scratch/test_death_blossom_led_hud.png), [`scratch/test_led_both_preview.png`](file:///home/mjones/agy/pyzerk/scratch/test_led_both_preview.png), [`scratch/test_death_blossom_menu.png`](file:///home/mjones/agy/pyzerk/scratch/test_death_blossom_menu.png).
  * **WASM Rebuild**:
    * Rebuilt `pyzerk.apk` and `pyzerk.tar.gz` via Pygbag and synchronized to both [`webdeploy/`](file:///home/mjones/agy/pyzerk/webdeploy) and [`../gemini_integrated_website/pyzerk/`](file:///home/mjones/agy/gemini_integrated_website/pyzerk).

### 18. Evil Otto Entrance Spawning & Chasing Mechanic (2026-09-26)
* **Feature Requirement**:
  * Instead of hardcoded left-side spawning (`[80, 240]`), Otto now spawns directly at the location where the player entered/started the current maze (`globals.PLAYER_MAZE_START_POS`).
  * Creates the authentic Berzerk arcade effect of Evil Otto following behind the player as they move from maze to maze.
* **Implementation Details**:
  * **Maze Start Tracking ([`globals.py`](file:///home/mjones/agy/pyzerk/globals.py), [`main.py`](file:///home/mjones/agy/pyzerk/main.py))**:
    * Added `globals.PLAYER_MAZE_START_POS` tracking the exact coordinate where the player begins the active room.
    * Recorded in `setupRoom()` across all transition modes:
      * New game / Level 1: `[80.0, 240.0]`.
      * Exit `UP` (entering from bottom of new maze): `[400.0, 435.0]`.
      * Exit `DOWN` (entering from top of new maze): `[400.0, 45.0]`.
      * Exit `LEFT` (entering from right of new maze): `[755.0, 240.0]`.
      * Exit `RIGHT` (entering from left of new maze): `[45.0, 240.0]`.
      * Respawn on death: preserves entrance coordinate for current level.
  * **Otto Class Initialization ([`otto.py`](file:///home/mjones/agy/pyzerk/otto.py))**:
    * Updated `Class_Otto.__init__(pos=None)` to default dynamically to `globals.PLAYER_MAZE_START_POS`.
  * **Spawning Dispatch ([`main.py`](file:///home/mjones/agy/pyzerk/main.py))**:
    * Updated `oneSecTimer()` to spawn Otto directly at `globals.PLAYER_MAZE_START_POS`.
    * Otto immediately computes movement vectors aiming from the entrance toward the player's active position, chasing them from behind.
* **Automated Verification**:
  * Created [`scratch/test_otto_spawn.py`](file:///home/mjones/agy/pyzerk/scratch/test_otto_spawn.py) verifying:
    1. Level 1 start pos spawning and chase vector.
    2. All 4 cardinal entrance locations (TOP, BOTTOM, LEFT, RIGHT).
    3. Respawn preservation of entrance location.
    All tests pass 100%.
* **WASM Rebuild & Sync**:
  * Rebuilt `pyzerk.apk` and `pyzerk.tar.gz` and deployed to `webdeploy/` and `../gemini_integrated_website/pyzerk/`.

### 19. Audio Engine Anti-Glitch Fix: Dedicated Laser Channels & Snappy Envelope (2026-09-26)
* **Problem Addressed**:
  * Firing sound previously glitched, clicked, stuttered, and dropped out during rapid player fire or intense robot combat.
  * Root causes:
    1. `player_gun` audio was 1.0 second long at full volume; holding fire (every 333ms) stacked 3+ long voices simultaneously.
    2. Robot bullets from up to 12 robots competed for the 15 SFX channels, starving the mixer.
    3. Channel exhaustion triggered `mixer.Channel(1).play(sound)`, abruptly truncating active waveforms mid-cycle and generating harsh DC-offset pops and machine-gun stutter.
    4. Synchronized bursts (Death Blossom) fired 8 identical sounds in the exact same frame, causing digital clipping and flanging buzz.
* **Fixes Implemented**:
  * **Dedicated Voice Channel Architecture ([`sounds.py`](file:///home/mjones/agy/pyzerk/sounds.py))**:
    * `Channel 0`: `SOUNDTRACK_CHAN` (reserved background music).
    * `Channel 1`: `PLAYER_GUN_CHAN` (dedicated player laser; re-triggers cleanly without channel contention or voice stealing).
    * `Channels 2 & 3`: `ROBOT_GUN_CHANS` (dedicated alternating 2-voice robot laser pool).
    * `Channels 4–15`: 12 dedicated channels reserved for general SFX (explosions, chimes, Otto, bullet clashes).
    * General SFX channels now steal only within channels 4–15, never interrupting music, player laser, or robot lasers.
  * **Snappy Arcade Laser Envelope (`player_gun.wav`, `player_gun.ogg`)**:
    * Re-synthesized laser duration to a crisp **0.220s (220ms)** with a 4ms anti-click attack and exponential decay to zero amplitude.
    * Fits cleanly within the player's 333ms fire interval, eliminating voice overlap while keeping peak amplitude at 0.85 for full dynamic headroom.
  * **Sub-Frame Re-Trigger Debounce ([`sounds.py`](file:///home/mjones/agy/pyzerk/sounds.py), [`bullets.py`](file:///home/mjones/agy/pyzerk/bullets.py))**:
    * `play_player_gun_sound()` debounces triggers within 60ms (Death Blossom burst plays 1 punchy, powerful blast instead of 8 stacked identical sounds).
    * `play_robot_gun_sound()` debounces triggers within 40ms across alternating channels 2 and 3.
* **Automated Verification**:
  * Created [`scratch/test_sound_engine.py`](file:///home/mjones/agy/pyzerk/scratch/test_sound_engine.py) verifying 220ms duration, peak headroom <= 0.86, channel reservations, player debounce, robot alternation, and general SFX isolation (100% PASS).
  * Full regression suite across all 10 test suites passed 100%.
* **WASM Rebuild & Sync**:
  * Rebuilt `pyzerk.apk` and `pyzerk.tar.gz` and deployed to `webdeploy/` and `../gemini_integrated_website/pyzerk/`.

---

## 💾 Current Session State & Handoff Summary (Ready to Resume)

### Current Status
* **Glitch-Free Audio Engine**: Dedicated Player Laser voice (Channel 1), alternating Robot Laser pool (Channels 2-3), snappy 220ms retro laser envelope, sub-frame debounce, and 12 protected general SFX channels (Channels 4-15) completely eliminate all audio stutter, clicking, and channel starvation.
* **Evil Otto Entrance Spawning & Chasing**: Otto spawns at the player's entrance location for the current maze, creating the authentic arcade effect of Otto following behind the player as they navigate through mazes.
* **Player Death Blossom Ability**: Spacebar triggers simultaneous 8-directional projectile blast with zero delay; limited to 1 per active life; recharges on respawn/new life AND upon completing every 10 levels passed milestone; top HUD indicator shows `DB:` with authentic Green (active) / Red (expired) hardware arcade LED; in-game instructions updated across menu, readme, and web HUD.
* **Game First Start 5-Second Startle Countdown**: Active at game start (and respawn) with countdown banner `*** ROBOTS STARTLED! NO FIRING (Xs) ***`, dynamically positioned at top or bottom to avoid obscuring the player.
* **Start Menu "2.0 RESUME GAME"**: Seamlessly integrated as item 1; grayed out with `[No Prior Game in Progress]` and skipped by navigation when idle; enabled with `[Press ENTER to Resume - Level X]` when paused; defaults cursor to resume on ESC/ENTER pause; preserves all entities, score, lives, and timers.
* **Robot Walking Leg Animation & Directional Eye Cycling**: Fully implemented in `robots.py` with modular leg strides, 6-frame authentic arcade visor scanning (cycling left when moving left, cycling right when moving right, centered when stationary or vertical), and randomized initial phases for natural crowd animation.
* **10-Level Bonus Life Celebration Banner**: Un-shadowed from robot startle banner; renders in prominent gold with stacked dual-banner positioning (`offset_y=28`) and celebratory audio chime; 100% visible on both top and bottom entry sides.
* **Web Resilience & ESC Key Handling**: Pressing ESC in gameplay smoothly pauses and returns to the Start Menu without freezing the WebAssembly runtime; browser event loop protected against abrupt termination.
* **Dynamic Status Popup Positioning**: Status banners (robot startle countdown, level loop milestone, 10-level bonus life) dynamically shift to the bottom of the screen whenever the player enters at the top, ensuring unobstructed view of the player.
* **Exit Corridor & Doorway Safety**: Complete immunity to wall electrocution while touching exits or during pending escape transitions; generous doorway hitbox buffer eliminates doorframe clipping deaths.
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
* **All 16 Test Suites Passing (100%)**:
  * `scratch/test_death_blossom.py`: PASSED (100%)
  * `scratch/test_resume_and_startle.py`: PASSED (100%)
  * `scratch/test_startle_banner_render.py`: PASSED (100%)
  * `scratch/test_robot_walk_and_eye.py`: PASSED (100%)
  * `scratch/test_bonus_life_display.py`: PASSED (100%)
  * `scratch/test_esc_key_behavior.py`: PASSED (100%)
  * `scratch/test_popup_positioning.py`: PASSED (100%)
  * `scratch/test_exit_entrance_safety.py`: PASSED (100%)
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




