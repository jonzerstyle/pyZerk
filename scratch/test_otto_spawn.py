import os
import sys
import copy
import math

# Set headless environment for SDL
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# Add pyzerk root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()
pygame.display.set_mode((800, 480))

import globals
import main
import otto
import player
import movement

def setup_clean_env():
    for grp in [globals.OBJECTS, globals.ROBOTS, globals.OTTO, globals.PLAYER, globals.BULLETS, globals.COLLIDABLE, globals.WALLS, globals.EXITS]:
        grp.empty()
    globals.LIVES = 3
    globals.LEVEL = 1
    globals.LEVELS_PASSED = 0
    globals.OTTOTIMER = otto.ottoTimerReload

def test_initial_level_otto_spawn():
    print("Testing initial game / level 1 Otto spawn location...")
    setup_clean_env()
    
    # Setup Room for level 1 (default start pos)
    main.setupRoom(1, entry_side=None)
    p = globals.PLAYER.sprite
    assert p is not None, "Player should be spawned"
    assert p.pos == [80.0, 240.0], f"Expected player at [80.0, 240.0], got {p.pos}"
    assert globals.PLAYER_MAZE_START_POS == [80.0, 240.0], f"Expected PLAYER_MAZE_START_POS [80.0, 240.0], got {globals.PLAYER_MAZE_START_POS}"

    # Move player into the room (player runs toward center)
    p.pos = [350.0, 240.0]
    p.update()

    # When Otto spawns, Otto must spawn at player's initial start pos [80.0, 240.0]
    o = otto.Class_Otto()
    assert o.pos == [80.0, 240.0], f"Expected Otto to spawn at maze start [80.0, 240.0], got {o.pos}"
    assert o in globals.OTTO.sprites()

    # Verify Otto chases player from the start pos
    o.updateMovement(p)
    assert o.speed[0] > 0, "Otto should be moving right toward player"
    assert abs(o.speed[1]) < 0.001, "Otto vertical movement should be 0 since aligned horizontally"
    print("  -> Initial level Otto successfully spawned at player's start pos [80.0, 240.0] and is chasing player!")

def test_all_exit_entry_sides_otto_spawn():
    print("Testing Otto spawn across all 4 maze entrance locations...")
    
    test_cases = [
        ('UP', [400.0, 435.0], "BOTTOM entrance (entering from bottom after exiting UP)"),
        ('DOWN', [400.0, 45.0], "TOP entrance (entering from top after exiting DOWN)"),
        ('LEFT', [755.0, 240.0], "RIGHT entrance (entering from right after exiting LEFT)"),
        ('RIGHT', [45.0, 240.0], "LEFT entrance (entering from left after exiting RIGHT)"),
    ]

    for entry_side, expected_pos, desc in test_cases:
        setup_clean_env()
        main.setupRoom(2, entry_side=entry_side)
        p = globals.PLAYER.sprite
        assert p is not None
        assert p.pos == expected_pos, f"Expected player at {expected_pos} for {desc}, got {p.pos}"
        assert globals.PLAYER_MAZE_START_POS == expected_pos, f"Expected start pos {expected_pos}, got {globals.PLAYER_MAZE_START_POS}"

        # Player moves away from entrance into center of room
        p.pos = [400.0, 240.0]
        p.update()

        # Otto spawns
        globals.OTTO.empty()
        o = otto.Class_Otto()
        assert o.pos == expected_pos, f"Expected Otto to spawn at {expected_pos} for {desc}, got {o.pos}"
        
        # Verify Otto movement vectors point from entrance towards player's new position
        o.updateMovement(p)
        dx = p.pos[0] - expected_pos[0]
        dy = p.pos[1] - expected_pos[1]
        dist = math.hypot(dx, dy)
        expected_speed_x = otto.otto_speed_mag * (dx / dist)
        expected_speed_y = otto.otto_speed_mag * (dy / dist)
        
        assert abs(o.speed[0] - expected_speed_x) < 0.01, f"Expected speed x {expected_speed_x}, got {o.speed[0]}"
        assert abs(o.speed[1] - expected_speed_y) < 0.01, f"Expected speed y {expected_speed_y}, got {o.speed[1]}"
        print(f"  -> Verified {desc}: Otto spawned at entrance {expected_pos} and chases player!")

def test_respawn_preserves_otto_spawn_location():
    print("Testing that respawn on current level preserves player's maze start location...")
    setup_clean_env()
    
    # Player entered room from LEFT exit (spawned at right [755.0, 240.0])
    main.current_entry_side = 'LEFT'
    main.setupRoom(3, entry_side='LEFT')
    assert globals.PLAYER_MAZE_START_POS == [755.0, 240.0]

    # Player moves and dies
    globals.PLAYER.sprite.pos = [500.0, 240.0]
    
    # Respawn
    main.respawnCurrentLevel()
    assert globals.PLAYER.sprite.pos == [755.0, 240.0]
    assert globals.PLAYER_MAZE_START_POS == [755.0, 240.0]

    # Spawn Otto
    globals.OTTO.empty()
    o = otto.Class_Otto()
    assert o.pos == [755.0, 240.0], f"Expected Otto at [755.0, 240.0] on respawn, got {o.pos}"
    print("  -> Respawn on current level correctly preserves Otto spawn at maze entrance!")

if __name__ == "__main__":
    test_initial_level_otto_spawn()
    test_all_exit_entry_sides_otto_spawn()
    test_respawn_preserves_otto_spawn_location()
    print("\nALL OTTO SPAWN TESTS PASSED SUCCESSFULLY (100%)!")
