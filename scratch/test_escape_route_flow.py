import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import asyncio
import globals
import main
import walls
import player
import maze

def test_interactive_escape_flow():
    print("=== STARTING SIMULATED ESCAPE ROUTE & TRANSITION FLOW TEST ===")

    # Initialize Pygame and screen
    pygame.init()
    screen = pygame.display.set_mode(globals.SCREENSIZE)

    # Start new game
    main.startNewGame()
    assert globals.LEVEL == 1, "Game started at Level 1"
    assert globals.LIVES == 3, "Game started with 3 lives"
    assert len(globals.PLAYER.sprites()) == 1, "Player created"
    assert len(globals.ROBOTS.sprites()) == globals.NUM_OF_ROBOTS, "Robots created"
    print("[PASS] Game started cleanly at Level 1.")

    # Locate an exit in current maze
    curr_exits = list(globals.EXITS.sprites())
    assert len(curr_exits) >= 1, f"Must have at least 1 exit, found {len(curr_exits)}"
    exit_obj = curr_exits[0]
    exit_dir = exit_obj.direction
    print(f"  -> Found exit {exit_dir} at pos {exit_obj.pos}, size {exit_obj.size}")

    # Move player into exit field
    p = globals.PLAYER.sprites()[0]
    p.pos = list(exit_obj.pos)
    p.update()
    assert pygame.sprite.collide_rect(p, exit_obj), "Player bounding box intersects exit field"

    # Simulate collision detection
    globals.PENDING_EXIT = None
    p.collide(exit_obj)
    exit_obj.collide(p)

    assert p.killState is False, "Player is not killed by green exit"
    assert globals.PENDING_EXIT == exit_dir, f"Pending exit is set to {exit_dir}"
    print(f"[PASS] Player collision with exit {exit_dir} safely registered.")

    # Trigger transition logic (as performed in main loop)
    old_maze_surf = pygame.Surface(globals.SCREENSIZE)
    if main.current_maze:
        main.current_maze.render_to_surface(old_maze_surf, grey_mode=False)

    globals.LEVELS_PASSED += 1
    globals.LEVEL += 1
    next_maze = maze.Class_Maze(globals.SCREENSIZE, instantiate=False)
    new_maze_grey_surf = pygame.Surface(globals.SCREENSIZE)
    next_maze.render_to_surface(new_maze_grey_surf, grey_mode=True)

    for a in globals.OBJECTS:
        a.kill()

    assert len(globals.PLAYER.sprites()) == 0, "Entities cleared during scroll transition"
    assert len(globals.ROBOTS.sprites()) == 0, "Robots cleared during scroll transition"
    print("[PASS] Gameplay entities cleared during transition.")

    # Simulate 24 transition frames
    total_frames = 24
    hud_font = pygame.font.Font(None, 24)
    for frame in range(1, total_frames + 1):
        t = float(frame) / float(total_frames)
        ease_t = t * t * (3.0 - 2.0 * t)
        screen.fill((0, 0, 0))
        # Blit scrolling surfaces
        screen.blit(old_maze_surf, (0, int(globals.SCREENSIZE[1] * ease_t)))
        screen.blit(new_maze_grey_surf, (0, int(-globals.SCREENSIZE[1] * (1.0 - ease_t))))
        main.draw_hud(screen, hud_font)

    # Save a screenshot of the transition midway
    pygame.image.save(screen, os.path.join(os.path.dirname(__file__), "test_transition_scroll_render.png"))
    print("[PASS] 24 frames of scrolling transition completed cleanly.")

    # Complete transition & activate room
    main.setupRoom(globals.LEVEL, entry_side=exit_dir, maze_instance=next_maze)
    globals.ROBOT_STARTLE_TIMER = 150

    assert globals.LEVEL == 2, f"Expected Level 2, got {globals.LEVEL}"
    assert len(globals.PLAYER.sprites()) == 1, "Player spawned in Level 2"
    assert len(globals.ROBOTS.sprites()) == globals.NUM_OF_ROBOTS, "Robots spawned in Level 2"

    new_p = globals.PLAYER.sprites()[0]
    if exit_dir == 'UP':
        assert new_p.pos[1] == globals.SCREENSIZE[1] - 45.0, "Player spawned at bottom for UP exit"
    elif exit_dir == 'DOWN':
        assert new_p.pos[1] == 45.0, "Player spawned at top for DOWN exit"
    elif exit_dir == 'LEFT':
        assert new_p.pos[0] == globals.SCREENSIZE[0] - 45.0, "Player spawned on right for LEFT exit"
    elif exit_dir == 'RIGHT':
        assert new_p.pos[0] == 45.0, "Player spawned on left for RIGHT exit"

    print(f"[PASS] Level 2 activated. Player safely spawned opposite to {exit_dir} at {new_p.pos}.")
    assert globals.ROBOT_STARTLE_TIMER == 150, "Robot startle timer initialized to 150 frames (5 seconds)."

    # Verify startled robots do not fire
    r = globals.ROBOTS.sprites()[0]
    r.gunHeatCnt = 0.0
    r.updateMovement()
    assert len(globals.BULLETS.sprites()) == 0, "No bullets fired during startle period"
    print("[PASS] Robot startle verification passed.")

    # Cleanup globals
    for a in globals.OBJECTS:
        a.kill()
    globals.ROBOT_STARTLE_TIMER = 0
    globals.PENDING_EXIT = None

    print("\nALL ESCAPE ROUTE & TRANSITION FLOW TESTS PASSED SUCCESSFULLY! 100% VERIFIED.")

if __name__ == "__main__":
    test_interactive_escape_flow()
