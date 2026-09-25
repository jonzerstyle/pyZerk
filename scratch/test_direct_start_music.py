import sys, os
sys.path.insert(0, os.getcwd())
import os
import globals
import pygame

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
except Exception:
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
import sounds
import main

# 1. Simulate boot sequence
sounds.playSound(sounds.welcomeSound)
sounds.start_game_music()

chan0 = pygame.mixer.Channel(0)
print("Boot check: Chan 0 is busy?", chan0.get_busy())
print("Boot check: Chan 0 sound is soundtrack?", chan0.get_sound() is sounds.soundTrack0Sound)
assert chan0.get_busy(), "Chan 0 should be playing music on boot!"
assert chan0.get_sound() is sounds.soundTrack0Sound, "Chan 0 sound must be soundtrack!"

# 2. Simulate user starting game WITHOUT touching music volume setting
main.startNewGame()

print("In-game check: Chan 0 is busy?", chan0.get_busy())
print("In-game check: Chan 0 sound is soundtrack?", chan0.get_sound() is sounds.soundTrack0Sound)
assert chan0.get_busy(), "Chan 0 must be playing music during gameplay!"
assert chan0.get_sound() is sounds.soundTrack0Sound, "Chan 0 sound must be soundtrack!"

# 3. Simulate gameplay SFX: shooting, explosions, level transitions
for _ in range(5):
    sounds.playSound(sounds.playerGunSound)
    sounds.playSound(sounds.robotExplodeSound)
    sounds.playSound(sounds.bulletClashSound)
    assert chan0.get_busy(), "SFX must never interrupt music!"
    assert chan0.get_sound() is sounds.soundTrack0Sound, "SFX must never replace soundtrack!"

print("ALL DIRECT BOOT AND GAMEPLAY CHECKS PASSED 100%!")
