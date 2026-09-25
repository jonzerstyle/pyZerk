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

# pre-initialize audio mixer with 44.1kHz, 16-bit stereo, and 4096 buffer for smooth WebAudio
try:
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
except Exception:
    pass

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

FRAME_RATE_SETTING = 30
FPS = FRAME_RATE_SETTING
BASE_OBJECT_SPEED = SCREENSIZE[0] / 10.0
ROBOT_OBJECT_SPEED = BASE_OBJECT_SPEED
PLAYER_OBJECT_SPEED = BASE_OBJECT_SPEED * 1.25
BULLET_OBJECT_SPEED = PLAYER_OBJECT_SPEED * 2.0
OTTO_OBJECT_SPEED = BASE_OBJECT_SPEED / 2.0

SCORE = 0
LEVEL = 0 
INITIAL_LIVES = 3
LIVES = INITIAL_LIVES
LEVELS_PASSED = 0
OTTOTIMER = 0
NUM_OF_ROBOTS = 12

MENUON = True

# Import the android module. If we can't import it, set it to None - this
# lets us test it, and check to see if we want android-specific behavior.
try:
    import android
except ImportError:
    android = None

