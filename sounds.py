import globals
import pygame
import misc
import os
import sys

try:
    import pygame.mixer as mixer
except ImportError:
    import android_mixer as mixer

# Dedicated Channel Architecture:
# - Channel 0: SOUNDTRACK_CHAN = 0 (Looping background music)
# - Channel 1: PLAYER_GUN_CHAN = 1 (Dedicated Player Laser, zero-competition voice)
# - Channels 2 & 3: ROBOT_GUN_CHANS = (2, 3) (Dedicated alternating Robot Laser pool)
# - Channels 4-15: General SFX channels (Explosions, chimes, Otto, bullet clashes, etc.)
SOUNDTRACK_CHAN = 0
PLAYER_GUN_CHAN = 1
ROBOT_GUN_CHANS = (2, 3)
GENERAL_SFX_START_CHAN = 4

# Minimum intervals (ms) to debounce rapid duplicate sound triggers
PLAYER_GUN_DEBOUNCE_MS = 60
ROBOT_GUN_DEBOUNCE_MS = 40

_last_player_gun_time = 0
_last_robot_gun_time = 0
_robot_gun_chan_idx = 0

# Volume settings (0.0 to 1.0)
music_volume = 0.7
sfx_volume = 0.7

SFX_BASE_VOLUMES = {
    "playerDeathSound": 0.8,
    "robotExplodeSound": 0.50,
    "gameOverSound": 0.8,
    "welcomeSound": 0.8,
    "robotWalkSound": 0.25,
    "playerGunSound": 0.35,
    "robotGunSound": 0.15,
    "robotShotSound": 0.5,
    "bulletClashSound": 0.30,
    "nextLevelSound": 0.8,
    "ottoAliveSound": 0.8,
}
MUSIC_BASE_VOLUME = 0.80

# Initialize sounds to None
playerDeathSound = None
robotExplodeSound = None
gameOverSound = None
welcomeSound = None
robotWalkSound = None
playerGunSound = None
robotGunSound = None
robotShotSound = None
bulletClashSound = None
nextLevelSound = None
ottoAliveSound = None
soundTrack0Sound = None

def _load_sound(base_name):
    """Load sound preferring .ogg (optimal for Pygbag WASM), falling back to .wav."""
    for ext in [".ogg", ".wav"]:
        rel = f"sounds/{base_name}{ext}"
        path = misc.get_asset_path(rel)
        if os.path.exists(path):
            try:
                return mixer.Sound(path)
            except Exception:
                pass
    # Final attempt directly via get_asset_path
    try:
        return mixer.Sound(misc.get_asset_path(f"sounds/{base_name}.ogg"))
    except Exception:
        try:
            return mixer.Sound(misc.get_asset_path(f"sounds/{base_name}.wav"))
        except Exception:
            return None

def _get_sound_obj(name):
    return getattr(sys.modules[__name__], name, None)

def apply_volumes():
    """Apply current volume multipliers to loaded sounds."""
    for name, base_vol in SFX_BASE_VOLUMES.items():
        snd = _get_sound_obj(name)
        if snd is not None:
            try:
                snd.set_volume(base_vol * sfx_volume)
            except Exception:
                pass
    if soundTrack0Sound is not None:
        try:
            soundTrack0Sound.set_volume(MUSIC_BASE_VOLUME * music_volume)
        except Exception:
            pass

def set_music_volume(volume):
    """Set music volume scale (0.0 to 1.0) and apply to soundtrack in real-time."""
    global music_volume
    music_volume = max(0.0, min(1.0, float(volume)))
    effective_vol = MUSIC_BASE_VOLUME * music_volume
    if soundTrack0Sound is not None:
        try:
            soundTrack0Sound.set_volume(effective_vol)
        except Exception:
            pass
    try:
        if mixer.get_init():
            chan = mixer.Channel(SOUNDTRACK_CHAN)
            if music_volume <= 0.001:
                chan.set_volume(0.0)
            else:
                chan.set_volume(1.0)
                # If channel is not currently playing music, start it
                if (not chan.get_busy() or chan.get_sound() != soundTrack0Sound) and soundTrack0Sound is not None:
                    chan.stop()
                    chan.play(soundTrack0Sound, -1)
    except Exception:
        pass

def get_music_volume():
    """Return current music volume (0.0 to 1.0)."""
    return music_volume

def set_sfx_volume(volume):
    """Set SFX volume scale (0.0 to 1.0) and apply to all SFX."""
    global sfx_volume
    sfx_volume = max(0.0, min(1.0, float(volume)))
    for name, base_vol in SFX_BASE_VOLUMES.items():
        snd = _get_sound_obj(name)
        if snd is not None:
            try:
                snd.set_volume(base_vol * sfx_volume)
            except Exception:
                pass

def get_sfx_volume():
    """Return current SFX volume (0.0 to 1.0)."""
    return sfx_volume

def play_nav_sound():
    """Play a short, crisp retro tick for menu navigation and volume adjustments."""
    if not globals.SOUNDS_ON or not mixer.get_init() or bulletClashSound is None:
        return
    try:
        bulletClashSound.set_volume(SFX_BASE_VOLUMES["bulletClashSound"] * max(0.3, sfx_volume))
        playSound(bulletClashSound)
    except Exception:
        pass

def play_music_sample(duration_ms=None):
    """Restart and play music sample from the beginning at current music volume."""
    if not globals.SOUNDS_ON or not mixer.get_init() or soundTrack0Sound is None:
        return
    try:
        chan = mixer.Channel(SOUNDTRACK_CHAN)
        chan.stop()
        if music_volume > 0.001:
            soundTrack0Sound.set_volume(MUSIC_BASE_VOLUME * music_volume)
            chan.set_volume(1.0)
            chan.play(soundTrack0Sound, -1)
    except Exception:
        pass

def play_sfx_sample(sample_type="gun"):
    """Play a sample output of sound effects at current SFX volume."""
    if not globals.SOUNDS_ON or not mixer.get_init():
        return
    try:
        target_snd = playerGunSound if sample_type == "gun" else robotExplodeSound
        if target_snd is None:
            target_snd = playerGunSound or robotExplodeSound
        if target_snd and sfx_volume > 0.001:
            base_vol = SFX_BASE_VOLUMES.get("playerGunSound", 0.35)
            target_snd.set_volume(base_vol * sfx_volume)
            playSound(target_snd)
    except Exception:
        pass

def start_game_music():
    """Start looping background music at current music volume."""
    if not globals.SOUNDS_ON or not mixer.get_init() or soundTrack0Sound is None:
        return
    try:
        chan = mixer.Channel(SOUNDTRACK_CHAN)
        if music_volume > 0.001:
            soundTrack0Sound.set_volume(MUSIC_BASE_VOLUME * music_volume)
            chan.set_volume(1.0)
            if not chan.get_busy() or chan.get_sound() != soundTrack0Sound:
                chan.stop()
                chan.play(soundTrack0Sound, -1)
    except Exception:
        pass

def stop_game_music():
    """Stop the background music channel."""
    if not globals.SOUNDS_ON or not mixer.get_init():
        return
    try:
        chan = mixer.Channel(SOUNDTRACK_CHAN)
        chan.stop()
    except Exception:
        pass

def init_mixer():
    global playerDeathSound, robotExplodeSound, gameOverSound, welcomeSound
    global robotWalkSound, playerGunSound, robotGunSound, robotShotSound
    global bulletClashSound, nextLevelSound, ottoAliveSound, soundTrack0Sound

    if not globals.SOUNDS_ON:
        return

    # Pre-initialize mixer with 44.1kHz, 16-bit stereo, and 4096 buffer if not yet initialized
    if not mixer.get_init():
        try:
            mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
        except Exception:
            pass
        try:
            mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        except Exception:
            try:
                mixer.init()
            except Exception:
                globals.SOUNDS_ON = False
                return

    # Allocate 16 channels and reserve channels 0-3 (Music, Player Gun, Robot Guns)
    try:
        mixer.set_num_channels(16)
        mixer.set_reserved(GENERAL_SFX_START_CHAN)
    except Exception:
        pass

    try:
        playerDeathSound = _load_sound("player_death")
        robotExplodeSound = _load_sound("robot_explode")
        gameOverSound = _load_sound("gameover")
        welcomeSound = _load_sound("welcome")
        robotWalkSound = _load_sound("robot_walk")
        playerGunSound = _load_sound("player_gun")
        robotGunSound = _load_sound("player_gun")
        robotShotSound = _load_sound("robot_shot")
        bulletClashSound = _load_sound("bullet_clash")
        nextLevelSound = _load_sound("nextlevel")
        ottoAliveSound = _load_sound("otto")
        soundTrack0Sound = _load_sound("BMUSIC")

        apply_volumes()
    except Exception:
        globals.SOUNDS_ON = False

def play_player_gun_sound():
    """Play the player's firing laser on dedicated Channel 1 with sub-frame debounce."""
    global _last_player_gun_time
    if not globals.SOUNDS_ON or not mixer.get_init() or playerGunSound is None:
        return
    now = pygame.time.get_ticks()
    if now - _last_player_gun_time < PLAYER_GUN_DEBOUNCE_MS:
        return  # Suppress duplicate triggers on the same or adjacent frames (e.g. Death Blossom burst)
    _last_player_gun_time = now
    try:
        chan = mixer.Channel(PLAYER_GUN_CHAN)
        chan.play(playerGunSound)
    except Exception:
        pass

def play_robot_gun_sound():
    """Play a robot's firing laser on alternating Channels 2 & 3 with micro-debounce."""
    global _last_robot_gun_time, _robot_gun_chan_idx
    if not globals.SOUNDS_ON or not mixer.get_init() or robotGunSound is None:
        return
    now = pygame.time.get_ticks()
    if now - _last_robot_gun_time < ROBOT_GUN_DEBOUNCE_MS:
        return  # Suppress simultaneous robot firings on the exact same frame
    _last_robot_gun_time = now
    try:
        target_chan_id = ROBOT_GUN_CHANS[_robot_gun_chan_idx]
        _robot_gun_chan_idx = (_robot_gun_chan_idx + 1) % len(ROBOT_GUN_CHANS)
        chan = mixer.Channel(target_chan_id)
        chan.play(robotGunSound)
    except Exception:
        pass

def playSound(sound):
    """Play a sound effect with intelligent channel routing and priority management."""
    if not globals.SOUNDS_ON or not mixer.get_init() or sound is None:
        return

    # Route laser sounds to their dedicated voice channels with debounce
    if sound == playerGunSound:
        play_player_gun_sound()
        return
    elif sound == robotGunSound:
        play_robot_gun_sound()
        return

    try:
        num_chans = mixer.get_num_channels()
        # Find idle SFX channel in general SFX range (Channels 4 to num_chans-1)
        for i in range(GENERAL_SFX_START_CHAN, num_chans):
            chan = mixer.Channel(i)
            if not chan.get_busy():
                chan.play(sound)
                return
        # If all general channels busy, steal the oldest general channel (starting at GENERAL_SFX_START_CHAN)
        # NEVER steal Channel 0 (Music), Channel 1 (Player Gun), or Channels 2/3 (Robot Guns)!
        if num_chans > GENERAL_SFX_START_CHAN:
            mixer.Channel(GENERAL_SFX_START_CHAN).play(sound)
    except Exception:
        pass

# Initialize mixer on import
init_mixer()

