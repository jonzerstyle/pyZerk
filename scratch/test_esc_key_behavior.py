#!/usr/bin/env python3
"""
Test Suite: ESC Key Handling & Web Environment Resilience
Verifies that pressing ESC while playing the game returns cleanly to the
Start Menu (like ENTER) without terminating the main game loop or hanging
the web interface.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import globals
import keybo
import menu
import highscore
import cclass

def setup_test_env():
    pygame.init()
    screen = pygame.display.set_mode(globals.SCREENSIZE)
    globals.FPS = 30
    globals.SOUNDS_ON = False
    return screen

def run_tests():
    screen = setup_test_env()
    print("=== STARTING ESC KEY BEHAVIOR & WEB RESILIENCE TESTS ===")

    # Test 1: Hitting ESC during gameplay
    print("\n--- 1. Testing ESC during Gameplay ---")
    kb = keybo.Class_ProcessKeybo()
    container = cclass.Class_Container()
    globals.MENUON = False

    esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    kb.run(globals.SCREENSIZE, screen, globals.SCREEN_BACKCOLOR, container, events=[esc_event])

    assert kb.running == 1, "keybo.running MUST remain 1 (True) when ESC is pressed in gameplay!"
    assert kb.return_to_menu is True, "keybo.return_to_menu MUST be True when ESC is pressed!"
    assert globals.MENUON is True, "globals.MENUON MUST be set to True to return to menu!"
    print("[PASS] Pressing ESC during gameplay sets return_to_menu=True, MENUON=True, and leaves running=1.")

    # Test 2: Hitting ENTER during gameplay (verifying parity with ESC)
    print("\n--- 2. Testing ENTER during Gameplay ---")
    kb2 = keybo.Class_ProcessKeybo()
    globals.MENUON = False
    enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    kb2.run(globals.SCREENSIZE, screen, globals.SCREEN_BACKCOLOR, container, events=[enter_event])

    assert kb2.running == 1
    assert kb2.return_to_menu is True
    assert globals.MENUON is True
    print("[PASS] Pressing ENTER during gameplay sets return_to_menu=True, MENUON=True, and leaves running=1.")

    # Test 3: Hitting ESC on Start Menu in Web Environment
    print("\n--- 3. Testing ESC on Start Menu in Web Environment ---")
    start_menu = menu.Class_StartMenu()
    
    # Mock web environment
    orig_is_web = highscore.is_web_env
    highscore.is_web_env = lambda: True
    try:
        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        action = start_menu.handle_event(esc_event)
        assert action is None, f"Expected action is None in web environment on ESC, got {action}"
        print("[PASS] In web environment, ESC in Start Menu does NOT return QUIT (prevents hang up).")
    finally:
        highscore.is_web_env = orig_is_web

    # Test 4: Hitting ESC on Start Menu in Desktop Environment
    print("\n--- 4. Testing ESC on Start Menu in Desktop Environment ---")
    highscore.is_web_env = lambda: False
    try:
        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        action = start_menu.handle_event(esc_event)
        assert action == "QUIT", f"Expected action 'QUIT' on desktop, got {action}"
        print("[PASS] In desktop environment, ESC in Start Menu returns 'QUIT' as expected.")
    finally:
        highscore.is_web_env = orig_is_web

    print("\nALL ESC KEY BEHAVIOR & WEB RESILIENCE TESTS PASSED! 100% VERIFIED.")

if __name__ == '__main__':
    run_tests()
