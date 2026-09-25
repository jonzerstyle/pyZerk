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

maxLevels = 50
MAX_OTTOS = 1

def startNewLevel():
    sounds.playSound(sounds.nextLevelSound)
    globals.OTTOTIMER = otto.ottoTimerReload 
    globals.LEVEL += 1
    # make level wrap back to zero
    if globals.LEVEL > maxLevels:
        globals.LEVEL = 0
    #destroy all the objects
    for a in globals.OBJECTS:
        a.kill()
    #start a new level
    pList = misc.distPoints(globals.SCREENSIZE, globals.NUM_OF_ROBOTS // 4, 4)
    player.Class_Player(player.player_start_pos, [0,0])
    for a in range(globals.NUM_OF_ROBOTS):
        robots.Class_Robot(pList[a], [0,0])
    #level up robots
    for a in globals.ROBOTS.sprites():
        a.levelUp(globals.LEVEL)
    maze.Class_Maze(globals.SCREENSIZE)

def startNewGame():
    """Start a fresh new game from Level 1, resetting score and level."""
    globals.SCORE = 0
    globals.LEVEL = 0
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

        # GAMEPLAY MODE
        # Keyboard processing
        keybo.run(globals.SCREENSIZE, screen, globals.SCREEN_BACKCOLOR, mainContainerC, events=events)
        if keybo.return_to_menu:
            returnToMenu()
            continue

        # Update object movement
        updateMovement(mainContainerC)

        # Look for collisions 
        detCollisions(keybo)

        # Tick off here once per second
        genTickTimer = oneSecTimer(genTickTimer)

        # Update objects
        for a in globals.OBJECTS:
            a.update()

        # Blank the screen
        screen.fill(globals.SCREEN_BACKCOLOR)
        dirtyrects = []

        for a in globals.OBJECTS.sprites():
            dirtyrects += a.draw(screen)

        # Draw in-game HUD
        score_surf = hud_font.render(f"SCORE: {globals.SCORE}", True, globals.WHITE)
        level_surf = hud_font.render(f"LEVEL: {globals.LEVEL}", True, globals.CYAN)
        menu_hint_surf = hud_font.render("[ENTER: MENU]", True, globals.YELLOW)
        dirtyrects.append(screen.blit(score_surf, (15, 8)))
        dirtyrects.append(screen.blit(level_surf, (360, 8)))
        dirtyrects.append(screen.blit(menu_hint_surf, (670, 8)))

        # Update the display
        pygame.display.flip()
        olddirtyrects = dirtyrects

        # Check to see if all robots destroyed or player destroyed to go to next level
        if globals.MENUON == False:
            if (len(globals.PLAYER.sprites()) == 0) or (len(globals.ROBOTS.sprites()) == 0):
                startNewLevel()

        await asyncio.sleep(0)

    #end of main loop

# This isn't run on Android.
if __name__ == "__main__":
    asyncio.run(main())


