import globals
import pygame
import misc
import os

try:
    import pygame.mixer as mixer
except ImportError:
    import android_mixer as mixer

# Reserve channel 0 exclusively for background soundtrack so SFX never interrupt it
SOUNDTRACK_CHAN = 0

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

    # Allocate 16 channels and reserve channel 0 for music
    try:
        mixer.set_num_channels(16)
        mixer.set_reserved(1)
    except Exception:
        pass

    try:
        playerDeathSound = _load_sound("player_death")
        if playerDeathSound:
            playerDeathSound.set_volume(0.8)

        robotExplodeSound = _load_sound("robot_explode")
        if robotExplodeSound:
            robotExplodeSound.set_volume(0.25)

        gameOverSound = _load_sound("gameover")
        if gameOverSound:
            gameOverSound.set_volume(0.8)

        welcomeSound = _load_sound("welcome")
        if welcomeSound:
            welcomeSound.set_volume(0.8)

        robotWalkSound = _load_sound("robot_walk")
        if robotWalkSound:
            robotWalkSound.set_volume(0.20)

        playerGunSound = _load_sound("player_gun")
        if playerGunSound:
            playerGunSound.set_volume(0.12)

        robotGunSound = _load_sound("player_gun")
        if robotGunSound:
            robotGunSound.set_volume(0.06)

        robotShotSound = _load_sound("robot_shot")
        if robotShotSound:
            robotShotSound.set_volume(0.5)

        bulletClashSound = _load_sound("bullet_clash")
        if bulletClashSound:
            bulletClashSound.set_volume(0.12)

        nextLevelSound = _load_sound("nextlevel")
        if nextLevelSound:
            nextLevelSound.set_volume(0.8)

        ottoAliveSound = _load_sound("otto")
        if ottoAliveSound:
            ottoAliveSound.set_volume(0.8)

        soundTrack0Sound = _load_sound("BMUSIC")
        if soundTrack0Sound:
            soundTrack0Sound.set_volume(0.20)
    except Exception:
        globals.SOUNDS_ON = False

def playSound(sound):
    if not globals.SOUNDS_ON or not mixer.get_init() or sound is None:
        return
    # find_channel(False) looks for an unreserved idle channel (channels 1-15)
    chan = mixer.find_channel(False)
    if chan is not None:
        chan.play(sound)

# Initialize mixer on import
init_mixer()

