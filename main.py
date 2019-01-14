#standard
import pygame
import random
import math
import copy
import os
import sys
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
from cclass import Class_Container
from keybo import Class_ProcessKeybo 
from pygame.locals import *

try:
    import pygame.mixer as mixer
except ImportError:
    import android_mixer as mixer

icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)

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
    pList = misc.distPoints(globals.SCREENSIZE, globals.NUM_OF_ROBOTS / 4, 4)
    player.Class_Player(player.player_start_pos, [0,0])
    for a in range(globals.NUM_OF_ROBOTS):
        robots.Class_Robot(pList[a], [0,0])
    #level up robots
    for a in globals.ROBOTS.sprites():
        a.levelUp(globals.LEVEL)
    maze.Class_Maze(globals.SCREENSIZE)

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
        for y in xrange(x+1 , len(globals.COLLIDABLE.sprites())):
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

# main
def main():
    keybo = Class_ProcessKeybo()
    keybo.collisionOn = True 
    flags = DOUBLEBUF
    bpp = 24
    screen = pygame.display.set_mode(globals.SCREENSIZE, flags, bpp)
    walls.loadImages()
    screen.fill(globals.SCREEN_BACKCOLOR)
    pygame.display.set_caption("Pyzerk")
    clock = pygame.time.Clock()
    olddirtyrects = []
    init = True
    genTickTimer = pygame.time.get_ticks()
    globals.OTTOTIMER = otto.ottoTimerReload 

    # Map the back button to the escape key.
    if globals.android:
        globals.android.init()
        globals.android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)

    #create a container for generic vars
    mainContainerC = Class_Container()

    #setup soundtrack
    if (globals.SOUNDS_ON == True): 
        sounds.playSound(sounds.welcomeSound) 
        sounds.playSound(sounds.robotWalkSound) 
        mixer.Channel(sounds.SOUNDTRACK_CHAN).play(sounds.soundTrack0Sound, -1)

    #main loop
    while keybo.running == True:
        globals.FPS = 1000.0 / clock.tick(globals.FRAME_RATE_SETTING)
        if init == True:
            init = False
            #startNewLevel()
            #show menu instead of starting game
            text.Class_Text((0,0), "First Menu Item", globals.WHITE)

        # Android-specific:
        if globals.android:
            if globals.android.check_pause():
                globals.android.wait_for_resume()

        #keyboard processing
        keybo.run(globals.SCREENSIZE, screen, globals.SCREEN_BACKCOLOR, mainContainerC)

        #update object movement
        updateMovement(mainContainerC)

        #look for collisions 
        detCollisions(keybo)

        #tick off here once per second
        genTickTimer = oneSecTimer(genTickTimer)

        #update objects
        for a in globals.OBJECTS:
            a.update()

        #blank the screen
        screen.fill(globals.SCREEN_BACKCOLOR)
        dirtyrects = []

        for a in globals.OBJECTS.sprites():
            dirtyrects += a.draw(screen)

        #draw the text
        for a in globals.TEXT.sprites():
            a.update(str(globals.SCORE))
            dirtyrects += a.draw(screen)

        #update the display pass in the rectangles to update for each object
        pygame.display.update(dirtyrects + olddirtyrects)
        olddirtyrects = dirtyrects

        #check to see if all robots destroyed or player destroyed to go to next level
        if (globals.MENUON == False):
            if ((len(globals.PLAYER.sprites()) == 0) | (len(globals.ROBOTS.sprites()) == 0)):
                startNewLevel()

    #end of main loop

# This isn't run on Android.
if __name__ == "__main__":
    main()

