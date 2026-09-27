import os, sys, asyncio
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, '/home/mjones/agy/pyzerk')

import pygame
pygame.init()
pygame.display.set_mode((800, 480))

import globals, main, player

def test_robot_clear():
    main.startNewGame()
    print('Initial: LEVEL =', globals.LEVEL, 'LEVELS_PASSED =', globals.LEVELS_PASSED, 'LIVES =', globals.LIVES, 'DB =', globals.DEATH_BLOSSOM_AVAILABLE)
    p = globals.PLAYER.sprite
    p.triggerDeathBlossom()
    print('Fired DB: DB =', globals.DEATH_BLOSSOM_AVAILABLE)

    for i in range(1, 15):
        for r in list(globals.ROBOTS.sprites()):
            r.kill()
        
        if len(globals.ROBOTS.sprites()) == 0:
            globals.LEVELS_PASSED += 1
            db_recharged_notice = False
            if globals.LEVELS_PASSED % 10 == 0:
                globals.LIVES += 1
                db_recharged_notice = not globals.DEATH_BLOSSOM_AVAILABLE
                globals.DEATH_BLOSSOM_AVAILABLE = True
            did_loop = main.startNewLevel()
        print(f'Cleared room {i} (robots) -> Now LEVEL: {globals.LEVEL}, LEVELS_PASSED: {globals.LEVELS_PASSED}, DB: {globals.DEATH_BLOSSOM_AVAILABLE}, LIVES: {globals.LIVES}, Recharged?: {db_recharged_notice}')

def test_exit_corridor():
    main.startNewGame()
    print('\nTesting Exit Corridor Method:')
    p = globals.PLAYER.sprite
    p.triggerDeathBlossom()
    print('Fired DB: DB =', globals.DEATH_BLOSSOM_AVAILABLE)

    for i in range(1, 15):
        globals.PENDING_EXIT = 'RIGHT'
        exit_dir = globals.PENDING_EXIT
        globals.PENDING_EXIT = None

        globals.LEVELS_PASSED += 1
        db_recharged_notice = False
        if globals.LEVELS_PASSED % 10 == 0:
            globals.LIVES += 1
            db_recharged_notice = not globals.DEATH_BLOSSOM_AVAILABLE
            globals.DEATH_BLOSSOM_AVAILABLE = True
        globals.LEVEL += 1
        if globals.LEVEL > globals.MAX_LEVELS:
            globals.LEVEL = 1
            globals.LEVEL_LOOP += 1

        for a in globals.OBJECTS:
            a.kill()

        main.setupRoom(globals.LEVEL, entry_side=exit_dir)
        print(f'Cleared room {i} (exit corridor) -> Now LEVEL: {globals.LEVEL}, LEVELS_PASSED: {globals.LEVELS_PASSED}, DB: {globals.DEATH_BLOSSOM_AVAILABLE}, LIVES: {globals.LIVES}, Recharged?: {db_recharged_notice}')

test_robot_clear()
test_exit_corridor()
