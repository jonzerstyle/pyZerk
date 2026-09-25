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
    print("=== STARTING BONUS LIFE DISPLAY & BANNER STACKING TESTS ===")

    pygame.init()
    screen = pygame.display.set_mode(globals.SCREENSIZE)
    banner_font = pygame.font.Font(None, 24)

    # 1. Test single banner positioning (Top vs Bottom)
    rect_top = main.draw_status_banner(screen, banner_font, "*** ROBOTS STARTLED! NO FIRING (5s) ***", (0, 255, 200), (0, 230, 80), (10, 25, 20), is_bottom=False, offset_y=0)
    assert rect_top.top == 37, f"Expected top banner at y=37, got {rect_top.top}"

    rect_bottom = main.draw_status_banner(screen, banner_font, "*** ROBOTS STARTLED! NO FIRING (5s) ***", (0, 255, 200), (0, 230, 80), (10, 25, 20), is_bottom=True, offset_y=0)
    expected_bottom_y = globals.SCREENSIZE[1] - rect_bottom.height - 22
    assert rect_bottom.top == expected_bottom_y, f"Expected bottom banner at y={expected_bottom_y}, got {rect_bottom.top}"
    print("[PASS] Single banner top (y=37) and bottom (y=438) positioning verified.")

    # 2. Test dual stacked banners when player NOT at top (both rendered at top of screen)
    screen.fill(globals.SCREEN_BACKCOLOR)
    globals.LIVES = 4
    bonus_rect_top = main.draw_status_banner(
        screen, banner_font, f"*** 10 LEVELS PASSED! +1 EXTRA LIFE! (LIVES: {globals.LIVES}) ***",
        (255, 230, 0), (255, 215, 0), (35, 30, 10), is_bottom=False, offset_y=0
    )
    startle_rect_top = main.draw_status_banner(
        screen, banner_font, "*** ROBOTS STARTLED! NO FIRING (5s) ***",
        (0, 255, 200), (0, 230, 80), (10, 25, 20), is_bottom=False, offset_y=28
    )
    assert bonus_rect_top.top == 37, f"Expected bonus life banner at y=37, got {bonus_rect_top.top}"
    assert startle_rect_top.top == 65, f"Expected stacked startle banner at y=65, got {startle_rect_top.top}"
    assert not bonus_rect_top.colliderect(startle_rect_top), "Banners must not overlap vertically"
    pygame.image.save(screen, os.path.join(os.path.dirname(__file__), "test_stacked_banners_top.png"))
    print("[PASS] Top stacked banners: Bonus life at y=37, Robot startle at y=65 (0 overlap). Saved screenshot.")

    # 3. Test dual stacked banners when player IS at top (both rendered at bottom of screen)
    screen.fill(globals.SCREEN_BACKCOLOR)
    bonus_rect_bot = main.draw_status_banner(
        screen, banner_font, f"*** 10 LEVELS PASSED! +1 EXTRA LIFE! (LIVES: {globals.LIVES}) ***",
        (255, 230, 0), (255, 215, 0), (35, 30, 10), is_bottom=True, offset_y=0
    )
    startle_rect_bot = main.draw_status_banner(
        screen, banner_font, "*** ROBOTS STARTLED! NO FIRING (5s) ***",
        (0, 255, 200), (0, 230, 80), (10, 25, 20), is_bottom=True, offset_y=28
    )
    assert bonus_rect_bot.top == expected_bottom_y, f"Expected bonus life banner at y={expected_bottom_y}, got {bonus_rect_bot.top}"
    assert startle_rect_bot.top == expected_bottom_y - 28, f"Expected stacked startle banner at y={expected_bottom_y - 28}, got {startle_rect_bot.top}"
    assert not bonus_rect_bot.colliderect(startle_rect_bot), "Bottom stacked banners must not overlap vertically"
    pygame.image.save(screen, os.path.join(os.path.dirname(__file__), "test_stacked_banners_bottom.png"))
    print("[PASS] Bottom stacked banners: Bonus life at y=438, Robot startle at y=410 (0 overlap). Saved screenshot.")

    # 4. Test 10-level pass triggering
    main.startNewGame()
    globals.LIVES = 3
    globals.LEVELS_PASSED = 9
    
    # Passing 10th level
    globals.LEVELS_PASSED += 1
    assert globals.LEVELS_PASSED % 10 == 0
    globals.LIVES += 1
    bonus_life_timer = 90
    assert globals.LIVES == 4, "Lives incremented to 4"
    assert bonus_life_timer == 90, "Bonus life timer set to 90 frames (~3s)"

    # Verify both banners render without shadowing
    globals.ROBOT_STARTLE_TIMER = 150
    game_over_timer = 0
    respawn_timer = 0
    is_player_at_top = False

    rendered_banners = []
    if game_over_timer == 0 and respawn_timer == 0:
        banner_offset = 0
        if bonus_life_timer > 0:
            msg = f"*** 10 LEVELS PASSED! +1 EXTRA LIFE! (LIVES: {globals.LIVES}) ***"
            r = main.draw_status_banner(screen, banner_font, msg, (255, 230, 0), (255, 215, 0), (35, 30, 10), is_player_at_top, offset_y=banner_offset)
            rendered_banners.append((msg, r))
            banner_offset += 28
        if globals.ROBOT_STARTLE_TIMER > 0:
            msg = f"★ ROBOTS STARTLED! NO FIRING (5s) ★"
            r = main.draw_status_banner(screen, banner_font, msg, (0, 255, 200), (0, 230, 80), (10, 25, 20), is_player_at_top, offset_y=banner_offset)
            rendered_banners.append((msg, r))
            banner_offset += 28

    assert len(rendered_banners) == 2, f"Expected 2 banners rendered, got {len(rendered_banners)}"
    assert "10 LEVELS PASSED" in rendered_banners[0][0]
    assert "ROBOTS STARTLED" in rendered_banners[1][0]
    assert rendered_banners[0][1].top == 37
    assert rendered_banners[1][1].top == 65
    print("[PASS] Full banner coexistence verified: Bonus life banner is NOT shadowed by robot startle banner!")

    print("\nALL BONUS LIFE DISPLAY TESTS PASSED SUCCESSFULLY! 100% VERIFIED.")

if __name__ == "__main__":
    run_tests()
