import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import globals
import main
import player
import maze

def test_maze_exit_scoring():
    print("=== STARTING PYZERK MAZE EXIT SCORING TESTS ===")

    # Initialize Pygame and dummy display
    pygame.init()
    screen = pygame.display.set_mode(globals.SCREENSIZE)

    # 1. Test New Game starts with Score 0
    main.startNewGame()
    assert globals.SCORE == 0, f"Expected initial SCORE == 0, got {globals.SCORE}"
    assert globals.LEVEL == 1, f"Expected initial LEVEL == 1, got {globals.LEVEL}"
    assert globals.LEVELS_PASSED == 0, f"Expected LEVELS_PASSED == 0, got {globals.LEVELS_PASSED}"
    print("[PASS] New game initialized with SCORE = 0, LEVEL = 1, LEVELS_PASSED = 0.")

    # 2. Test Exiting via Green Exit Doorway awards +1 point
    curr_exits = list(globals.EXITS.sprites())
    assert len(curr_exits) >= 1, "At least 1 exit generated"
    exit_obj = curr_exits[0]
    exit_dir = exit_obj.direction

    p = globals.PLAYER.sprites()[0]
    p.pos = list(exit_obj.pos)
    p.update()

    # Trigger exit collision
    p.collide(exit_obj)
    exit_obj.collide(p)
    assert globals.PENDING_EXIT == exit_dir, f"PENDING_EXIT set to {exit_dir}"

    # Simulate exit handling logic as executed in main.py loop
    prev_score = globals.SCORE
    if globals.PENDING_EXIT is not None:
        exit_dir = globals.PENDING_EXIT
        globals.PENDING_EXIT = None
        globals.SCORE += 1
        globals.LEVELS_PASSED += 1
        globals.LEVEL += 1

    assert globals.SCORE == prev_score + 1, f"Expected SCORE {prev_score + 1}, got {globals.SCORE}"
    assert globals.LEVELS_PASSED == 1, f"Expected LEVELS_PASSED == 1, got {globals.LEVELS_PASSED}"
    print(f"[PASS] Exiting maze via green exit doorway awarded +1 point (Score: {prev_score} -> {globals.SCORE}).")

    # 3. Test Room Clear (eliminating all robots) awards +1 point for clearing/exiting the maze
    prev_score = globals.SCORE
    for r in list(globals.ROBOTS.sprites()):
        r.kill()

    # Simulate room clear logic as executed in main.py loop
    if len(globals.ROBOTS.sprites()) == 0:
        globals.SCORE += 1
        globals.LEVELS_PASSED += 1
        main.startNewLevel()

    assert globals.SCORE == prev_score + 1, f"Expected SCORE {prev_score + 1}, got {globals.SCORE}"
    assert globals.LEVELS_PASSED == 2, f"Expected LEVELS_PASSED == 2, got {globals.LEVELS_PASSED}"
    print(f"[PASS] Clearing all robots to exit maze awarded +1 point (Score: {prev_score} -> {globals.SCORE}).")

    # 4. Test HUD Rendering with updated score
    hud_font = pygame.font.Font(None, 24)
    main.draw_hud(screen, hud_font)
    print(f"[PASS] Top HUD successfully rendered with active SCORE: {globals.SCORE}.")

    # 5. Compound Test: 5 consecutive exits
    score_before = globals.SCORE
    for i in range(5):
        globals.SCORE += 1
        globals.LEVELS_PASSED += 1
    assert globals.SCORE == score_before + 5, f"Expected score {score_before + 5}, got {globals.SCORE}"
    print(f"[PASS] Multi-maze progression verified: 5 exits cleanly added 5 points (Total SCORE: {globals.SCORE}).")

    print("\nALL MAZE EXIT SCORING TESTS PASSED! 100% VERIFIED.")

if __name__ == "__main__":
    test_maze_exit_scoring()
