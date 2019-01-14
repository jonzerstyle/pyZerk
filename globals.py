import pygame

#colors
RED = [255,0,0]
GREEN = [0,255,0]
BLUE = [0,0,255]
YELLOW = [255,255,0]
CYAN = [0,255,255]
MAGENTA = [255,0,255]
WHITE = [255,255,255]
BLACK = [0,0,0]

SCREENSIZE = (800, 480)
SCREEN_BACKCOLOR = (0, 0, 0)
SOUNDS_ON = True

# must call pygame.init before doing try: on pygame stuff or Memory Error results
pygame.init()

# sprite groups - to help manage sprites
OBJECTS = pygame.sprite.Group()
ROBOTS = pygame.sprite.Group()
OTTO = pygame.sprite.Group()
PLAYER = pygame.sprite.GroupSingle()
BULLETS = pygame.sprite.Group()
COLLIDABLE = pygame.sprite.Group()
WALLS = pygame.sprite.Group()
TEXT = pygame.sprite.Group()

FPS = 0
FRAME_RATE_SETTING = 30
BASE_OBJECT_SPEED = SCREENSIZE[0] / 10.0
ROBOT_OBJECT_SPEED = BASE_OBJECT_SPEED
PLAYER_OBJECT_SPEED = BASE_OBJECT_SPEED * 1.25
BULLET_OBJECT_SPEED = PLAYER_OBJECT_SPEED * 2.0
OTTO_OBJECT_SPEED = BASE_OBJECT_SPEED / 2.0

SCORE = 0
LEVEL = 0 
OTTOTIMER = 0
NUM_OF_ROBOTS = 12

MENUON = False

# Import the android module. If we can't import it, set it to None - this
# lets us test it, and check to see if we want android-specific behavior.
try:
    import android
except ImportError:
    android = None

