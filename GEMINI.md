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

### 4. WebAssembly (Pygbag) & Website Deployment
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


---

## 💾 Current Session State & Handoff Summary (Ready to Resume)

### Current Status
* **Start Menu**: Fully implemented in `menu.py` and integrated into `main.py`.
  * 1.0 Start Game
  * 2.0 Music Volume Slider + sample output
  * 3.0 SFX Volume Slider + sample output
  * Press Enter during game to return to Start Menu
  * Controls legend on-screen
* **Audio Engine**: Reserved Channel 0 for background soundtrack in `sounds.py`.
* **Soundtrack**: Sourced **Envisioning Science Fiction Starship Ambience** with randomized short bridge sounds (`trek-communicator`, `bridge_1`, `bridge_56`, `bridge_57`, `bridge_74`, `bridge_101`, `bridge_116`, `science-fiction-space-shu`, `space-trek-02`, `space-trek-03`).
  * 64.0-second seamless equal-power loop (0.0 seam error).
  * Deployed to `sounds/BMUSIC.ogg` (813 KB Vorbis) and `sounds/BMUSIC.wav`.
  * Original backup saved at `sounds/BMUSIC_backup.ogg`.
  * Candidate audio assets saved at `/home/mjones/agy/pyzerk_audio_scratch/`.
* **WebAssembly (Pygbag)**: Rebuilt web bundle (`pyzerk.apk` / `pyzerk.tar.gz`) and synchronized to `webdeploy/` and `../gemini_integrated_website/pyzerk/`.
* **Tests**: Automated test suites in `scratch/test_start_menu_features.py` and `scratch/test_interactive_flow.py` pass with 0 errors (100%).

