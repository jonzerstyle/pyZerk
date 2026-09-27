import os, sys
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, '/home/mjones/agy/pyzerk')

import pygame
pygame.init()
screen = pygame.display.set_mode((800, 480))

import globals, main, player, keybo
from cclass import Class_Container

def test_full_recharge_and_firing_cycle():
    print("Testing Full Free Life + Death Blossom Recharge and Firing Cycle...")
    main.startNewGame()
    assert globals.DEATH_BLOSSOM_AVAILABLE == True, "DB should start ready"
    
    # 1. Fire Death Blossom in Level 1
    p = globals.PLAYER.sprite
    assert p.triggerDeathBlossom() == True, "Should fire DB in level 1"
    assert globals.DEATH_BLOSSOM_AVAILABLE == False, "DB should be expired"
    
    # 2. Advance 9 levels (entering Level 10, LEVELS_PASSED = 9)
    for lvl in range(1, 10):
        globals.PENDING_EXIT = 'RIGHT'
        exit_dir = globals.PENDING_EXIT
        globals.PENDING_EXIT = None
        globals.LEVELS_PASSED += 1
        if globals.LEVELS_PASSED % 10 == 0:
            globals.LIVES += 1
            globals.DEATH_BLOSSOM_AVAILABLE = True
        globals.LEVEL += 1
    
    assert globals.LEVELS_PASSED == 9
    assert globals.DEATH_BLOSSOM_AVAILABLE == False, "After 9 levels passed, still not recharged"
    
    # 3. Advance the 10th level (entering Level 11, LEVELS_PASSED = 10)
    globals.PENDING_EXIT = 'RIGHT'
    exit_dir = globals.PENDING_EXIT
    globals.PENDING_EXIT = None
    globals.LEVELS_PASSED += 1
    recharged = False
    if globals.LEVELS_PASSED % 10 == 0:
        globals.LIVES += 1
        db_recharged_notice = not globals.DEATH_BLOSSOM_AVAILABLE
        globals.DEATH_BLOSSOM_AVAILABLE = True
        recharged = True
    globals.LEVEL += 1
    
    assert globals.LEVELS_PASSED == 10
    assert recharged == True, "Recharge must trigger on 10th level passed"
    assert globals.DEATH_BLOSSOM_AVAILABLE == True, "Death Blossom MUST be available (Green)"
    assert db_recharged_notice == True, "db_recharged_notice should be True"
    
    # 4. Set up room for Level 11 and test player firing Death Blossom with Spacebar
    main.setupRoom(globals.LEVEL, entry_side='RIGHT')
    p_lvl11 = globals.PLAYER.sprite
    assert p_lvl11 is not None, "Player must exist in room"
    assert globals.DEATH_BLOSSOM_AVAILABLE == True, "Death blossom must still be available in new room"
    
    # Simulate Spacebar press via keybo and container
    kb = keybo.Class_ProcessKeybo()
    cont = Class_Container()
    ev_space = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    kb.run(globals.SCREENSIZE, screen, (0, 0, 0), cont, events=[ev_space])
    assert cont.getItem("death_blossom") == True, "Container must have death_blossom == True"
    
    # Execute updateMovement
    main.updateMovement(cont)
    assert globals.DEATH_BLOSSOM_AVAILABLE == False, "Death blossom should now be consumed"
    assert len(globals.BULLETS) == 8, f"Expected 8 bullets fired, got {len(globals.BULLETS)}"
    print("  -> Free life awarded: LIVES increased, DB recharged to Green, and Spacebar successfully fires Death Blossom!")

test_full_recharge_and_firing_cycle()
