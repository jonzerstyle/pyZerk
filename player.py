import globals
import robots
import object
import copy
import movement
import sounds
import bullets

# Define player base dimensions
player_polygon_max_cnt = (70.0, 140.0)

def normalize_points(pts):
    return [[p[0] / player_polygon_max_cnt[0], p[1] / player_polygon_max_cnt[1]] for p in pts]

# Modular polygon components (raw grid scale: 70 x 140)
# 1. Head sections
HEAD_LEFT = [[20.0, 3.0], [20.0, 23.0], [27.0, 23.0]]
HEAD_RIGHT = [[40.0, 26.0], [40.0, 22.0], [51.0, 22.0], [51.0, 3.0], [20.0, 3.0]]

# 2. Resting arm poses (clean offset from torso to prevent self-intersecting scanlines)
DEFAULT_LEFT_ARM = [[27.0, 27.0], [12.0, 27.0], [3.0, 37.0], [3.0, 63.0], [17.0, 63.0], [17.0, 40.0]]
DEFAULT_RIGHT_ARM = [[51.0, 40.0], [51.0, 64.0], [64.0, 64.0], [64.0, 37.0], [54.0, 26.0]]

# 3. Leg animation frames (connected between left waist [20, 40] and right waist [48, 40])
# Standing / idle pose: both legs planted upright on the ground (y=134)
STANDING_LEGS = [
    [20.0, 40.0],
    [20.0, 134.0],
    [31.0, 134.0],
    [31.0, 85.0],
    [37.0, 85.0],
    [37.0, 134.0],
    [48.0, 134.0],
    [48.0, 40.0]
]

# Stride A: left leg forward/down to 134, right leg kicked backward (107..120)
STRIDE_A_LEGS = [
    [20.0, 40.0],
    [20.0, 134.0],
    [40.0, 134.0],
    [40.0, 120.0],
    [56.0, 120.0],
    [56.0, 107.0],
    [48.0, 107.0],
    [48.0, 40.0]
]

# Passing pose A: left leg moving back, right leg swinging forward
PASSING_LEGS_A = [
    [20.0, 40.0],
    [24.0, 134.0],
    [35.0, 134.0],
    [35.0, 95.0],
    [39.0, 95.0],
    [45.0, 124.0],
    [52.0, 115.0],
    [48.0, 40.0]
]

# Stride B: right leg forward/down to 134, left leg kicked backward (107..120)
STRIDE_B_LEGS = [
    [20.0, 40.0],
    [20.0, 107.0],
    [12.0, 107.0],
    [12.0, 120.0],
    [28.0, 120.0],
    [28.0, 134.0],
    [48.0, 134.0],
    [48.0, 40.0]
]

# Passing pose B: right leg moving back, left leg swinging forward
PASSING_LEGS_B = [
    [20.0, 40.0],
    [16.0, 115.0],
    [23.0, 124.0],
    [29.0, 95.0],
    [33.0, 95.0],
    [33.0, 134.0],
    [44.0, 134.0],
    [48.0, 40.0]
]

# 4. Aiming arm poses (thick, solid arms matching resting arm width)
LEFT_AIM = {
    # Aiming LEFT: prominent reach to -8.0, matching resting arm thickness (y=22..42)
    movement.dirEnum.LEFT: [
        [27.0, 27.0], [14.0, 22.0], [-8.0, 22.0], [-8.0, 42.0], [17.0, 42.0], [17.0, 40.0]
    ],
    # Aiming UPLEFT: prominent diagonal reach
    movement.dirEnum.UPLEFT: [
        [27.0, 27.0], [14.0, 22.0], [-2.0, 0.0], [-10.0, 8.0], [17.0, 42.0], [17.0, 40.0]
    ],
    # Aiming DOWNLEFT: clean 0-fuzz diagonal reach
    movement.dirEnum.DOWNLEFT: [
        [27.0, 27.0], [10.0, 22.0], [-10.0, 45.0], [0.0, 55.0], [17.0, 42.0], [17.0, 40.0]
    ],
    # Aiming UP: vertical left arm
    movement.dirEnum.UP: [
        [27.0, 27.0], [18.0, 27.0], [18.0, -10.0], [5.0, -10.0], [5.0, 38.0], [17.0, 40.0]
    ],
    # Aiming DOWN: clean vertical left arm (0-fuzz)
    movement.dirEnum.DOWN: [
        [27.0, 27.0], [12.0, 27.0], [3.0, 27.0], [3.0, 80.0], [17.0, 80.0], [17.0, 40.0]
    ]
}

RIGHT_AIM = {
    # Aiming RIGHT: prominent reach to 78.0, matching resting arm thickness (y=22..42)
    movement.dirEnum.RIGHT: [
        [51.0, 42.0], [78.0, 42.0], [78.0, 22.0], [54.0, 22.0], [54.0, 26.0]
    ],
    # Aiming UPRIGHT: prominent diagonal reach
    movement.dirEnum.UPRIGHT: [
        [51.0, 42.0], [80.0, 8.0], [72.0, 0.0], [54.0, 22.0], [54.0, 26.0]
    ],
    # Aiming DOWNRIGHT: clean 0-fuzz diagonal reach
    movement.dirEnum.DOWNRIGHT: [
        [51.0, 40.0], [68.0, 52.0], [78.0, 42.0], [58.0, 22.0], [54.0, 26.0]
    ],
    # Aiming UP: vertical right arm
    movement.dirEnum.UP: [
        [51.0, 40.0], [66.0, 40.0], [66.0, -10.0], [54.0, -10.0], [54.0, 26.0]
    ],
    # Aiming DOWN: clean vertical right arm (0-fuzz)
    movement.dirEnum.DOWN: [
        [51.0, 40.0], [51.0, 80.0], [64.0, 80.0], [64.0, 26.0], [54.0, 26.0]
    ]
}

# Pre-normalized modular parts (computed once, never mutated in-place)
NORM_HEAD_LEFT = normalize_points(HEAD_LEFT)
NORM_HEAD_RIGHT = normalize_points(HEAD_RIGHT)
NORM_DEFAULT_LEFT_ARM = normalize_points(DEFAULT_LEFT_ARM)
NORM_DEFAULT_RIGHT_ARM = normalize_points(DEFAULT_RIGHT_ARM)

NORM_STANDING_LEGS = normalize_points(STANDING_LEGS)
NORM_STRIDE_A_LEGS = normalize_points(STRIDE_A_LEGS)
NORM_PASSING_LEGS_A = normalize_points(PASSING_LEGS_A)
NORM_STRIDE_B_LEGS = normalize_points(STRIDE_B_LEGS)
NORM_PASSING_LEGS_B = normalize_points(PASSING_LEGS_B)

NORM_LEFT_AIM = {k: normalize_points(v) for k, v in LEFT_AIM.items()}
NORM_RIGHT_AIM = {k: normalize_points(v) for k, v in RIGHT_AIM.items()}

# Build default player polygon in normalized coordinates
player_polygon_pts = copy.deepcopy(
    NORM_HEAD_LEFT + NORM_DEFAULT_LEFT_ARM + NORM_STANDING_LEGS + NORM_DEFAULT_RIGHT_ARM + NORM_HEAD_RIGHT
)

# Colors: first is outline, second is fill
player_polygon_colors = [globals.BLACK, globals.GREEN]
player_pixel_size = [15.0, 24.0]
player_start_pos = [0 + globals.SCREENSIZE[0] / 10.0, globals.SCREENSIZE[1] / 2.0]

# Speed in pixels per second
player_speed_mag = globals.PLAYER_OBJECT_SPEED * 1.25

player_polygon_list_pts = [player_polygon_pts[:], []]
player_color_list_pts = [player_polygon_colors[:], []]
player_max_bullets = 100

# Cooldown time for gun in frame counts
player_gunheatcnt_max = 10.0


# Class to display the player object - inherits low level Class_Obj
class Class_Player(object.Class_Obj):
    def __init__(self, pos, speed, size=player_pixel_size,
                 list_polygon_pts=player_polygon_list_pts,
                 list_colors=player_color_list_pts, groups=[]):
        self.blitImage = None
        self.angle = 0.0
        self.size = copy.deepcopy(size)
        self.list_polygon_pts = copy.deepcopy(list_polygon_pts)
        self.list_colors = copy.deepcopy(list_colors)
        self.bullets = 0
        self.max_bullets = player_max_bullets
        self.gunHeatCnt = 0

        # Animation and aiming state
        self.facing_dir = movement.dirEnum.RIGHT
        self.anim_timer = 0
        self.anim_speed = 3  # Ticks per leg step frame
        self.anim_frame_idx = 0
        self.run_frames_right = [NORM_STRIDE_A_LEGS, NORM_PASSING_LEGS_A, NORM_STRIDE_B_LEGS, NORM_PASSING_LEGS_B]
        self.run_frames_left = [NORM_STRIDE_B_LEGS, NORM_PASSING_LEGS_B, NORM_STRIDE_A_LEGS, NORM_PASSING_LEGS_A]
        self.aim_hold_timer = 0
        self.current_aim_dir = None

        # Put in groups
        object.Class_Obj.__init__(self, pos, speed, groups + [globals.PLAYER, globals.COLLIDABLE])

    def collide(self, victim):
        if globals.SOUNDS_ON:
            sounds.playSound(sounds.playerDeathSound)
        self.killState = True

    def updateMovement(self, player_movement_dir, player_fire):
        speed_vect = movement.number_to_speed_vect[player_movement_dir]
        self.speed[0] = player_speed_mag * speed_vect[0]
        self.speed[1] = player_speed_mag * speed_vect[1]

        # Update horizontal facing direction based on movement
        if player_movement_dir in (movement.dirEnum.LEFT, movement.dirEnum.UPLEFT, movement.dirEnum.DOWNLEFT):
            self.facing_dir = movement.dirEnum.LEFT
        elif player_movement_dir in (movement.dirEnum.RIGHT, movement.dirEnum.UPRIGHT, movement.dirEnum.DOWNRIGHT):
            self.facing_dir = movement.dirEnum.RIGHT

        # Cool down gun heat
        if self.gunHeatCnt > 1:
            self.gunHeatCnt -= 1
        else:
            self.gunHeatCnt = 0.0

        # Cool down aim hold timer
        if self.aim_hold_timer > 0:
            self.aim_hold_timer -= 1
            if self.aim_hold_timer == 0:
                self.current_aim_dir = None

        if player_fire == "shoot":
            # Stop player movement while shooting
            self.speed[0] = 0.0
            self.speed[1] = 0.0

            # Determine firing direction: prefer current direction held, fallback to facing direction
            fire_dir = player_movement_dir if player_movement_dir != movement.dirEnum.NONE else self.facing_dir
            self.current_aim_dir = fire_dir
            self.aim_hold_timer = int(player_gunheatcnt_max)

            if self.gunHeatCnt == 0.0:
                self.gunHeatCnt = player_gunheatcnt_max
                # Create a bullet if bullet limit not exceeded
                if self.bullets < self.max_bullets:
                    bullets.Class_Bullet(self, self.speed, fire_dir)
                    self.bullets += 1

        # 1. Select active leg pose
        if self.speed[0] == 0.0 and self.speed[1] == 0.0:
            active_legs = NORM_STANDING_LEGS
            self.anim_timer = 0
        else:
            self.anim_timer += 1
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_frame_idx = (self.anim_frame_idx + 1) % len(self.run_frames_right)

            if self.facing_dir == movement.dirEnum.LEFT:
                active_legs = self.run_frames_left[self.anim_frame_idx]
            else:
                active_legs = self.run_frames_right[self.anim_frame_idx]

        # 2. Select active arm poses
        active_left_arm = NORM_DEFAULT_LEFT_ARM
        active_right_arm = NORM_DEFAULT_RIGHT_ARM

        if self.current_aim_dir is not None:
            aim_dir = self.current_aim_dir
            if aim_dir in (movement.dirEnum.LEFT, movement.dirEnum.UPLEFT, movement.dirEnum.DOWNLEFT):
                # Point left arm in the direction of fire
                active_left_arm = NORM_LEFT_AIM.get(aim_dir, NORM_DEFAULT_LEFT_ARM)
            elif aim_dir in (movement.dirEnum.RIGHT, movement.dirEnum.UPRIGHT, movement.dirEnum.DOWNRIGHT):
                # Point right arm in the direction of fire
                active_right_arm = NORM_RIGHT_AIM.get(aim_dir, NORM_DEFAULT_RIGHT_ARM)
            elif aim_dir in (movement.dirEnum.UP, movement.dirEnum.DOWN):
                # For vertical firing, point the arm matching current facing side
                if self.facing_dir == movement.dirEnum.LEFT:
                    active_left_arm = NORM_LEFT_AIM.get(aim_dir, NORM_DEFAULT_LEFT_ARM)
                else:
                    active_right_arm = NORM_RIGHT_AIM.get(aim_dir, NORM_DEFAULT_RIGHT_ARM)

        # 3. Assemble the full player polygon from pre-normalized parts directly
        self.list_polygon_pts[0] = (
            NORM_HEAD_LEFT + active_left_arm + active_legs + active_right_arm + NORM_HEAD_RIGHT
        )
