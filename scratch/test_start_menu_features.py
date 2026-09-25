import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

import globals
import sounds
import menu
import main
import keybo
import player
import robots
import maze

def test_menu_initialization():
    print("Testing Menu Initialization...")
    assert globals.MENUON == True, "MENUON should default to True on startup"
    start_menu = menu.Class_StartMenu()
    assert start_menu.selected_index == 0, "Default selection should be item 0 (Start Game)"
    print("  -> Menu initialization test passed!")

def test_music_volume_and_sample():
    print("Testing Music Volume and Sample Output...")
    start_menu = menu.Class_StartMenu()
    start_menu.selected_index = 1
    
    # Test Left Arrow (Decrease volume)
    sounds.set_music_volume(0.7)
    ev_left = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
    start_menu.handle_event(ev_left)
    assert abs(sounds.get_music_volume() - 0.6) < 1e-4, f"Expected 0.6, got {sounds.get_music_volume()}"
    
    # Test Right Arrow (Increase volume)
    ev_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    start_menu.handle_event(ev_right)
    assert abs(sounds.get_music_volume() - 0.7) < 1e-4, f"Expected 0.7, got {sounds.get_music_volume()}"
    
    # Test Enter key on music volume plays sample output
    ev_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    res = start_menu.handle_event(ev_enter)
    assert res is None, "Enter on volume should not exit menu"
    assert start_menu.sample_type == "music", "Sample type should be music"
    assert start_menu.sample_active_until > pygame.time.get_ticks(), "Sample timer should be active"
    print("  -> Music volume and sample output test passed!")

def test_sfx_volume_and_sample():
    print("Testing SFX Volume and Sample Output...")
    start_menu = menu.Class_StartMenu()
    start_menu.selected_index = 2
    
    # Test Left Arrow (Decrease SFX volume)
    sounds.set_sfx_volume(0.7)
    ev_left = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
    start_menu.handle_event(ev_left)
    assert abs(sounds.get_sfx_volume() - 0.6) < 1e-4, f"Expected 0.6, got {sounds.get_sfx_volume()}"
    
    # Test Right Arrow (Increase SFX volume)
    ev_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    start_menu.handle_event(ev_right)
    assert abs(sounds.get_sfx_volume() - 0.7) < 1e-4, f"Expected 0.7, got {sounds.get_sfx_volume()}"
    
    # Test Enter key on SFX volume plays sample output
    ev_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    res = start_menu.handle_event(ev_enter)
    assert res is None, "Enter on SFX volume should not exit menu"
    assert start_menu.sample_type == "sfx", "Sample type should be sfx"
    assert start_menu.sample_active_until > pygame.time.get_ticks(), "Sample timer should be active"
    print("  -> SFX volume and sample output test passed!")

def test_quick_keys():
    print("Testing Quick Keys [1], [2], [3]...")
    start_menu = menu.Class_StartMenu()
    
    # Key '2' selects music volume and plays sample
    ev_2 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2)
    start_menu.handle_event(ev_2)
    assert start_menu.selected_index == 1
    assert start_menu.sample_type == "music"
    
    # Key '3' selects SFX volume and plays sample
    ev_3 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_3)
    start_menu.handle_event(ev_3)
    assert start_menu.selected_index == 2
    assert start_menu.sample_type == "sfx"
    
    # Key '1' triggers start game
    ev_1 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1)
    act = start_menu.handle_event(ev_1)
    assert act == "START_GAME"
    print("  -> Quick keys test passed!")

def test_start_game_and_return_to_menu():
    print("Testing Start Game and Return to Menu on Enter...")
    main.walls.loadImages()
    
    # 1. Start a game
    globals.MENUON = True
    main.startNewGame()
    assert globals.MENUON == False, "MENUON should be False after starting game"
    assert len(globals.PLAYER.sprites()) == 1, "Player should be spawned"
    assert len(globals.ROBOTS.sprites()) > 0, "Robots should be spawned"
    assert globals.SCORE == 0, "Score should be reset to 0"
    assert globals.LEVEL == 1, "Level should be set to 1"
    
    # 2. In game: hitting Enter returns back to main menu
    ev_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    kp = keybo.Class_ProcessKeybo()
    from cclass import Class_Container
    cont = Class_Container()
    kp.run(globals.SCREENSIZE, pygame.display.set_mode(globals.SCREENSIZE), (0,0,0), cont, events=[ev_enter])
    
    assert kp.return_to_menu == True, "return_to_menu flag should be True"
    assert globals.MENUON == True, "MENUON should be True after hitting Enter"
    
    main.returnToMenu()
    assert globals.MENUON == True
    assert len(globals.OBJECTS.sprites()) == 0, "All game objects should be cleared in menu"
    
    # 3. Start a game again
    main.startNewGame()
    assert globals.MENUON == False
    assert len(globals.PLAYER.sprites()) == 1
    assert len(globals.ROBOTS.sprites()) > 0
    main.returnToMenu()
    print("  -> Start game and return to menu on Enter test passed!")

def test_menu_rendering():
    print("Testing Menu Rendering Surface...")
    surface = pygame.Surface(globals.SCREENSIZE)
    start_menu = menu.Class_StartMenu()
    start_menu.draw(surface)
    assert surface.get_size() == globals.SCREENSIZE
    print("  -> Menu rendering test passed!")

if __name__ == "__main__":
    test_menu_initialization()
    test_music_volume_and_sample()
    test_sfx_volume_and_sample()
    test_quick_keys()
    test_start_game_and_return_to_menu()
    test_menu_rendering()
    print("\nALL START MENU FEATURE TESTS PASSED SUCCESSFULLY! 100%")
