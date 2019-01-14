import globals
import robots
import object
import copy
import movement
import sounds
import bullets

#define player
player_polygon_max_cnt = (70.0,140.0)
player_polygon_pts = [[20.0,3.0],\
                     [20.0,23.0],\
                     [27.0,23.0],\
                     [27.0,27.0],\
                     [12.0,27.0],\
                     [3.0,37.0],\
                     [3.0,63.0],\
                     [20.0,63.0],\
                     [20.0,40.0],\
                     [20.0,134.0],\
                     [40.0,134.0],\
                     [40.0,120.0],\
                     [56.0,120.0],\
                     [56.0,107.0],\
                     [48.0,107.0],\
                     [48.0,40.0],\
                     [48.0,64.0],\
                     [64.0,64.0],\
                     [64.0,37.0],\
                     [54.0,26.0],\
                     [40.0,26.0],\
                     [40.0,22.0],\
                     [51.0,22.0],\
                     [51.0,3.0],\
                     [20.0,3.0]]
# first list is line color
# second list is fill color
player_polygon_colors = [globals.BLACK,\
                         globals.GREEN]
player_pixel_size = [15.0,24.0]
player_start_pos = [0 + globals.SCREENSIZE[0] / 10.0, globals.SCREENSIZE[1] / 2.0]

#speed in pixels per second
# set player speed at 1.25x robot speed
player_speed_mag = globals.PLAYER_OBJECT_SPEED * 1.25 

#normalize points so that x,y are percent of relative max
for i in range(len(player_polygon_pts)):
    player_polygon_pts[i][0] /= player_polygon_max_cnt[0] 
    player_polygon_pts[i][1] /= player_polygon_max_cnt[1] 

player_polygon_list_pts = [player_polygon_pts[:],[]] 
player_color_list_pts = [player_polygon_colors[:],[]]
player_max_bullets = 100

#cool down time for gun in frame counts
#help prevent bullets colliding with themselves on init
#if running at approx 30 frames per second then count of 30 
#give one second
player_gunheatcnt_max = 10.0

# class to display a real object - inherits low level Obj class
class Class_Player(object.Class_Obj):
    def __init__(self, pos, speed, size = player_pixel_size,\
                 list_polygon_pts = player_polygon_list_pts,\
                 list_colors = player_color_list_pts, groups = []):
        self.blitImage = None
        self.angle = 0.0
        self.size = copy.deepcopy(size)
        self.list_polygon_pts =  copy.deepcopy(list_polygon_pts) 
        self.list_colors = copy.deepcopy(list_colors)
        self.bullets = 0
        self.max_bullets = player_max_bullets
        self.gunHeatCnt = 0 
        # put in groups
        object.Class_Obj.__init__(self, pos, speed, groups + [globals.PLAYER, globals.COLLIDABLE])
    def collide(self, victim):
        if (globals.SOUNDS_ON == True):
            sounds.playSound(sounds.playerDeathSound) 
        self.killState = True
    def updateMovement(self, player_movement_dir, player_fire):
        speed_vect = movement.number_to_speed_vect[player_movement_dir]
        self.speed[0] = player_speed_mag * speed_vect[0]
        self.speed[1] = player_speed_mag * speed_vect[1]

        if (self.gunHeatCnt > 1):
            self.gunHeatCnt -= 1 
        else:
            self.gunHeatCnt = 0.0

        if (player_fire == "shoot"):
            # stop player movement while shooting
            self.speed[0] = 0.0
            self.speed[1] = 0.0
            if (self.gunHeatCnt == 0.0):
                self.gunHeatCnt = player_gunheatcnt_max
                #create a bullet - if player bullet no longer exists 
                if (self.bullets < self.max_bullets):
                    bullets.Class_Bullet(self, self.speed, player_movement_dir)
                    self.bullets += 1

