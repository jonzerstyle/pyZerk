import os, sys
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()
pygame.display.set_mode((800, 480))

import globals
import main
import player

main.startNewGame()
print('Initial: LEVEL =', globals.LEVEL, 'LEVELS_PASSED =', globals.LEVELS_PASSED, 'DB =', globals.DEATH_BLOSSOM_AVAILABLE)
p = globals.PLAYER.sprite
p.triggerDeathBlossom()
print('After firing DB: DB =', globals.DEATH_BLOSSOM_AVAILABLE)

for lvl in range(1, 15):
    globals.LEVELS_PASSED += 1
    recharged = False
    if globals.LEVELS_PASSED % 10 == 0:
        globals.LIVES += 1
        globals.DEATH_BLOSSOM_AVAILABLE = True
        recharged = True
    globals.LEVEL += 1
    print(f'Passed Level {lvl} -> Entering LEVEL: {globals.LEVEL}, LEVELS_PASSED: {globals.LEVELS_PASSED}, LIVES: {globals.LIVES}, DB: {globals.DEATH_BLOSSOM_AVAILABLE} (Recharged? {recharged})')
