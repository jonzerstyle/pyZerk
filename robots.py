import globals
import object
import copy
import random
import movement
import sounds
import pygame
import misc
import bullets


# Define robot base dimensions
robot_polygon_max_cnt = (110.0, 130.0)

def normalize_points(pts):
    return [[p[0] / robot_polygon_max_cnt[0], p[1] / robot_polygon_max_cnt[1]] for p in pts]

# Modular polygon components (raw grid scale: 110 x 130)
# 1. Upper body left side (Head top/left, left shoulder/arm down to 70, up to waist at [30, 50])
ROBOT_UPPER_LEFT = [
    [30.0, 0.0],
    [30.0, 10.0],
    [20.0, 10.0],
    [20.0, 20.0],
    [10.0, 20.0],
    [10.0, 30.0],
    [0.0, 30.0],
    [0.0, 70.0],
    [20.0, 70.0],
    [20.0, 50.0],
    [30.0, 50.0],
]

# 2. Upper body right side (From right waist [80, 50], down arm to 70, up right head to top at [30, 0])
ROBOT_UPPER_RIGHT = [
    [80.0, 50.0],
    [90.0, 50.0],
    [90.0, 70.0],
    [110.0, 70.0],
    [110.0, 30.0],
    [100.0, 30.0],
    [100.0, 20.0],
    [90.0, 20.0],
    [90.0, 10.0],
    [80.0, 10.0],
    [80.0, 0.0],
    [30.0, 0.0],
]

# 3. Leg animation poses (connected between left waist [30, 50] and right waist [80, 50])
# Standing / idle pose: both feet planted firmly on the ground (y=130)
ROBOT_STANDING_LEGS = [
    [30.0, 110.0],
    [20.0, 110.0],
    [20.0, 130.0],
    [50.0, 130.0],
    [50.0, 80.0],
    [60.0, 80.0],
    [60.0, 130.0],
    [90.0, 130.0],
    [90.0, 110.0],
    [80.0, 110.0],
]

# Stride A: Left leg planted (y=130), Right leg lifted/kicked back (y=90..110)
ROBOT_STRIDE_A_LEGS = [
    [30.0, 110.0],
    [20.0, 110.0],
    [20.0, 130.0],
    [50.0, 130.0],
    [50.0, 80.0],
    [60.0, 80.0],
    [60.0, 110.0],
    [90.0, 110.0],
    [90.0, 90.0],
    [80.0, 90.0],
]

# Stride B: Left leg lifted/kicked back (y=90..110), Right leg planted (y=130)
ROBOT_STRIDE_B_LEGS = [
    [30.0, 90.0],
    [20.0, 90.0],
    [20.0, 110.0],
    [50.0, 110.0],
    [50.0, 80.0],
    [60.0, 80.0],
    [60.0, 130.0],
    [90.0, 130.0],
    [90.0, 110.0],
    [80.0, 110.0],
]

# 4. Eyeball scanning poses across the visor slit (y=20..30)
# Visor horizontal width is from x=10 to x=100 in head.
EYE_CENTER = [
    [42.0, 20.0], [42.0, 30.0], [68.0, 30.0], [68.0, 20.0], [42.0, 20.0]
]
EYE_MID_LEFT = [
    [30.0, 20.0], [30.0, 30.0], [56.0, 30.0], [56.0, 20.0], [30.0, 20.0]
]
EYE_FAR_LEFT = [
    [18.0, 20.0], [18.0, 30.0], [44.0, 30.0], [44.0, 20.0], [18.0, 20.0]
]
EYE_BLANK = []
EYE_FAR_RIGHT = [
    [66.0, 20.0], [66.0, 30.0], [92.0, 30.0], [92.0, 20.0], [66.0, 20.0]
]
EYE_MID_RIGHT = [
    [54.0, 20.0], [54.0, 30.0], [80.0, 30.0], [80.0, 20.0], [54.0, 20.0]
]

# Pre-normalized modular components
NORM_ROBOT_UPPER_LEFT = normalize_points(ROBOT_UPPER_LEFT)
NORM_ROBOT_UPPER_RIGHT = normalize_points(ROBOT_UPPER_RIGHT)

NORM_ROBOT_STANDING_LEGS = normalize_points(ROBOT_STANDING_LEGS)
NORM_ROBOT_STRIDE_A_LEGS = normalize_points(ROBOT_STRIDE_A_LEGS)
NORM_ROBOT_STRIDE_B_LEGS = normalize_points(ROBOT_STRIDE_B_LEGS)

NORM_EYE_CENTER = normalize_points(EYE_CENTER)
NORM_EYE_MID_LEFT = normalize_points(EYE_MID_LEFT)
NORM_EYE_FAR_LEFT = normalize_points(EYE_FAR_LEFT)
NORM_EYE_BLANK = []
NORM_EYE_FAR_RIGHT = normalize_points(EYE_FAR_RIGHT)
NORM_EYE_MID_RIGHT = normalize_points(EYE_MID_RIGHT)

# Colors: first is outline, second is fill
robot_polygon_colors = [globals.BLACK, globals.YELLOW]
robot_eyeball_colors = [[], globals.BLACK]
robot_pixel_size = [20.0, 20.0]
robot_speed_mag = globals.ROBOT_OBJECT_SPEED

# Default assembled polygons for initial sprite state
robot_polygon_pts = copy.deepcopy(
    NORM_ROBOT_UPPER_LEFT + NORM_ROBOT_STANDING_LEGS + NORM_ROBOT_UPPER_RIGHT
)
robot_eyeball_pts = copy.deepcopy(NORM_EYE_CENTER)
robot_polygon_list_pts = [robot_polygon_pts[:], robot_eyeball_pts[:]]
robot_color_list_pts = [robot_polygon_colors[:], robot_eyeball_colors[:]]

robot_max_bullets = 1
robot_gunheatcnt_max = 120.0

# class to display a real object - inherits low level Obj class
class Class_Robot(object.Class_Obj):
    def __init__(self, pos, speed, size = robot_pixel_size,\
                 list_polygon_pts = robot_polygon_list_pts,\
                 list_colors = robot_color_list_pts, \
                 groups = []):
        self.blitImage = None
        self.angle = 0.0
        self.size = copy.deepcopy(size)
        self.list_polygon_pts = copy.deepcopy(list_polygon_pts) 
        self.list_colors = copy.deepcopy(list_colors)
        self.lastDir = movement.dirEnum.NONE
        self.gunHeatCnt = 0 
        self.bullets = 0
        self.max_bullets = robot_max_bullets
        self.speed_mag = robot_speed_mag 
        self.gunheatcnt_max = robot_gunheatcnt_max 
        # start gunheat at something reasonable so robots dont shoot right after creation
        self.gunHeatCnt = random.uniform(self.gunheatcnt_max / 2, self.gunheatcnt_max)

        # Walking leg animation configuration
        self.anim_speed = 4  # Ticks per leg step frame
        self.anim_timer = random.randint(0, self.anim_speed - 1)
        self.anim_frame_idx = random.randint(0, 3)
        self.walk_frames_right = [
            NORM_ROBOT_STANDING_LEGS,
            NORM_ROBOT_STRIDE_B_LEGS,
            NORM_ROBOT_STANDING_LEGS,
            NORM_ROBOT_STRIDE_A_LEGS,
        ]
        self.walk_frames_left = [
            NORM_ROBOT_STANDING_LEGS,
            NORM_ROBOT_STRIDE_A_LEGS,
            NORM_ROBOT_STANDING_LEGS,
            NORM_ROBOT_STRIDE_B_LEGS,
        ]
        self.walk_frames_vert = [
            NORM_ROBOT_STANDING_LEGS,
            NORM_ROBOT_STRIDE_A_LEGS,
            NORM_ROBOT_STANDING_LEGS,
            NORM_ROBOT_STRIDE_B_LEGS,
        ]

        # Eyeball cycling animation configuration (scanning visor)
        self.eye_anim_speed = 3  # Ticks per eye scan frame
        self.eye_timer = random.randint(0, self.eye_anim_speed - 1)
        self.eye_frame_idx = random.randint(0, 5)
        # Cycle left: Center -> Mid-Left -> Far-Left -> Blank (wrap) -> Far-Right -> Mid-Right
        self.eye_frames_left = [
            NORM_EYE_CENTER,
            NORM_EYE_MID_LEFT,
            NORM_EYE_FAR_LEFT,
            NORM_EYE_BLANK,
            NORM_EYE_FAR_RIGHT,
            NORM_EYE_MID_RIGHT,
        ]
        # Cycle right: Center -> Mid-Right -> Far-Right -> Blank (wrap) -> Far-Left -> Mid-Left
        self.eye_frames_right = [
            NORM_EYE_CENTER,
            NORM_EYE_MID_RIGHT,
            NORM_EYE_FAR_RIGHT,
            NORM_EYE_BLANK,
            NORM_EYE_FAR_LEFT,
            NORM_EYE_MID_LEFT,
        ]

        # put in groups
        object.Class_Obj.__init__(self, pos, speed, groups + [globals.ROBOTS, globals.COLLIDABLE])
    def levelUp(self, level):
        # increase number of bullets by level
        # increase speed by % per level
        # reduce max heat time by % per level
        self.max_bullets += level
        self.speed_mag = (1.0 + 0.02 * level) * self.speed_mag 
        if level < 40:
            self.gunheatcnt_max = (1.0 - (0.02 * level)) * self.gunheatcnt_max 
        else:
            # dont let gunheat go lower than 90% or robots wont move
            # they will constantly fire lol.
            self.gunheatcnt_max = (1.0 - (0.90)) * self.gunheatcnt_max 
        if (self.gunheatcnt_max < 0):
            self.gunheatcnt_max
    def collide(self, victim):
        if victim not in globals.PLAYER.sprites():
            if (globals.SOUNDS_ON == True): 
                #depending on victim play diff sound
                if victim in globals.BULLETS.sprites():
                    sounds.playSound(sounds.robotShotSound)
                    for a in globals.PLAYER.sprites():
                        if victim.shooter_obj == a:
                            globals.SCORE += 1
                else:
                    sounds.playSound(sounds.robotExplodeSound) 
                if globals.android:
                  globals.android.vibrate(2)
            self.killState = True
    def updateMovement(self):
        # build a list of directions that contain collidable
        # objects at the size of this object in all 8 ways

        lRects = []
        rect = copy.deepcopy(self.rect)
        height = self.rect[3]
        #move the rect one rect up
        rect[1] = rect[1] - height 
        lRects.append(rect)

        rect = copy.deepcopy(self.rect)
        height = self.rect[3]
        #move the rect one rect down
        rect[1] = rect[1] + height 
        lRects.append(rect)

        rect = copy.deepcopy(self.rect)
        width = self.rect[2]
        # move the rect one rect to left
        rect[0] = rect[0] - width 
        lRects.append(rect)

        rect = copy.deepcopy(self.rect)
        width = self.rect[2]
        # move the rect one rect to right
        rect[0] = rect[0] + width 
        lRects.append(rect)

        rect = copy.deepcopy(self.rect)
        width = self.rect[2]
        height = self.rect[3]
        #move the rect to top left
        rect[0] = rect[0] - width 
        rect[1] = rect[1] - height 
        lRects.append(rect)

        rect = copy.deepcopy(self.rect)
        width = self.rect[2]
        height = self.rect[3]
        #move the rect to top right
        rect[0] = rect[0] + width 
        rect[1] = rect[1] - height 
        lRects.append(rect)

        rect = copy.deepcopy(self.rect)
        width = self.rect[2]
        height = self.rect[3]
        #move the rect to bottom left
        rect[0] = rect[0] - width 
        rect[1] = rect[1] + height 
        lRects.append(rect)

        rect = copy.deepcopy(self.rect)
        width = self.rect[2]
        height = self.rect[3]
        #move the rect to bottom right
        rect[0] = rect[0] + width 
        rect[1] = rect[1] + height 
        lRects.append(rect)

        #check for hits on radar rects
        #   to objects
        hitList = []
        for a in lRects:
            hit = 0
            for b in globals.OBJECTS:
                hit = a.colliderect(b.rect)
                if (hit == True):
                    break
            hitList.append(hit)

        #build a list of hitLists that are zero
        pickDir = []
        for i in range(0, len(hitList)):
            if (hitList[i] == False):
                pickDir.append(i)

        # movement hysterisis:
        # if cant find a direction dont move
        # add hysterisis to movement to prevent "jitter"
        # lean on old reliable direction for next move
        if self.lastDir in pickDir:
            direction = self.lastDir
            # avoidance:
            # check to see if we can move away from objects
            # near us - if not then leave direction
            # at same as last
            for i in range(0, len(hitList)):
                if (hitList[i] == True):
                    # is opposite direction blocked?
                    if (hitList[movement.number_to_opposite_direction[i]] \
                        == False):
                        #pick it
                        direction = movement.number_to_opposite_direction[i]
                        break
        else:
            if len(pickDir) > 0:
                index = random.randint(0,len(pickDir) - 1)
                direction = pickDir[index]
            else:
                direction = movement.dirEnum.NONE
        self.lastDir = direction

        speed_vect = movement.number_to_speed_vect[direction]
        self.speed[0] = self.speed_mag * speed_vect[0]
        self.speed[1] = self.speed_mag * speed_vect[1]

        if (self.gunHeatCnt > 1):
            self.gunHeatCnt -= 1 
        else:
            self.gunHeatCnt = 0.0

        if (self.gunHeatCnt == 0.0):
            self.gunHeatCnt = random.uniform(self.gunheatcnt_max / 2, self.gunheatcnt_max)
            # Create a bullet if player bullet limit not exceeded AND robots are not startled
            if (self.bullets < self.max_bullets) and (globals.ROBOT_STARTLE_TIMER <= 0):
                # Make robot bullets red
                bullets.Class_Bullet(self, self.speed, direction, bullets.robot_bullet_color_list_pts)
                # Stop robot movement while shooting
                self.speed[0] = 0.0
                self.speed[1] = 0.0
                self.bullets += 1

        # 1. Update walking leg animation based on robot velocity
        if self.speed[0] == 0.0 and self.speed[1] == 0.0:
            active_legs = NORM_ROBOT_STANDING_LEGS
            self.anim_timer = 0
        else:
            self.anim_timer += 1
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame_idx = (self.anim_frame_idx + 1) % len(self.walk_frames_vert)

            if self.speed[0] < -0.01:
                active_legs = self.walk_frames_left[self.anim_frame_idx]
            elif self.speed[0] > 0.01:
                active_legs = self.walk_frames_right[self.anim_frame_idx]
            else:
                active_legs = self.walk_frames_vert[self.anim_frame_idx]

        # 2. Update eyeball cycling animation (cycles left when moving left, cycles right when moving right)
        if self.speed[0] < -0.01:
            # Moving left: cycle eye to the left
            self.eye_timer += 1
            if self.eye_timer >= self.eye_anim_speed:
                self.eye_timer = 0
                self.eye_frame_idx = (self.eye_frame_idx + 1) % len(self.eye_frames_left)
            active_eye = self.eye_frames_left[self.eye_frame_idx]
        elif self.speed[0] > 0.01:
            # Moving right: cycle eye to the right
            self.eye_timer += 1
            if self.eye_timer >= self.eye_anim_speed:
                self.eye_timer = 0
                self.eye_frame_idx = (self.eye_frame_idx + 1) % len(self.eye_frames_right)
            active_eye = self.eye_frames_right[self.eye_frame_idx]
        else:
            # Moving vertically or stationary: eye centered
            self.eye_timer = 0
            self.eye_frame_idx = 0
            active_eye = NORM_EYE_CENTER

        # 3. Assemble active robot polygons
        self.list_polygon_pts[0] = (
            NORM_ROBOT_UPPER_LEFT + active_legs + NORM_ROBOT_UPPER_RIGHT
        )
        self.list_polygon_pts[1] = active_eye




