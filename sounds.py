import globals
import pygame

try:
    import pygame.mixer as mixer
except ImportError:
    import android_mixer as mixer

# assume we have at least 8 channels 0 through 7
SOUNDTRACK_CHAN = 7

# setup sounds
if (globals.SOUNDS_ON == True): 
    playerDeathSound = mixer.Sound("sounds/player_death.wav")
    playerDeathSound.set_volume(1.5)
    robotExplodeSound = mixer.Sound("sounds/robot_explode.ogg")
    robotExplodeSound.set_volume(.25)
    gameOverSound = mixer.Sound("sounds/gameover.wav")
    gameOverSound.set_volume(1.0)
    welcomeSound = mixer.Sound("sounds/welcome.wav")
    welcomeSound.set_volume(1.0)
    robotWalkSound = mixer.Sound("sounds/robot_walk.ogg")
    robotWalkSound.set_volume(.25)
    playerGunSound = mixer.Sound("sounds/player_gun.ogg")
    playerGunSound.set_volume(.10)
    robotGunSound = mixer.Sound("sounds/player_gun.ogg")
    robotGunSound.set_volume(.01)
    robotShotSound = mixer.Sound("sounds/robot_shot.wav")
    robotShotSound.set_volume(.75)
    bulletClashSound = mixer.Sound("sounds/bullet_clash.ogg")
    bulletClashSound.set_volume(.10)
    nextLevelSound = mixer.Sound("sounds/nextlevel.wav")
    nextLevelSound.set_volume(1.0)
    ottoAliveSound = mixer.Sound("sounds/otto.wav")
    ottoAliveSound.set_volume(1.0)
    soundTrack0Sound = mixer.Sound("sounds/BMUSIC.ogg")
    soundTrack0Sound.set_volume(0.25)

    mixer.set_reserved(SOUNDTRACK_CHAN)

def playSound(sound):
    chan = mixer.find_channel(False)
    # may want to queue sound on a existing channel
    # but not reserved if a open channel is not found
    # tbd
    if (chan != None):
        chan.play(sound)

