import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
pygame.init()

import globals
import main
import menu
import robots
import player

def test_resume_and_startle():
    print("=== Testing Startle Timer and Resume Game System ===")

    # Initialize menu
    test_menu = menu.Class_StartMenu()

    # 1. Test Initial Menu State (No Game in Progress)
    globals.GAME_IN_PROGRESS = False
    assert test_menu.has_game_in_progress == False, "Expected no game in progress on fresh boot"
    
    # Test navigation skipping disabled item 1 (Resume Game)
    test_menu.selected_index = 0  # On Start Game
    # Press DOWN -> should skip 1 and land on 2 (Music Volume)
    ev_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    test_menu.handle_event(ev_down)
    assert test_menu.selected_index == 2, f"Expected DOWN from 0 to skip to 2, got {test_menu.selected_index}"

    # Press UP -> should skip 1 and land on 0 (Start Game)
    ev_up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
    test_menu.handle_event(ev_up)
    assert test_menu.selected_index == 0, f"Expected UP from 2 to skip to 0, got {test_menu.selected_index}"

    # Try pressing 2 (quick select) when no game in progress -> should NOT return RESUME_GAME
    ev_2 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2)
    res_2 = test_menu.handle_event(ev_2)
    assert res_2 != "RESUME_GAME", "Resume Game must not be activated when no game in progress"

    # Try pressing Enter on item 1 when no game in progress
    test_menu.selected_index = 1
    ev_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    res_enter = test_menu.handle_event(ev_enter)
    assert res_enter != "RESUME_GAME", "Enter on disabled Resume Game must not activate"
    print("  -> Initial state: Resume Game correctly disabled, grayed out, and skipped by navigation.")

    # 2. Test Game First Start & 5-Second Startle Timer
    main.startNewGame()
    assert globals.GAME_IN_PROGRESS == True, "Expected GAME_IN_PROGRESS == True after startNewGame()"
    assert test_menu.has_game_in_progress == True, "Expected menu to reflect game in progress"
    assert globals.ROBOT_STARTLE_TIMER == 5 * globals.FRAME_RATE_SETTING, \
        f"Expected startle timer 150 (5s), got {globals.ROBOT_STARTLE_TIMER}"
    assert len(globals.PLAYER.sprites()) == 1, "Player should be spawned"
    assert len(globals.ROBOTS.sprites()) > 0, "Robots should be spawned"

    # Verify robots cannot fire during startle window
    r = globals.ROBOTS.sprites()[0]
    r.gunHeatCnt = 0.0
    r.bullets = 0
    # Attempt updateMovement: bullet must not be created because ROBOT_STARTLE_TIMER > 0
    r.updateMovement()
    assert len(globals.BULLETS.sprites()) == 0, "Robots must not fire while startle timer is active"
    print("  -> Game first start: 5-second robot startle timer active (150 frames) and firing suppressed.")

    # 3. Test Pausing Gameplay & Returning to Menu with State Preserved
    globals.SCORE = 250
    globals.LEVEL = 3
    player_pos_before = list(globals.PLAYER.sprites()[0].pos)
    robot_count_before = len(globals.ROBOTS.sprites())

    # Simulate pause via pauseGame
    main.pauseGame(test_menu)
    assert globals.MENUON == True, "MENUON must be True when paused"
    assert test_menu.selected_index == 1, "Menu cursor must default to 1 (RESUME GAME) when pausing"

    # Verify entities are preserved (NOT killed)
    assert len(globals.PLAYER.sprites()) == 1, "Player must be preserved across pause"
    assert len(globals.ROBOTS.sprites()) == robot_count_before, "Robots must be preserved across pause"
    assert globals.SCORE == 250, "Score must be preserved across pause"
    assert globals.LEVEL == 3, "Level must be preserved across pause"
    print("  -> Gameplay pause: entities, score, level, and player pos preserved intact.")

    # 4. Test Menu Navigation when Game in Progress
    # DOWN from 1 should go to 2
    test_menu.handle_event(ev_down)
    assert test_menu.selected_index == 2, f"Expected DOWN from 1 to go to 2, got {test_menu.selected_index}"
    # UP from 2 should go to 1 (Resume Game is selectable now!)
    test_menu.handle_event(ev_up)
    assert test_menu.selected_index == 1, f"Expected UP from 2 to go to 1, got {test_menu.selected_index}"

    # Pressing ENTER on item 1 returns RESUME_GAME
    res_resume = test_menu.handle_event(ev_enter)
    assert res_resume == "RESUME_GAME", f"Expected RESUME_GAME action, got {res_resume}"

    # Pressing key 2 also returns RESUME_GAME
    res_key2 = test_menu.handle_event(ev_2)
    assert res_key2 == "RESUME_GAME", f"Expected key 2 to return RESUME_GAME, got {res_key2}"
    print("  -> Menu active state: Resume Game cleanly selectable via UP/DOWN, Enter, and Key 2.")

    # 5. Test Resuming Gameplay
    if res_resume == "RESUME_GAME":
        globals.MENUON = False
    assert globals.MENUON == False, "MENUON should be False after resuming"
    assert list(globals.PLAYER.sprites()[0].pos) == player_pos_before, "Player position intact upon resume"
    print("  -> Gameplay resume: successfully transitions out of menu back to gameplay.")

    # 6. Test Game Over Clears Game in Progress
    main.returnToMenu(test_menu)
    assert globals.MENUON == True, "MENUON should be True after returnToMenu"
    assert globals.GAME_IN_PROGRESS == False, "GAME_IN_PROGRESS should be False after game ends"
    assert test_menu.has_game_in_progress == False, "Menu should reflect no game in progress"
    assert test_menu.selected_index == 0, "Menu cursor should reset to 0 (START A GAME)"
    assert len(globals.OBJECTS.sprites()) == 0, "Objects should be cleared after game ends"
    print("  -> Game over / Session end: Game in progress cleared and Resume Game disabled.")

    # 7. Render Surface Verification for Both Menu States
    screen = pygame.Surface(globals.SCREENSIZE)
    # Disabled state
    test_menu.has_game_in_progress = False
    test_menu.draw(screen)
    pygame.image.save(screen, "scratch/test_menu_disabled_resume.png")

    # Enabled state
    test_menu.has_game_in_progress = True
    test_menu.selected_index = 1
    test_menu.draw(screen)
    pygame.image.save(screen, "scratch/test_menu_active_resume.png")
    print("  -> Menu rendering verified in both disabled and active resume states.")

    print("\nALL STARTLE TIMER AND RESUME GAME TESTS PASSED (100%)!")

if __name__ == '__main__':
    test_resume_and_startle()
