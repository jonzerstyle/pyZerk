import os
import sys
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import globals
import main
import maze
import walls
import player
import robots
import bullets

def run_tests():
    print("=== STARTING PYZERK ESCAPE ROUTES & TRANSITION TESTS ===")

    # 1. Test Exit Generation & Bounds (at least 1, up to 4)
    print("\n--- 1. Testing Exit Generation (1 to 4 exits) ---")
    valid_dirs = {'UP', 'DOWN', 'LEFT', 'RIGHT'}
    for i in range(100):
        m = maze.Class_Maze(globals.SCREENSIZE, instantiate=False)
        assert 1 <= len(m.exit_dirs) <= 4, f"Exit count must be between 1 and 4, got {len(m.exit_dirs)}"
        assert set(m.exit_dirs).issubset(valid_dirs), f"Exits must be subset of {valid_dirs}"
        assert len(m.exit_specs) == len(m.exit_dirs), "Number of exit specs must match exit_dirs"
    print("[PASS] 100 maze generation runs verified: 100% have 1 to 4 valid exits.")

    # 1b. Test Entrance Wall Location Allocated Last
    print("\n--- 1b. Testing Entrance Wall Allocated Last ---")
    for test_entry in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
        for _ in range(50):
            m = maze.Class_Maze(globals.SCREENSIZE, instantiate=False, entry_wall=test_entry)
            if len(m.exit_dirs) < 4:
                # When fewer than 4 exits are allocated, the entry wall is NEVER allocated
                assert test_entry not in m.exit_dirs, f"Entry wall {test_entry} must NOT be allocated when exit count is {len(m.exit_dirs)}"
            else:
                # When all 4 exits are allocated, the entry wall is the LAST allocation
                assert m.exit_dirs[-1] == test_entry, f"Entry wall {test_entry} must be the LAST allocation, got {m.exit_dirs}"
    print("[PASS] Entrance wall last allocation rule verified across all 4 entry directions (200 test runs).")

    # 2. Test Green Wall Segment Dimensions (twice the width of the player character)
    print("\n--- 2. Testing Exit Dimensions (twice player character width) ---")
    player_w = player.player_pixel_size[0]  # 15.0
    expected_exit_w = 2.0 * player_w       # 30.0

    all_exits_maze = maze.Class_Maze(globals.SCREENSIZE, exit_dirs=['UP', 'DOWN', 'LEFT', 'RIGHT'], instantiate=False)
    for x, y, w, h, d in all_exits_maze.exit_specs:
        if d in ('UP', 'DOWN'):
            assert w == expected_exit_w, f"Horizontal exit width must be {expected_exit_w}, got {w}"
            assert h == all_exits_maze.wallThickness, f"Exit height must be wallThickness {all_exits_maze.wallThickness}, got {h}"
            # Centered horizontally
            assert abs((x + w / 2.0) - globals.SCREENSIZE[0] / 2.0) < 1.0, f"Exit must be horizontally centered at {globals.SCREENSIZE[0] / 2.0}"
        elif d in ('LEFT', 'RIGHT'):
            assert h == expected_exit_w, f"Vertical exit height must be {expected_exit_w}, got {h}"
            assert w == all_exits_maze.wallThickness, f"Exit width must be wallThickness {all_exits_maze.wallThickness}, got {w}"
            # Centered vertically
            assert abs((y + h / 2.0) - globals.SCREENSIZE[1] / 2.0) < 1.0, f"Exit must be vertically centered at {globals.SCREENSIZE[1] / 2.0}"
    print(f"[PASS] All exit dimensions verified: exactly twice player width ({expected_exit_w}px).")

    # 3. Test Player Collision with Green Exit Field vs Blue Electrified Wall
    print("\n--- 3. Testing Collision Behavior (Green exit is NOT electrified) ---")
    # Clean entity groups
    for a in globals.OBJECTS:
        a.kill()

    test_player = player.Class_Player([400, 240], [0, 0])
    exit_field = walls.Class_ExitField([400, 240], [30, 10], 'UP')

    globals.PENDING_EXIT = None
    # Simulate collision with exit field
    test_player.collide(exit_field)
    exit_field.collide(test_player)

    assert test_player.killState is False, "Player MUST NOT die when touching green exit field!"
    assert globals.PENDING_EXIT == 'UP', f"Expected PENDING_EXIT == 'UP', got {globals.PENDING_EXIT}"
    print("[PASS] Touching green exit field does NOT kill player and flags PENDING_EXIT correctly.")

    # Simulate collision with blue electrified wall
    blue_wall = walls.Class_Wall([400, 240], [10, 10])
    test_player.collide(blue_wall)
    assert test_player.killState is True, "Player MUST die when touching blue electrified wall!"
    print("[PASS] Touching blue electrified wall kills player as expected.")

    # 4. Test Player Spawn Position on Opposite Side of New Maze
    print("\n--- 4. Testing Player Spawn Opposite to Exit Direction ---")
    for a in globals.OBJECTS:
        a.kill()

    # Case A: Exit UP -> Spawn at Bottom
    main.setupRoom(1, entry_side='UP')
    p = globals.PLAYER.sprites()[0]
    assert p.pos[0] == globals.SCREENSIZE[0] / 2.0, f"Expected X at center, got {p.pos[0]}"
    assert p.pos[1] == globals.SCREENSIZE[1] - 45.0, f"Expected Y near bottom (435), got {p.pos[1]}"
    print("[PASS] Exit 'UP' -> Player correctly spawned at bottom of next maze.")

    # Case B: Exit DOWN -> Spawn at Top
    for a in globals.OBJECTS:
        a.kill()
    main.setupRoom(1, entry_side='DOWN')
    p = globals.PLAYER.sprites()[0]
    assert p.pos[0] == globals.SCREENSIZE[0] / 2.0
    assert p.pos[1] == 45.0, f"Expected Y near top (45), got {p.pos[1]}"
    print("[PASS] Exit 'DOWN' -> Player correctly spawned at top of next maze.")

    # Case C: Exit LEFT -> Spawn on Right
    for a in globals.OBJECTS:
        a.kill()
    main.setupRoom(1, entry_side='LEFT')
    p = globals.PLAYER.sprites()[0]
    assert p.pos[0] == globals.SCREENSIZE[0] - 45.0, f"Expected X near right (755), got {p.pos[0]}"
    assert p.pos[1] == globals.SCREENSIZE[1] / 2.0
    print("[PASS] Exit 'LEFT' -> Player correctly spawned on right of next maze.")

    # Case D: Exit RIGHT -> Spawn on Left
    for a in globals.OBJECTS:
        a.kill()
    main.setupRoom(1, entry_side='RIGHT')
    p = globals.PLAYER.sprites()[0]
    assert p.pos[0] == 45.0, f"Expected X near left (45), got {p.pos[0]}"
    assert p.pos[1] == globals.SCREENSIZE[1] / 2.0
    print("[PASS] Exit 'RIGHT' -> Player correctly spawned on left of next maze.")

    # 5. Test Robot 5-Second Startle Period (Move but Cannot Fire)
    print("\n--- 5. Testing Robot 5-Second Startle Period ---")
    for a in globals.OBJECTS:
        a.kill()
    test_robot = robots.Class_Robot([200, 200], [0, 0])
    test_robot.gunHeatCnt = 0.0
    initial_bullets = len(globals.BULLETS.sprites())

    # Set startle timer active
    globals.ROBOT_STARTLE_TIMER = 150  # 5 seconds @ 30 FPS
    test_robot.updateMovement()
    assert len(globals.BULLETS.sprites()) == initial_bullets, "Robot must NOT fire while startle timer is active!"
    print("[PASS] Robot did NOT fire while ROBOT_STARTLE_TIMER > 0.")

    # Startle timer expired -> Robot can fire
    globals.ROBOT_STARTLE_TIMER = 0
    test_robot.gunHeatCnt = 0.0
    test_robot.updateMovement()
    assert len(globals.BULLETS.sprites()) == initial_bullets + 1, "Robot can fire once startle timer expires."
    print("[PASS] Robot successfully fires when ROBOT_STARTLE_TIMER == 0.")

    # 6. Test Surface Rendering & Grey Wall Transition Mode
    print("\n--- 6. Testing Surface Rendering (Normal Blue/Green vs Grey Transition) ---")
    test_maze = maze.Class_Maze(globals.SCREENSIZE, exit_dirs=['UP', 'DOWN', 'LEFT', 'RIGHT'], instantiate=False)

    surf_normal = pygame.Surface(globals.SCREENSIZE)
    surf_normal.fill((0, 0, 0))
    test_maze.render_to_surface(surf_normal, grey_mode=False)

    surf_grey = pygame.Surface(globals.SCREENSIZE)
    surf_grey.fill((0, 0, 0))
    test_maze.render_to_surface(surf_grey, grey_mode=True)

    # Check color sampling
    # Normal wall pixel (e.g. at (20, 2)): blue component should be highest
    c_norm_wall = surf_normal.get_at((20, 2))
    assert c_norm_wall[2] > 200 and c_norm_wall[2] > c_norm_wall[0], f"Expected blue wall in normal mode, got {c_norm_wall}"

    # Grey wall pixel (e.g. at (20, 5)): R, G, B should be equal/grey (160, 160, 160)
    c_grey_wall = surf_grey.get_at((20, 5))
    assert c_grey_wall[0] == 160 and c_grey_wall[1] == 160 and c_grey_wall[2] == 160, f"Expected grey (160, 160, 160), got {c_grey_wall}"
    print("[PASS] Color sampling verified: Normal mode has blue walls, Transition mode has grey walls.")

    # Save visual verification images
    pygame.image.save(surf_normal, os.path.join(os.path.dirname(__file__), "test_maze_normal_render.png"))
    pygame.image.save(surf_grey, os.path.join(os.path.dirname(__file__), "test_maze_grey_transition_render.png"))
    print("[PASS] Visual verification images rendered and saved to scratch/.")

    # Cleanup globals
    for a in globals.OBJECTS:
        a.kill()
    globals.ROBOT_STARTLE_TIMER = 0
    globals.PENDING_EXIT = None

    print("\nALL ESCAPE ROUTES & TRANSITION TESTS PASSED SUCCESSFULLY! 100% VERIFIED.")

if __name__ == "__main__":
    run_tests()
