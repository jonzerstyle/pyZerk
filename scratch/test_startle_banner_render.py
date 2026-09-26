import os, sys
sys.path.insert(0, os.path.abspath('.'))
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
import math

pygame.init()
import globals
import main

screen = pygame.Surface(globals.SCREENSIZE)
main.startNewGame()

# Advance 1 frame of gameplay drawing
banner_font = pygame.font.Font(None, 28)
hud_font = pygame.font.Font(None, 24)

screen.fill(globals.SCREEN_BACKCOLOR)
for a in globals.OBJECTS.sprites():
    a.draw(screen)

main.draw_hud(screen, hud_font)

secs_left = math.ceil(globals.ROBOT_STARTLE_TIMER / globals.FRAME_RATE_SETTING)
startle_msg = f"*** ROBOTS STARTLED! NO FIRING ({secs_left}s) ***"
main.draw_status_banner(screen, banner_font, startle_msg, (0, 255, 200), (0, 230, 80), (10, 25, 20), is_bottom=False)

pygame.image.save(screen, 'scratch/test_game_start_startle_banner.png')
print('Saved scratch/test_game_start_startle_banner.png')
