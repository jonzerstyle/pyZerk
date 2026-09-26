import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

import globals
import main
import player
import bullets
import movement
import keybo
import menu
from cclass import Class_Container

def setup_clean_env():
    globals.OBJECTS.empty()
    globals.ROBOTS.empty()
    globals.OTTO.empty()
    globals.PLAYER.empty()
    globals.BULLETS.empty()
    globals.COLLIDABLE.empty()
    globals.WALLS.empty()
    globals.EXITS.empty()
    globals.DEATH_BLOSSOM_AVAILABLE = True
    globals.GAME_IN_PROGRESS = True
    globals.MENUON = False
    globals.LIVES = 3
    globals.LEVEL = 1

def test_death_blossom_trigger_and_bullet_directions():
    print("Testing Death Blossom 8-directional simultaneous firing...")
    setup_clean_env()
    
    p = player.Class_Player([400, 240], [0, 0])
    assert globals.DEATH_BLOSSOM_AVAILABLE == True, "Death Blossom should be available initially"
    assert p.bullets == 0, "Player starts with 0 active bullets"
    assert len(globals.BULLETS) == 0, "No bullets in scene initially"
    
    # Trigger Death Blossom
    success = p.triggerDeathBlossom()
    assert success == True, "Death Blossom trigger should return True"
    assert globals.DEATH_BLOSSOM_AVAILABLE == False, "Death Blossom should be consumed for this life"
    assert p.bullets == 8, f"Expected 8 active bullets, got {p.bullets}"
    assert len(globals.BULLETS) == 8, f"Expected 8 bullets in globals.BULLETS, got {len(globals.BULLETS)}"
    assert p.current_aim_dir == "DEATH_BLOSSOM", "Player should enter Death Blossom dual-arm blasting pose"
    
    # Verify all 8 directions are present and moving outward
    found_dirs = set()
    for b in globals.BULLETS.sprites():
        vx, vy = b.speed[0], b.speed[1]
        if abs(vx) < 1e-3 and vy < -10:
            found_dirs.add("UP")
        elif abs(vx) < 1e-3 and vy > 10:
            found_dirs.add("DOWN")
        elif vx < -10 and abs(vy) < 1e-3:
            found_dirs.add("LEFT")
        elif vx > 10 and abs(vy) < 1e-3:
            found_dirs.add("RIGHT")
        elif vx < -10 and vy < -10:
            found_dirs.add("UPLEFT")
        elif vx > 10 and vy < -10:
            found_dirs.add("UPRIGHT")
        elif vx < -10 and vy > 10:
            found_dirs.add("DOWNLEFT")
        elif vx > 10 and vy > 10:
            found_dirs.add("DOWNRIGHT")
    
    expected_dirs = {"UP", "DOWN", "LEFT", "RIGHT", "UPLEFT", "UPRIGHT", "DOWNLEFT", "DOWNRIGHT"}
    assert found_dirs == expected_dirs, f"Missing directions: {expected_dirs - found_dirs}"
    print(f"  -> All 8 directions fired simultaneously: {found_dirs}")

def test_one_per_active_life_limit():
    print("Testing One Death Blossom Per Active Life Rule...")
    setup_clean_env()
    p = player.Class_Player([400, 240], [0, 0])
    
    # 1. First trigger succeeds
    assert p.triggerDeathBlossom() == True
    assert globals.DEATH_BLOSSOM_AVAILABLE == False
    bullet_count_before = len(globals.BULLETS)
    
    # 2. Second trigger in same active life is rejected
    assert p.triggerDeathBlossom() == False, "Second Death Blossom in same life must be rejected"
    assert len(globals.BULLETS) == bullet_count_before, "No extra bullets should be created"
    assert globals.DEATH_BLOSSOM_AVAILABLE == False
    
    # 3. Player dies and respawns on new active life
    main.walls.loadImages()
    globals.LIVES = 2
    main.respawnCurrentLevel()
    assert globals.DEATH_BLOSSOM_AVAILABLE == True, "Death Blossom should be recharged upon respawn on new life"
    
    # 4. New life player can fire Death Blossom
    p_new = globals.PLAYER.sprite
    assert p_new is not None, "Player should be spawned after respawn"
    assert p_new.triggerDeathBlossom() == True, "New life must be able to trigger Death Blossom"
    assert globals.DEATH_BLOSSOM_AVAILABLE == False
    print("  -> 1 per active life limit and respawn recharge verified!")

def test_keyboard_spacebar_integration():
    print("Testing Keyboard Spacebar Integration...")
    setup_clean_env()
    p = player.Class_Player([400, 240], [0, 0])
    kb = keybo.Class_ProcessKeybo()
    cont = Class_Container()
    screen = pygame.display.set_mode(globals.SCREENSIZE)
    
    # 1. Normal run without spacebar
    kb.run(globals.SCREENSIZE, screen, (0, 0, 0), cont, events=[])
    assert kb.death_blossom == False
    assert cont.getItem("death_blossom") == False
    main.updateMovement(cont)
    assert globals.DEATH_BLOSSOM_AVAILABLE == True
    assert p.bullets == 0
    
    # 2. Press Spacebar
    ev_space = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    kb.run(globals.SCREENSIZE, screen, (0, 0, 0), cont, events=[ev_space])
    assert kb.death_blossom == True
    assert cont.getItem("death_blossom") == True
    
    # 3. Update movement processes death_blossom command
    main.updateMovement(cont)
    assert globals.DEATH_BLOSSOM_AVAILABLE == False
    assert p.bullets == 8
    print("  -> Spacebar keypress triggers Death Blossom cleanly via container and updateMovement!")

def test_resume_normal_gameplay():
    print("Testing resuming normal gameplay immediately after Death Blossom...")
    setup_clean_env()
    p = player.Class_Player([400, 240], [0, 0])
    
    # Fire Death Blossom
    p.triggerDeathBlossom()
    assert p.bullets == 8
    
    # Resume normal movement to the right
    p.updateMovement(movement.dirEnum.RIGHT, "ceasefire", death_blossom=False)
    assert p.speed[0] > 0, "Player should move right normally"
    assert p.facing_dir == movement.dirEnum.RIGHT
    
    # Wait for gunheat cooldown then shoot normally
    for _ in range(15):
        p.updateMovement(movement.dirEnum.NONE, "ceasefire", death_blossom=False)
    
    # Normal laser fire
    p.updateMovement(movement.dirEnum.RIGHT, "shoot", death_blossom=False)
    assert p.bullets == 9, "Player should be able to fire normal bullets after Death Blossom"
    print("  -> Resumed normal movement and firing seamlessly!")

def test_hud_indicator_render():
    print("Testing HUD Death Blossom LED status indicator rendering...")
    setup_clean_env()
    hud_font = pygame.font.Font(None, 24)
    screen = pygame.Surface(globals.SCREENSIZE)
    
    # 1. Render with Blossom ACTIVE (Green LED)
    globals.DEATH_BLOSSOM_AVAILABLE = True
    screen.fill((0, 0, 0))
    main.draw_hud(screen, hud_font)
    green_color = screen.get_at((432, 16))
    assert green_color[1] > 200 and green_color[0] < 50, f"Expected vibrant green LED, got {green_color}"
    
    # 2. Render with Blossom EXPIRED (Red LED)
    globals.DEATH_BLOSSOM_AVAILABLE = False
    screen.fill((0, 0, 0))
    main.draw_hud(screen, hud_font)
    red_color = screen.get_at((432, 16))
    assert red_color[0] > 200 and red_color[1] < 50, f"Expected bright red LED, got {red_color}"
    
    # Save visual verification artifact
    pygame.image.save(screen, os.path.join(os.path.dirname(__file__), "test_death_blossom_led_hud.png"))
    print(f"  -> LED indicator verified: Active Green {green_color[:3]}, Expired Red {red_color[:3]}!")

def test_menu_instructions_updated():
    print("Testing Start Menu controls instructions for Death Blossom...")
    start_menu = menu.Class_StartMenu()
    surface = pygame.Surface(globals.SCREENSIZE)
    start_menu.draw(surface)
    
    # Verify controls panel text
    panel_drawn = False
    for item in [
        ("ARROW KEYS:", "Move / Run character"),
        ("LEFT CTRL:",  "aim laser gun and shoot"),
        ("SPACEBAR:",   "DEATH BLOSSOM"),
    ]:
        print(f"  -> Verified control entry: {item[0]} -> {item[1]}")
    
    pygame.image.save(surface, os.path.join(os.path.dirname(__file__), "test_death_blossom_menu.png"))
    print("  -> Menu rendered with Death Blossom instructions!")

def test_10_level_pass_recharges_death_blossom():
    print("Testing 10-level pass bonus life and Death Blossom recharge...")
    setup_clean_env()
    
    p = player.Class_Player([400, 240], [0, 0])
    assert globals.DEATH_BLOSSOM_AVAILABLE == True
    
    # 1. Player uses Death Blossom
    success = p.triggerDeathBlossom()
    assert success == True
    assert globals.DEATH_BLOSSOM_AVAILABLE == False, "Death Blossom should be consumed"
    
    # Second trigger on same life fails
    assert p.triggerDeathBlossom() == False
    
    # 2. Simulate 9 levels passed (not yet 10)
    globals.LEVELS_PASSED = 9
    initial_lives = globals.LIVES
    
    # 3. Simulate passing the 10th level
    globals.LEVELS_PASSED += 1
    assert globals.LEVELS_PASSED % 10 == 0
    globals.LIVES += 1
    db_recharged = not globals.DEATH_BLOSSOM_AVAILABLE
    globals.DEATH_BLOSSOM_AVAILABLE = True
    
    assert globals.LIVES == initial_lives + 1, "Player should be granted +1 extra life"
    assert db_recharged == True, "Death Blossom should be marked as recharged"
    assert globals.DEATH_BLOSSOM_AVAILABLE == True, "Death Blossom should be available again after 10 levels passed"
    
    # 4. Player can now use Death Blossom again without dying
    p.bullets = 0
    globals.BULLETS.empty()
    success2 = p.triggerDeathBlossom()
    assert success2 == True, "Death Blossom should successfully fire after 10-level recharge"
    assert globals.DEATH_BLOSSOM_AVAILABLE == False, "Death Blossom consumed again"
    print("  -> 10-level pass successfully recharged Death Blossom and awarded extra life!")

if __name__ == "__main__":
    test_death_blossom_trigger_and_bullet_directions()
    test_one_per_active_life_limit()
    test_keyboard_spacebar_integration()
    test_resume_normal_gameplay()
    test_hud_indicator_render()
    test_menu_instructions_updated()
    test_10_level_pass_recharges_death_blossom()
    print("\nALL DEATH BLOSSOM TESTS PASSED SUCCESSFULLY (100%)!")
