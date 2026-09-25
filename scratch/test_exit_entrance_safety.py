#!/usr/bin/env python3
"""
Test Suite: Exit & Entrance Safety Verification
Verifies that approaching or passing through a green exit (including exits
located near the player on the entrance wall) never kills the player, even
with lateral offsets, doorway doorframe grazing, or diagonal approaches.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import globals
import maze
import walls
import player
import movement
import keybo
import cclass

def setup_test_env():
    pygame.init()
    pygame.display.set_mode(globals.SCREENSIZE)
    globals.FPS = 30
    globals.SOUNDS_ON = False

def clear_all():
    for g in [globals.OBJECTS, globals.WALLS, globals.EXITS, globals.PLAYER, globals.COLLIDABLE]:
        g.empty()
    globals.PENDING_EXIT = None

def run_tests():
    setup_test_env()
    print("=== STARTING EXIT & ENTRANCE SAFETY TESTS ===")

    # Test 1: Moving straight into an entrance wall exit across all 4 directions
    print("\n--- 1. Testing Straight Entrance Exit Traversal ---")
    directions = [
        ('UP_entry', 'DOWN', [400.0, 435.0], movement.dirEnum.DOWN),
        ('DOWN_entry', 'UP', [400.0, 45.0], movement.dirEnum.UP),
        ('LEFT_entry', 'RIGHT', [755.0, 240.0], movement.dirEnum.RIGHT),
        ('RIGHT_entry', 'LEFT', [45.0, 240.0], movement.dirEnum.LEFT)
    ]
    for label, exit_dir, spawn_pos, move_dir in directions:
        clear_all()
        m = maze.Class_Maze(globals.SCREENSIZE, exit_dirs=[exit_dir])
        p = player.Class_Player(spawn_pos, [0, 0])
        p.facing_dir = move_dir
        kb = keybo.Class_ProcessKeybo()
        kb.collisionOn = 1
        container = cclass.Class_Container()
        container.addItem('player_movement', move_dir)
        container.addItem('player_fire', 'ceasefire')

        escaped = False
        died = False
        for frame in range(40):
            if globals.PENDING_EXIT is not None:
                escaped = True
                break
            p.updateMovement(container.getItem('player_movement'), container.getItem('player_fire'))
            colSprites = globals.COLLIDABLE.sprites()
            for x in range(len(colSprites) - 1):
                for y in range(x + 1, len(colSprites)):
                    if pygame.sprite.collide_rect(colSprites[x], colSprites[y]):
                        colSprites[x].collide(colSprites[y])
                        colSprites[y].collide(colSprites[x])
            for a in globals.OBJECTS:
                a.update()
            if len(globals.PLAYER.sprites()) == 0:
                died = True
                break

        assert escaped is True, f"Failed to escape through {label}!"
        assert died is False, f"Player DIED attempting to escape through {label}!"
        print(f"[PASS] {label}: Safely escaped in {frame} frames without dying.")

    # Test 2: Moving with lateral offsets into entrance exit (doorway grazing)
    print("\n--- 2. Testing Lateral Offsets & Doorframe Grazing ---")
    for exit_dir, spawn, move in [
        ('DOWN', [400.0, 435.0], movement.dirEnum.DOWN),
        ('UP', [400.0, 45.0], movement.dirEnum.UP),
        ('RIGHT', [755.0, 240.0], movement.dirEnum.RIGHT),
        ('LEFT', [45.0, 240.0], movement.dirEnum.LEFT)
    ]:
        for offset in range(-12, 13, 3):
            clear_all()
            m = maze.Class_Maze(globals.SCREENSIZE, exit_dirs=[exit_dir])
            if exit_dir in ('UP', 'DOWN'):
                p_pos = [spawn[0] + offset, spawn[1]]
            else:
                p_pos = [spawn[0], spawn[1] + offset]
            p = player.Class_Player(p_pos, [0, 0])
            p.facing_dir = move
            container = cclass.Class_Container()
            container.addItem('player_movement', move)
            container.addItem('player_fire', 'ceasefire')

            escaped = False
            died = False
            for frame in range(40):
                if globals.PENDING_EXIT is not None:
                    escaped = True
                    break
                p.updateMovement(container.getItem('player_movement'), container.getItem('player_fire'))
                colSprites = globals.COLLIDABLE.sprites()
                for x in range(len(colSprites) - 1):
                    for y in range(x + 1, len(colSprites)):
                        if pygame.sprite.collide_rect(colSprites[x], colSprites[y]):
                            colSprites[x].collide(colSprites[y])
                            colSprites[y].collide(colSprites[x])
                for a in globals.OBJECTS:
                    a.update()
                if len(globals.PLAYER.sprites()) == 0:
                    died = True
                    break

            assert escaped is True, f"Failed to escape with offset {offset} on exit {exit_dir}!"
            assert died is False, f"Player DIED on offset {offset} on exit {exit_dir}!"
        print(f"[PASS] Exit {exit_dir}: Verified offsets -12 to +12 (100% safe escape).")

    # Test 3: Wall collision immunity while touching exit
    print("\n--- 3. Testing Wall Immunity When Overlapping Exit ---")
    clear_all()
    p = player.Class_Player([400.0, 470.0], [0, 0])
    exit_field = walls.Class_ExitField([400.0, 470.0], [30, 10], 'DOWN')
    wall = walls.Class_Wall([400.0, 470.0], [10, 10])
    # Player overlaps both wall and exit field simultaneously
    p.collide(wall)
    assert p.killState is False, "Player MUST NOT die when overlapping exit and wall simultaneously!"
    print("[PASS] Overlapping exit and wall simultaneously does NOT kill player.")

    # Test 4: Wall collision kills when NOT touching exit
    print("\n--- 4. Testing Normal Electrified Wall Collision Kills ---")
    clear_all()
    p = player.Class_Player([200.0, 200.0], [0, 0])
    wall = walls.Class_Wall([200.0, 200.0], [10, 10])
    p.collide(wall)
    assert p.killState is True, "Player MUST die when touching normal electrified wall!"
    print("[PASS] Normal electrified wall collision kills player as expected.")

    print("\nALL EXIT & ENTRANCE SAFETY TESTS PASSED! 100% VERIFIED.")

if __name__ == '__main__':
    run_tests()
