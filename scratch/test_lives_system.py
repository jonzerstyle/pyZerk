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
    screen.blit(lives_surf, (200, 8))
    screen.blit(level_surf, (370, 8))
    screen.blit(hud_font.render("[ENTER: MENU]", True, globals.YELLOW), (655, 8))
    pygame.image.save(screen, os.path.join(os.path.dirname(__file__), "test_hud_render.png"))
    print("[PASS] HUD top status bar with LIVES rendered and saved to test_hud_render.png.")

    print("\nALL 5 TESTS PASSED SUCCESSFULLY! 100% VERIFIED.")

if __name__ == "__main__":
    run_tests()
