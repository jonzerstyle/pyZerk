import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import globals
import highscore
import menu
import main

def run_tests():
    print("=== STARTING HIGH SCORE & INITIALS ENTRY TESTS ===")
    
    # 1. Test load_high_score() default values
    hs_path = highscore.get_highscore_path()
    if os.path.exists(hs_path):
        os.remove(hs_path)
        
    score, initials = highscore.load_high_score()
    assert score == 100, f"Expected default score 100, got {score}"
    assert initials == "CPU", f"Expected default initials CPU, got {initials}"
    assert globals.HIGH_SCORE == 100
    assert globals.HIGH_SCORE_INITIALS == "CPU"
    print("[PASS] Default high score correctly loaded (100, 'CPU').")

    # 2. Test is_high_score() logic
    assert not highscore.is_high_score(0), "Score 0 should not qualify"
    assert not highscore.is_high_score(50), "Score 50 should not qualify"
    assert not highscore.is_high_score(100), "Score 100 should not qualify (equal)"
    assert highscore.is_high_score(101), "Score 101 should qualify"
    assert highscore.is_high_score(250), "Score 250 should qualify"
    print("[PASS] is_high_score qualification logic verified.")

    # 3. Test saving high score and file persistence
    highscore.save_high_score(350, "MJW")
    assert globals.HIGH_SCORE == 350
    assert globals.HIGH_SCORE_INITIALS == "MJW"
    assert os.path.exists(hs_path), "highscore.json file must exist"
    
    with open(hs_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["score"] == 350
        assert data["initials"] == "MJW"
    print("[PASS] save_high_score file persistence verified.")

    # 4. Test reloading persisted high score
    globals.HIGH_SCORE = 0
    globals.HIGH_SCORE_INITIALS = ""
    s, init = highscore.load_high_score()
    assert s == 350 and init == "MJW"
    print("[PASS] high score file successfully reloaded across game sessions.")

    # 5. Test Class_HighScoreEntry interactive state machine
    entry = highscore.Class_HighScoreEntry(score=420)
    assert entry.active is True
    assert entry.initials == ["A", "A", "A"]
    assert entry.char_index == 0

    # Simulate typing 'B'
    evt_b = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_b, "unicode": "b"})
    entry.handle_event(evt_b)
    assert entry.initials[0] == "B", f"Expected first letter 'B', got {entry.initials[0]}"
    assert entry.char_index == 1, f"Expected cursor to advance to 1, got {entry.char_index}"

    # Simulate typing 'E'
    evt_e = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_e, "unicode": "e"})
    entry.handle_event(evt_e)
    assert entry.initials[1] == "E"
    assert entry.char_index == 2

    # Simulate typing 'R'
    evt_r = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_r, "unicode": "r"})
    entry.handle_event(evt_r)
    assert entry.initials[2] == "R"
    assert entry.char_index == 2  # At last slot

    assert entry.get_initials_string() == "BER"
    print("[PASS] Direct keyboard typing ('B', 'E', 'R') correctly captured.")

    # Test arrow cycling: UP on slot 2 ('R' -> 'S')
    evt_up = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_UP, "unicode": ""})
    entry.handle_event(evt_up)
    assert entry.initials[2] == "S", f"Expected 'S', got {entry.initials[2]}"

    # Test LEFT arrow navigation
    evt_left = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT, "unicode": ""})
    entry.handle_event(evt_left)
    assert entry.char_index == 1

    # Test BACKSPACE
    evt_back = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_BACKSPACE, "unicode": ""})
    entry.handle_event(evt_back)
    assert entry.char_index == 0

    # Type 'Z', 'E', 'R'
    entry.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_z, "unicode": "z"}))
    entry.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_e, "unicode": "e"}))
    entry.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_r, "unicode": "r"}))
    assert entry.get_initials_string() == "ZER"
    print("[PASS] Arrow keys, backspace, and cursor navigation verified.")

    # Test ENTER confirmation
    evt_enter = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN, "unicode": ""})
    res = entry.handle_event(evt_enter)
    assert res == "CONFIRMED"
    assert entry.active is False
    assert globals.HIGH_SCORE == 420
    assert globals.HIGH_SCORE_INITIALS == "ZER"
    print("[PASS] High score entry confirmation and persistence verified.")

    # 6. Test Rendering of High Score on Screen Surfaces
    screen = pygame.display.set_mode(globals.SCREENSIZE)
    
    # Test HighScoreEntry draw
    test_entry = highscore.Class_HighScoreEntry(score=500)
    test_entry.draw(screen)
    pygame.image.save(screen, os.path.join(os.path.dirname(__file__), "test_highscore_entry_render.png"))
    print("[PASS] HighScoreEntry dialog rendered and saved to test_highscore_entry_render.png.")

    # Test Start Menu with High Score banner
    start_menu = menu.Class_StartMenu()
    screen.fill((0, 0, 0))
    start_menu.draw(screen)
    pygame.image.save(screen, os.path.join(os.path.dirname(__file__), "test_menu_highscore_render.png"))
    print("[PASS] Start Menu with High Score marquee rendered and saved.")

    # 7. Test WebDeploy Environment (Zero File Writes, Uses browser localStorage)
    print("\n--- Testing Webdeploy Environment (localStorage without file writes) ---")
    import platform
    class MockLocalStorage:
        def __init__(self):
            self.store = {}
        def getItem(self, key):
            return self.store.get(key, None)
        def setItem(self, key, value):
            self.store[key] = str(value)

    class MockWindow:
        def __init__(self):
            self.localStorage = MockLocalStorage()

    mock_win = MockWindow()
    platform.window = mock_win
    
    assert highscore.is_web_env() is True, "is_web_env must detect platform.window"
    
    # Save high score in web mode
    mtime_before = os.path.getmtime(hs_path) if os.path.exists(hs_path) else None
    highscore.save_high_score(888, "WEB")
    
    assert mock_win.localStorage.getItem("pyzerk_high_score") == "888"
    assert mock_win.localStorage.getItem("pyzerk_high_initials") == "WEB"
    assert globals.HIGH_SCORE == 888
    assert globals.HIGH_SCORE_INITIALS == "WEB"
    
    # Verify file was NOT touched
    if mtime_before is not None:
        assert os.path.getmtime(hs_path) == mtime_before, "highscore.json must not be modified in web mode"
    print("[PASS] Web mode saved to browser localStorage with ZERO disk file writes.")

    # Load high score in web mode
    globals.HIGH_SCORE = 0
    globals.HIGH_SCORE_INITIALS = ""
    w_score, w_init = highscore.load_high_score()
    assert w_score == 888 and w_init == "WEB"
    print("[PASS] Web mode loaded directly from browser localStorage.")

    # Cleanup mock
    delattr(platform, "window")
    assert highscore.is_web_env() is False, "Desktop mode restored"

    # Restore default high score for repository clean state
    highscore.save_high_score(100, "CPU")

    print("\nALL HIGH SCORE TESTS PASSED SUCCESSFULLY! 100% VERIFIED.")

if __name__ == "__main__":
    run_tests()
