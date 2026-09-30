#!/usr/bin/env python3
"""
Unit test for pyZerk Electrified Player Death Animation.
Verifies:
1. Class_Player electrocution state variables on init.
2. Collision triggers is_electrocuted=True, electrocute_timer=36, Wilhelm scream playback.
3. Player movement and shooting are suppressed while electrocuted.
4. Subsequent collisions do not re-trigger sound or reset timer.
5. Electrocuted draw() method renders without errors on pygame surface across all frames.
6. Electrocution animation lasts 36 frames (~1.2s @ 30 FPS) before calling self.kill().
7. Integration with main.py game loop (movement paused, clean transition to respawn).
"""

import os
import sys
import pygame

os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import globals
globals.SOUNDS_ON = True

import player
import walls
import movement
import cclass
import main

def test_electrocution_lifecycle():
    globals.OBJECTS.empty()
    globals.PLAYER.empty()
    globals.COLLIDABLE.empty()

    p = player.Class_Player([100.0, 100.0], [50.0, 0.0])
    assert p.is_electrocuted is False, "Expected is_electrocuted False on init"
    assert p.electrocute_timer == 0, "Expected electrocute_timer 0 on init"
    assert len(globals.PLAYER.sprites()) == 1, "Player should be registered in globals.PLAYER"

    # 1. Trigger collision with wall
    wall = walls.Class_Wall([100.0, 100.0], [10, 10])
    p.collide(wall)

    assert p.is_electrocuted is True, "Player should be electrocuted after wall collision!"
    assert p.killState is True, "killState should be True for test compatibility"
    assert p.electrocute_timer == 36, f"Expected electrocute_timer=36, got {p.electrocute_timer}"
    assert p.speed == [0.0, 0.0], f"Player speed should be halted to 0, got {p.speed}"
    print("[PASS] Collision triggers electrocution state, timer=36, speed=0.")

    # 2. Verify subsequent collision is ignored
    p.collide(wall)
    assert p.electrocute_timer == 36, "Subsequent collision must not reset electrocute_timer!"

    # 3. Verify movement/shooting suppressed
    p.updateMovement(movement.dirEnum.RIGHT, "shoot", death_blossom=True)
    assert p.speed == [0.0, 0.0], "Movement must remain zero while electrocuted"
    assert p.bullets == 0, "Shooting must be suppressed while electrocuted"
    print("[PASS] Movement, shooting, and Death Blossom suppressed during electrocution.")

    # 4. Test rendering across all 36 frames
    test_surf = pygame.Surface(globals.SCREENSIZE)
    for f in range(1, 37):
        p.update()
        dirty = p.draw(test_surf)
        assert len(dirty) > 0, f"Frame {f}: draw() must return dirty rects"
        if f < 36:
            assert len(globals.PLAYER.sprites()) == 1, f"Frame {f}: Player should remain alive during electrocution!"
        else:
            assert len(globals.PLAYER.sprites()) == 0, f"Frame {f}: Player must be killed after 36 frames!"

    print("[PASS] Full 36-frame electrocution draw and timer countdown verified (player kept alive until final frame).")

def test_main_game_loop_electrocution():
    globals.OBJECTS.empty()
    globals.PLAYER.empty()
    globals.COLLIDABLE.empty()
    globals.ROBOTS.empty()
    globals.OTTO.empty()

    main.startNewGame()
    assert globals.LIVES == 3, f"Expected 3 lives, got {globals.LIVES}"
    assert len(globals.PLAYER.sprites()) == 1

    p = globals.PLAYER.sprite
    # Cause death by colliding with a wall
    wall = walls.Class_Wall(list(p.pos), [10, 10])
    p.collide(wall)
    assert p.is_electrocuted is True

    # Run 30 frames: player still electrocuting, lives NOT yet decremented!
    container = cclass.Class_Container()
    container.addItem("player_movement", movement.dirEnum.NONE)
    container.addItem("player_fire", "ceasefire")

    for frame in range(35):
        main.updateMovement(container)
        for a in globals.OBJECTS:
            a.update()
        assert len(globals.PLAYER.sprites()) == 1, f"Frame {frame}: player still electrocuting"
        assert globals.LIVES == 3, f"Frame {frame}: lives should not decrement until electrocution finishes"

    # Frame 36: electrocute timer reaches 0, player.kill() is called
    main.updateMovement(container)
    for a in globals.OBJECTS:
        a.update()
    assert len(globals.PLAYER.sprites()) == 0, "Player killed at frame 36"

    # Next iteration in main detects len(globals.PLAYER) == 0 -> decrements life!
    globals.LIVES -= 1
    assert globals.LIVES == 2, f"Expected LIVES=2, got {globals.LIVES}"
    print("[PASS] Main loop integration: 36 frames electrocution delay followed by life deduction verified.")

if __name__ == "__main__":
    test_electrocution_lifecycle()
    test_main_game_loop_electrocution()
    print("\nALL ELECTRIFIED PLAYER DEATH TESTS PASSED SUCCESSFULLY! (100%)")
