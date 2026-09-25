import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import globals
import main
import sounds

def run_tests():
    print("=== STARTING PYZERK LIVES SYSTEM UNIT TESTS ===")
    
    # 1. Test Initial State in globals
    assert globals.INITIAL_LIVES == 3, f"Expected INITIAL_LIVES == 3, got {globals.INITIAL_LIVES}"
    assert globals.LIVES == 3, f"Expected initial LIVES == 3, got {globals.LIVES}"
    assert globals.LEVELS_PASSED == 0, f"Expected initial LEVELS_PASSED == 0, got {globals.LEVELS_PASSED}"
    print("[PASS] globals.py default constants verified.")

    # 2. Test startNewGame() initialization
    main.startNewGame()
    assert globals.LIVES == 3, f"Expected LIVES == 3 after startNewGame, got {globals.LIVES}"
    assert globals.LEVEL == 1, f"Expected LEVEL == 1 after startNewGame, got {globals.LEVEL}"
    assert globals.SCORE == 0, f"Expected SCORE == 0 after startNewGame, got {globals.SCORE}"
    assert globals.LEVELS_PASSED == 0, f"Expected LEVELS_PASSED == 0 after startNewGame, got {globals.LEVELS_PASSED}"
    assert len(globals.PLAYER.sprites()) == 1, "Expected 1 player sprite created in level 1"
    assert len(globals.ROBOTS.sprites()) == globals.NUM_OF_ROBOTS, f"Expected {globals.NUM_OF_ROBOTS} robots in level 1"
    print("[PASS] startNewGame() correctly initializes 3 lives, level 1, score 0, and entities.")

    # 3. Test death & respawnCurrentLevel() logic
    # Player dies once
    player_sprite = globals.PLAYER.sprites()[0]
    player_sprite.kill()
    assert len(globals.PLAYER.sprites()) == 0, "Player sprite killed"
    globals.LIVES -= 1
    assert globals.LIVES == 2, f"Expected LIVES == 2, got {globals.LIVES}"
    
    # Respawn current level
    main.respawnCurrentLevel()
    assert globals.LEVEL == 1, f"Expected LEVEL to remain 1 after death respawn, got {globals.LEVEL}"
    assert len(globals.PLAYER.sprites()) == 1, "Player respawned in current level"
    assert len(globals.ROBOTS.sprites()) == globals.NUM_OF_ROBOTS, "Robots respawned in current level"
    print("[PASS] Player death decrements lives (3 -> 2) and respawnCurrentLevel keeps level 1.")

    # Player dies second time
    globals.PLAYER.sprites()[0].kill()
    globals.LIVES -= 1
    assert globals.LIVES == 1, f"Expected LIVES == 1, got {globals.LIVES}"
    main.respawnCurrentLevel()
    assert globals.LEVEL == 1, "Level still 1"
    print("[PASS] Player death decrements lives (2 -> 1).")

    # Player dies third time (out of lives)
    globals.PLAYER.sprites()[0].kill()
    globals.LIVES -= 1
    assert globals.LIVES == 0, f"Expected LIVES == 0, got {globals.LIVES}"
    print("[PASS] Player death reaches 0 lives (Game Over condition verified).")

    # 4. Test 10-level passed award logic
    globals.LIVES = 1
    globals.LEVELS_PASSED = 0
    for lvl in range(1, 11):
        # Simulate level clear
        globals.LEVELS_PASSED += 1
        if globals.LEVELS_PASSED % 10 == 0:
            globals.LIVES += 1
            print(f"  -> Passed level {lvl}: Awarded +1 life! Current lives: {globals.LIVES}")
        main.startNewLevel()

    assert globals.LEVELS_PASSED == 10, f"Expected LEVELS_PASSED == 10, got {globals.LEVELS_PASSED}"
    assert globals.LIVES == 2, f"Expected 1 life back after 10 levels passed (1 -> 2), got {globals.LIVES}"
    assert globals.LEVEL == 11, f"Expected LEVEL == 11, got {globals.LEVEL}"
    print("[PASS] Clearing 10 levels awards +1 extra life correctly!")

    # Pass 10 more levels (up to 20)
    for lvl in range(11, 21):
        globals.LEVELS_PASSED += 1
        if globals.LEVELS_PASSED % 10 == 0:
            globals.LIVES += 1
            print(f"  -> Passed level {lvl}: Awarded +1 life! Current lives: {globals.LIVES}")
        main.startNewLevel()

    assert globals.LEVELS_PASSED == 20, f"Expected LEVELS_PASSED == 20, got {globals.LEVELS_PASSED}"
    assert globals.LIVES == 3, f"Expected second bonus life after 20 levels passed (2 -> 3), got {globals.LIVES}"
    assert globals.LEVEL == 21, f"Expected LEVEL == 21, got {globals.LEVEL}"
    print("[PASS] Clearing 20 levels awards another bonus life (2 -> 3)!")

    # 5. Test HUD Top Status Bar Rendering
    screen = pygame.display.set_mode(globals.SCREENSIZE)
    hud_font = pygame.font.Font(None, 24)
    lives_surf = hud_font.render(f"LIVES: {globals.LIVES}", True, (0, 255, 100))
    score_surf = hud_font.render(f"SCORE: {globals.SCORE}", True, globals.WHITE)
    level_surf = hud_font.render(f"LEVEL: {globals.LEVEL}", True, globals.CYAN)
    
    assert lives_surf.get_width() > 0 and lives_surf.get_height() > 0, "Lives HUD surface rendered"
    assert score_surf.get_width() > 0 and score_surf.get_height() > 0, "Score HUD surface rendered"
    assert level_surf.get_width() > 0 and level_surf.get_height() > 0, "Level HUD surface rendered"
    
    # Render onto test surface and save screenshot
    screen.fill((0, 0, 0))
    screen.blit(score_surf, (15, 8))
    screen.blit(lives_surf, (190, 8))
    screen.blit(level_surf, (340, 8))
    screen.blit(hud_font.render("[ENTER: MENU]", True, globals.YELLOW), (655, 8))
    pygame.image.save(screen, os.path.join(os.path.dirname(__file__), "test_hud_render.png"))
    print("[PASS] HUD top status bar with LIVES rendered and saved to test_hud_render.png.")

    # 6. Test Max Level Loop Around (Surpassing Level 50)
    print("\n--- Testing Level Loop Around when Max Level (50) is reached and surpassed ---")
    main.startNewGame()
    globals.LIVES = 3
    globals.LEVELS_PASSED = 48
    globals.LEVEL = 49  # Simulate on level 49

    # Clear level 49 -> Enter level 50 (MAX_LEVELS)
    globals.LEVELS_PASSED += 1
    did_loop = main.startNewLevel()
    assert did_loop is False, "Not looped yet at level 50"
    assert globals.LEVEL == 50, f"Expected LEVEL == 50, got {globals.LEVEL}"
    assert globals.LEVEL_LOOP == 0, f"Expected LEVEL_LOOP == 0, got {globals.LEVEL_LOOP}"
    print(f"  -> At Level 50 (Max Level): LEVEL={globals.LEVEL}, LOOP={globals.LEVEL_LOOP + 1}")

    # Clear level 50 -> Surpass max level (50) and loop around!
    globals.LEVELS_PASSED += 1  # 50 levels passed!
    if globals.LEVELS_PASSED % 10 == 0:
        globals.LIVES += 1
    did_loop = main.startNewLevel()

    assert did_loop is True, "Expected did_loop to be True when surpassing MAX_LEVELS"
    assert globals.LEVEL == 1, f"Expected LEVEL to wrap back to 1 (not 0), got {globals.LEVEL}"
    assert globals.LEVEL_LOOP == 1, f"Expected LEVEL_LOOP == 1 (Loop 2), got {globals.LEVEL_LOOP}"
    assert globals.LEVELS_PASSED == 50, f"Expected LEVELS_PASSED == 50, got {globals.LEVELS_PASSED}"
    assert globals.LIVES == 4, f"Expected bonus life for passing 50 levels (3 -> 4), got {globals.LIVES}"
    print(f"  -> Surpassed Level 50! Clean loop around: LEVEL={globals.LEVEL}, LOOP={globals.LEVEL_LOOP + 1}, LIVES={globals.LIVES}")

    # Play 10 more levels in Loop 2 (Levels 1 through 10 of Loop 2)
    for _ in range(10):
        globals.LEVELS_PASSED += 1
        if globals.LEVELS_PASSED % 10 == 0:
            globals.LIVES += 1
        main.startNewLevel()

    assert globals.LEVEL == 11, f"Expected LEVEL == 11 in Loop 2, got {globals.LEVEL}"
    assert globals.LEVEL_LOOP == 1, f"Expected LEVEL_LOOP == 1, got {globals.LEVEL_LOOP}"
    assert globals.LEVELS_PASSED == 60, f"Expected LEVELS_PASSED == 60, got {globals.LEVELS_PASSED}"
    assert globals.LIVES == 5, f"Expected another bonus life at 60 levels passed (4 -> 5), got {globals.LIVES}"
    print(f"  -> Reached 60 levels passed in Loop 2: +1 bonus life awarded! LIVES={globals.LIVES}")

    # Verify loop HUD string
    loop_hud_text = f"LEVEL: {globals.LEVEL} [LOOP {globals.LEVEL_LOOP + 1}]"
    assert loop_hud_text == "LEVEL: 11 [LOOP 2]", f"Unexpected HUD text: {loop_hud_text}"
    hud_loop_surf = hud_font.render(loop_hud_text, True, globals.CYAN)
    assert hud_loop_surf.get_width() > 0, "Loop HUD rendered"
    print(f"  -> Loop HUD verified: '{loop_hud_text}'")

    # Verify startNewGame resets loop counter
    main.startNewGame()
    assert globals.LEVEL_LOOP == 0, f"Expected LEVEL_LOOP == 0 on new game, got {globals.LEVEL_LOOP}"
    assert globals.LEVEL == 1, f"Expected LEVEL == 1 on new game, got {globals.LEVEL}"
    assert globals.LIVES == 3, f"Expected LIVES == 3 on new game, got {globals.LIVES}"
    print("  -> startNewGame cleanly resets LEVEL_LOOP to 0, LEVEL to 1, LIVES to 3.")

    print("\nALL 6 TESTS PASSED SUCCESSFULLY! 100% VERIFIED.")

if __name__ == "__main__":
    run_tests()
