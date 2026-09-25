import os
import sys

# Configure WSL audio via PulseAudio if available
local_lib = os.path.expanduser("~/.local/lib")
local_pulse = os.path.join(local_lib, "pulseaudio")
if os.path.exists("/mnt/wslg/PulseServer") and os.path.exists(local_lib):
    os.environ.setdefault("PULSE_SERVER", "unix:/mnt/wslg/PulseServer")
    os.environ.setdefault("SDL_AUDIODRIVER", "pulseaudio")
    cur_ld = os.environ.get("LD_LIBRARY_PATH", "")
    if local_lib not in cur_ld and not os.environ.get("_PYZERK_AUDIO_LOADED"):
        os.environ["LD_LIBRARY_PATH"] = f"{local_lib}:{local_pulse}" + (f":{cur_ld}" if cur_ld else "")
        os.environ["_PYZERK_AUDIO_LOADED"] = "1"
        os.execv(sys.executable, [sys.executable] + sys.argv)

#standard
import asyncio
import pygame

# Configure audio mixer parameters before any pygame subsystem initialization
try:
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
except Exception:
    pass
import random
import math
import copy
#import custom modules 
import globals
import misc
import player
import bullets
import robots
import movement
import sounds
import object
import maze
import otto
import walls
import text
import menu
import highscore
from cclass import Class_Container
from keybo import Class_ProcessKeybo 
from pygame.locals import *

try:
    import pygame.mixer as mixer
except ImportError:
    import android_mixer as mixer

try:
    icon = pygame.image.load(misc.get_asset_path('icon.png'))
    pygame.display.set_icon(icon)
except Exception:
    pass

maxLevels = globals.MAX_LEVELS
MAX_OTTOS = 1

def setupRoom(level_num):
    """Set up objects, player, robots, and maze for a level room."""
    globals.OTTOTIMER = otto.ottoTimerReload 
    # destroy all existing objects
    for a in globals.OBJECTS:
        a.kill()
    # spawn player and robots
    pList = misc.distPoints(globals.SCREENSIZE, globals.NUM_OF_ROBOTS // 4, 4)
    player.Class_Player(player.player_start_pos, [0,0])
    for a in range(globals.NUM_OF_ROBOTS):
        robots.Class_Robot(pList[a], [0,0])
    # level up robots to match current level
    for a in globals.ROBOTS.sprites():
        a.levelUp(level_num)
    maze.Class_Maze(globals.SCREENSIZE)

def startNewLevel():
    """Advance to the next level and setup the room, looping cleanly to Level 1 when max level is surpassed."""
    sounds.playSound(sounds.nextLevelSound)
    globals.LEVEL += 1
    did_loop = False
    # When max level is reached and surpassed, loop cleanly back to Level 1
    if globals.LEVEL > globals.MAX_LEVELS:
        globals.LEVEL = 1
        globals.LEVEL_LOOP += 1
        did_loop = True
    setupRoom(globals.LEVEL)
    return did_loop

def respawnCurrentLevel():
    """Respawn the player and reset the room for the current level without advancing."""
    setupRoom(globals.LEVEL)

def startNewGame():
    """Start a fresh new game from Level 1, resetting score, lives, level, and loop counter."""
    highscore.load_high_score()
    globals.SCORE = 0
    globals.LEVEL = 0
    globals.LEVEL_LOOP = 0
    globals.LIVES = globals.INITIAL_LIVES
    globals.LEVELS_PASSED = 0
    for a in globals.OBJECTS:
        a.kill()
    startNewLevel()
    globals.MENUON = False
    sounds.start_game_music()

def returnToMenu():
    """Return to start menu, halting gameplay entities while keeping music active."""
    globals.MENUON = True
    for a in globals.OBJECTS:
        a.kill()

def updateMovement(main_containerObj):
    for a in globals.PLAYER.sprites():
        a.updateMovement(main_containerObj.getItem("player_movement"),\
                         main_containerObj.getItem("player_fire"))
    for a in globals.ROBOTS.sprites():
        a.updateMovement()
    for a in globals.OTTO.sprites():
        if len(globals.PLAYER.sprites()) > 0:
            a.updateMovement(globals.PLAYER.sprites()[0])

def detCollisions(keyboObj):
    colSprites = globals.COLLIDABLE.sprites()
    for x in range(len(globals.COLLIDABLE.sprites()) - 1):
        for y in range(x+1 , len(globals.COLLIDABLE.sprites())):
            if ((pygame.sprite.collide_rect(colSprites[x],colSprites[y]) == True) \
                & (keyboObj.collisionOn)):
                colSprites[x].collide(colSprites[y])
                colSprites[y].collide(colSprites[x])

def oneSecTimer(timer):
    if (pygame.time.get_ticks() >= timer + 1000):
        timer = pygame.time.get_ticks()
        if (len(globals.OTTO) < MAX_OTTOS):
            if (globals.OTTOTIMER > 0):
                globals.OTTOTIMER -= 1
            else:
                globals.OTTOTIMER = otto.ottoTimerReload 
                #make otto
                otto.Class_Otto()
                sounds.playSound(sounds.ottoAliveSound)
    return timer

def _web_log(msg):
    try:
        import platform
        if hasattr(platform, "window") and hasattr(platform.window, "logToScreen"):
            platform.window.logToScreen(msg)
    except Exception:
        pass

# main
async def main():
    _web_log("main(): Starting...")
    keybo = Class_ProcessKeybo()
    keybo.collisionOn = True 
    flags = DOUBLEBUF
    bpp = 0
    screen = pygame.display.set_mode(globals.SCREENSIZE, flags, bpp)
    _web_log("main(): Display initialized!")
    walls.loadImages()
    screen.fill(globals.SCREEN_BACKCOLOR)
    pygame.display.set_caption("Pyzerk")

    clock = pygame.time.Clock()
    olddirtyrects = []
    genTickTimer = pygame.time.get_ticks()
    globals.OTTOTIMER = otto.ottoTimerReload 

    # Map the back button to the escape key.
    if globals.android:
        globals.android.init()
        globals.android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)

    #create a container for generic vars
    mainContainerC = Class_Container()

    # Welcome voice on boot and start background music
    if globals.SOUNDS_ON and mixer.get_init(): 
        sounds.playSound(sounds.welcomeSound) 
        sounds.start_game_music() 

    # Start Menu initialization
    start_menu = menu.Class_StartMenu()
    globals.MENUON = True
    hud_font = pygame.font.Font(None, 24)
    go_font = pygame.font.Font(None, 54)
    banner_font = pygame.font.Font(None, 28)

    highscore.load_high_score()
    high_score_entry = None
    respawn_timer = 0
    game_over_timer = 0
    bonus_life_timer = 0
    loop_banner_timer = 0

    #main loop
    while keybo.running == True:
        dt = clock.tick(globals.FRAME_RATE_SETTING)
        globals.FPS = 1000.0 / dt if dt > 0 else float(globals.FRAME_RATE_SETTING)

        # Android-specific:
        if globals.android:
            if globals.android.check_pause():
                globals.android.wait_for_resume()

        events = pygame.event.get()

        # START MENU MODE
        if globals.MENUON:
            for event in events:
                action = start_menu.handle_event(event)
                if action == "START_GAME":
                    high_score_entry = None
                    respawn_timer = 0
                    game_over_timer = 0
                    bonus_life_timer = 0
                    loop_banner_timer = 0
                    startNewGame()
                    break
                elif action == "QUIT":
                    keybo.running = False
                    break

            if globals.MENUON:
                start_menu.draw(screen)
                pygame.display.flip()
            await asyncio.sleep(0)
            continue

        # HIGH SCORE INITIALS ENTRY MODE
        if high_score_entry and high_score_entry.active:
            for event in events:
                action = high_score_entry.handle_event(event)
                if action == "CONFIRMED":
                    high_score_entry = None
                    game_over_timer = 90
                    if globals.SOUNDS_ON:
                        sounds.playSound(sounds.gameOverSound)
                    break

            if high_score_entry and high_score_entry.active:
                screen.fill(globals.SCREEN_BACKCOLOR)
                for a in globals.OBJECTS.sprites():
                    a.draw(screen)
                high_score_entry.draw(screen)
                pygame.display.flip()
                await asyncio.sleep(0)
                continue

        # GAMEPLAY MODE
        # Keyboard processing
        keybo.run(globals.SCREENSIZE, screen, globals.SCREEN_BACKCOLOR, mainContainerC, events=events)
        if keybo.return_to_menu:
            if highscore.is_high_score(globals.SCORE):
                high_score_entry = highscore.Class_HighScoreEntry(globals.SCORE)
                continue
            respawn_timer = 0
            game_over_timer = 0
            bonus_life_timer = 0
            loop_banner_timer = 0
            returnToMenu()
            continue

        if game_over_timer > 0:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    game_over_timer = 0
                    returnToMenu()
                    break
            if globals.MENUON:
                continue
            game_over_timer -= 1
            if game_over_timer == 0:
                returnToMenu()
                continue
        elif respawn_timer > 0:
            respawn_timer -= 1
            if respawn_timer == 0:
                respawnCurrentLevel()
        else:
            # Update object movement
            updateMovement(mainContainerC)

            # Look for collisions 
            detCollisions(keybo)

            # Tick off here once per second
            genTickTimer = oneSecTimer(genTickTimer)

            # Update objects
            for a in globals.OBJECTS:
                a.update()

            if bonus_life_timer > 0:
                bonus_life_timer -= 1
            if loop_banner_timer > 0:
                loop_banner_timer -= 1

            # Check to see if player died or all robots destroyed
            if len(globals.PLAYER.sprites()) == 0:
                # Player lost a life!
                globals.LIVES -= 1
                if globals.LIVES > 0:
                    respawn_timer = 30  # ~1 second respawn delay
                else:
                    if highscore.is_high_score(globals.SCORE):
                        high_score_entry = highscore.Class_HighScoreEntry(globals.SCORE)
                    else:
                        game_over_timer = 90  # ~3 seconds Game Over display
                        if globals.SOUNDS_ON:
                            sounds.playSound(sounds.gameOverSound)
            elif len(globals.ROBOTS.sprites()) == 0:
                # Level cleared!
                globals.LEVELS_PASSED += 1
                # Award one life back every ten levels passed
                if globals.LEVELS_PASSED % 10 == 0:
                    globals.LIVES += 1
                    bonus_life_timer = 60  # ~2 seconds banner
                did_loop = startNewLevel()
                if did_loop:
                    loop_banner_timer = 90  # ~3 seconds milestone banner for looping game

        # Blank the screen
        screen.fill(globals.SCREEN_BACKCOLOR)
        dirtyrects = []

        for a in globals.OBJECTS.sprites():
            dirtyrects += a.draw(screen)

        # Draw in-game HUD top status bar
        score_surf = hud_font.render(f"SCORE: {globals.SCORE}", True, globals.WHITE)
        lives_color = (0, 255, 100) if globals.LIVES > 1 else (255, 60, 60)
        lives_surf = hud_font.render(f"LIVES: {globals.LIVES}", True, lives_color)
        if globals.LEVEL_LOOP > 0:
            level_text = f"LEVEL: {globals.LEVEL} [L{globals.LEVEL_LOOP + 1}]"
        else:
            level_text = f"LEVEL: {globals.LEVEL}"
        level_surf = hud_font.render(level_text, True, globals.CYAN)
        hi_surf = hud_font.render(f"HI: {globals.HIGH_SCORE} ({globals.HIGH_SCORE_INITIALS})", True, (255, 215, 0))
        menu_hint_surf = hud_font.render("[ENTER: MENU]", True, globals.YELLOW)
        dirtyrects.append(screen.blit(score_surf, (15, 8)))
        dirtyrects.append(screen.blit(lives_surf, (155, 8)))
        dirtyrects.append(screen.blit(level_surf, (270, 8)))
        dirtyrects.append(screen.blit(hi_surf, (440, 8)))
        dirtyrects.append(screen.blit(menu_hint_surf, (665, 8)))

        # Draw loop-around milestone banner when max level is surpassed
        if loop_banner_timer > 0 and game_over_timer == 0 and respawn_timer == 0:
            loop_msg = f"★ MAX LEVEL SURPASSED! ENTERING LOOP {globals.LEVEL_LOOP + 1}! ★"
            loop_surf = banner_font.render(loop_msg, True, (0, 255, 255))
            lx = (globals.SCREENSIZE[0] - loop_surf.get_width()) // 2
            bg_rect = pygame.Rect(lx - 12, 34, loop_surf.get_width() + 24, loop_surf.get_height() + 6)
            pygame.draw.rect(screen, (10, 20, 30), bg_rect)
            pygame.draw.rect(screen, (0, 220, 255), bg_rect, 1)
            dirtyrects.append(screen.blit(loop_surf, (lx, 37)))
        # Draw 10-level bonus life celebration banner
        elif bonus_life_timer > 0 and game_over_timer == 0 and respawn_timer == 0:
            bonus_surf = banner_font.render("★ 10 LEVELS PASSED! +1 EXTRA LIFE! ★", True, (255, 230, 0))
            bx = (globals.SCREENSIZE[0] - bonus_surf.get_width()) // 2
            bg_rect = pygame.Rect(bx - 12, 34, bonus_surf.get_width() + 24, bonus_surf.get_height() + 6)
            pygame.draw.rect(screen, (10, 25, 15), bg_rect)
            pygame.draw.rect(screen, (255, 220, 0), bg_rect, 1)
            dirtyrects.append(screen.blit(bonus_surf, (bx, 37)))

        # Draw respawn notification overlay if player died but still has lives
        if respawn_timer > 0:
            respawn_text = f"PLAYER DESTROYED!  LIVES REMAINING: {globals.LIVES}"
            respawn_surf = banner_font.render(respawn_text, True, (255, 90, 90))
            rx = (globals.SCREENSIZE[0] - respawn_surf.get_width()) // 2
            ry = (globals.SCREENSIZE[1] - respawn_surf.get_height()) // 2
            bg_rect = pygame.Rect(rx - 16, ry - 10, respawn_surf.get_width() + 32, respawn_surf.get_height() + 20)
            pygame.draw.rect(screen, (25, 10, 10), bg_rect)
            pygame.draw.rect(screen, (255, 60, 60), bg_rect, 2)
            dirtyrects.append(screen.blit(respawn_surf, (rx, ry)))

        # Draw Game Over modal overlay if out of lives
        if game_over_timer > 0:
            panel_w, panel_h = 500, 180
            px = (globals.SCREENSIZE[0] - panel_w) // 2
            py = (globals.SCREENSIZE[1] - panel_h) // 2
            panel_rect = pygame.Rect(px, py, panel_w, panel_h)
            pygame.draw.rect(screen, (20, 10, 15), panel_rect)
            pygame.draw.rect(screen, (255, 50, 50), panel_rect, 3)
            
            go_surf = go_font.render("GAME OVER", True, (255, 40, 40))
            score_summary = hud_font.render(f"FINAL SCORE: {globals.SCORE}   |   LEVELS PASSED: {globals.LEVELS_PASSED}", True, globals.WHITE)
            hint_summary = hud_font.render("[PRESS ENTER TO RETURN TO MENU]", True, globals.YELLOW)
            
            dirtyrects.append(screen.blit(go_surf, go_surf.get_rect(center=(px + panel_w // 2, py + 45))))
            dirtyrects.append(screen.blit(score_summary, score_summary.get_rect(center=(px + panel_w // 2, py + 105))))
            dirtyrects.append(screen.blit(hint_summary, hint_summary.get_rect(center=(px + panel_w // 2, py + 145))))

        # Update the display
        pygame.display.flip()
        olddirtyrects = dirtyrects

        await asyncio.sleep(0)

    #end of main loop

# This isn't run on Android.
if __name__ == "__main__":
    asyncio.run(main())


