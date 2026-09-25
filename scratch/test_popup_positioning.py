#!/usr/bin/env python3
"""
Test Suite: Status Popup Dynamic Top/Bottom Positioning
Verifies that status messages / popups (robot startle, loop milestone, bonus life)
appear at the bottom of the screen when the player enters the maze at the top
(or is near the top), completely avoiding obscuring the player character.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import globals
import main
import player
import walls

def setup_test_env():
    pygame.init()
    screen = pygame.display.set_mode(globals.SCREENSIZE)
    globals.FPS = 30
    globals.SOUNDS_ON = False
    return screen

def run_tests():
    screen = setup_test_env()
    banner_font = pygame.font.Font(None, 28)
    print("=== STARTING STATUS POPUP POSITIONING TESTS ===")

    # Case 1: Player enters maze at TOP (entry_side='DOWN', spawn at [400, 45])
    print("\n--- 1. Testing Player Entering at TOP ---")
    main.setupRoom(1, entry_side='DOWN')
    p = globals.PLAYER.sprites()[0]
    assert p.pos[1] < 100, f"Expected player near top (y < 100), got {p.pos[1]}"
    assert main.current_entry_side == 'DOWN', f"Expected current_entry_side=='DOWN', got {main.current_entry_side}"

    is_player_at_top = (main.current_entry_side == 'DOWN') or (
        len(globals.PLAYER.sprites()) > 0 and globals.PLAYER.sprites()[0].pos[1] < 120
    )
    assert is_player_at_top is True, "is_player_at_top must be True when player enters at TOP!"

    # Render banner with is_bottom=True
    screen.fill(globals.SCREEN_BACKCOLOR)
    rect = main.draw_status_banner(screen, banner_font, "★ ROBOTS STARTLED! NO FIRING (5s) ★", (0, 255, 200), (0, 230, 80), (10, 25, 20), is_bottom=True)
    assert rect.top > 400, f"Banner must be rendered at bottom (top > 400), got {rect.top}"
    # Verify banner does NOT overlap player at y=45
    assert not rect.colliderect(p.rect), f"Banner {rect} MUST NOT overlap player {p.rect}!"
    print(f"[PASS] Banner rendered at BOTTOM (y={rect.top}), player at y={p.rect.top}. No overlap!")
    pygame.image.save(screen, os.path.join(os.path.dirname(__file__), "test_popup_bottom_render.png"))

    # Case 2: Player enters maze at BOTTOM (entry_side='UP', spawn at [400, 435])
    print("\n--- 2. Testing Player Entering at BOTTOM ---")
    main.setupRoom(1, entry_side='UP')
    p = globals.PLAYER.sprites()[0]
    assert p.pos[1] > 400, f"Expected player near bottom (y > 400), got {p.pos[1]}"
    assert main.current_entry_side == 'UP', f"Expected current_entry_side=='UP', got {main.current_entry_side}"

    is_player_at_top = (main.current_entry_side == 'DOWN') or (
        len(globals.PLAYER.sprites()) > 0 and globals.PLAYER.sprites()[0].pos[1] < 120
    )
    assert is_player_at_top is False, "is_player_at_top must be False when player enters at BOTTOM!"

    # Render banner with is_bottom=False
    screen.fill(globals.SCREEN_BACKCOLOR)
    rect = main.draw_status_banner(screen, banner_font, "★ ROBOTS STARTLED! NO FIRING (5s) ★", (0, 255, 200), (0, 230, 80), (10, 25, 20), is_bottom=False)
    assert rect.top < 60, f"Banner must be rendered at top (top < 60), got {rect.top}"
    assert not rect.colliderect(p.rect), f"Banner {rect} MUST NOT overlap player {p.rect}!"
    print(f"[PASS] Banner rendered at TOP (y={rect.top}), player at y={p.rect.top}. No overlap!")
    pygame.image.save(screen, os.path.join(os.path.dirname(__file__), "test_popup_top_render.png"))

    # Case 3: Player enters on LEFT / RIGHT
    print("\n--- 3. Testing Player Entering on LEFT & RIGHT ---")
    for side, expected_spawn_x in [('RIGHT', 45.0), ('LEFT', 755.0)]:
        main.setupRoom(1, entry_side=side)
        p = globals.PLAYER.sprites()[0]
        assert abs(p.pos[0] - expected_spawn_x) < 5
        is_player_at_top = (main.current_entry_side == 'DOWN') or (
            len(globals.PLAYER.sprites()) > 0 and globals.PLAYER.sprites()[0].pos[1] < 120
        )
        assert is_player_at_top is False
        rect = main.draw_status_banner(screen, banner_font, "★ 10 LEVELS PASSED! +1 EXTRA LIFE! ★", (255, 230, 0), (255, 220, 0), (10, 25, 15), is_bottom=is_player_at_top)
        assert rect.top < 60
        assert not rect.colliderect(p.rect)
        print(f"[PASS] Entry {side}: Banner at top (y={rect.top}), player at x={p.rect.left}, y={p.rect.top}. No overlap!")

    # Case 4: Respawn preserves current_entry_side
    print("\n--- 4. Testing Respawn Preserves Entry Side ---")
    main.setupRoom(2, entry_side='DOWN')
    assert main.current_entry_side == 'DOWN'
    main.respawnCurrentLevel()
    assert main.current_entry_side == 'DOWN', f"Respawn must keep current_entry_side=='DOWN', got {main.current_entry_side}"
    p = globals.PLAYER.sprites()[0]
    assert p.pos[1] < 100, "Respawn must keep player at top spawn position"
    print("[PASS] Respawn preserves top entrance positioning and status popup placement.")

    print("\nALL STATUS POPUP POSITIONING TESTS PASSED! 100% VERIFIED.")

if __name__ == '__main__':
    run_tests()
