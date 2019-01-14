import globals
import object
import copy
import movement
import sounds
import math
import misc

#define otto
otto_polygon_max_cnt = (80.0,70.0)
otto_polygon_pts = [[20.0,0.0],\
                    [20.0,10.0],\
                    [10.0,10.0],\
                    [10.0,20.0],\
                    [0.0,20.0],\
                    [0.0,50.0],\
                    [10.0,50.0],\
                    [10.0,60.0],\
                    [20.0,60.0],\
                    [20.0,70.0],\
                    [60.0,70.0],\
                    [60.0,60.0],\
                    [70.0,60.0],\
                    [70.0,50.0],\
                    [80.0,50.0],\
                    [80.0,20.0],\
                    [70.0,20.0],\
                    [70.0,10.0],\
                    [60.0,10.0],\
                    [60.0,0.0],\
                    [20.0,0.0]]
otto_eye1_polygon_pts = [[20.0,20.0],\
                         [20.0,30.0],\
                         [30.0,30.0],\
                         [30.0,20.0],
                         [20.0,20.0]]
otto_eye2_polygon_pts = [[50.0,20.0],\
                         [50.0,30.0],\
                         [60.0,30.0],\
                         [60.0,20.0],\
                         [50.0,20.0]]
otto_mouth_polygon_pts = [[20.0,40.0],\
                         [20.0,50.0],\
                         [60.0,50.0],\
                         [60.0,40.0],\
                         [20.0,40.0]]
                          
# first list is line color
# second list is fill color
otto_polygon_colors = [[],\
                         globals.RED]
otto_eye1_polygon_colors = [[],\
                         globals.BLACK]
otto_eye2_polygon_colors = [[],\
                         globals.BLACK]
otto_mouth_polygon_colors = [[],\
                         globals.BLACK]
otto_pixel_size = [30.0,30.0]
otto_start_pos = [0 + globals.SCREENSIZE[0] / 10.0, globals.SCREENSIZE[1] / 2.0]

#speed in pixels per second
otto_speed_mag = globals.OTTO_OBJECT_SPEED

#time in seconds before otto appears
ottoTimerReload = 30.0

#count in fps to rotate otto
ottoRotateTimer = 15.0

#normalize points so that x,y are percent of relative max
for i in range(len(otto_polygon_pts)):
    otto_polygon_pts[i][0] /= otto_polygon_max_cnt[0] 
    otto_polygon_pts[i][1] /= otto_polygon_max_cnt[1] 
for i in range(len(otto_eye1_polygon_pts)):
    otto_eye1_polygon_pts[i][0] /= otto_polygon_max_cnt[0] 
    otto_eye1_polygon_pts[i][1] /= otto_polygon_max_cnt[1] 
for i in range(len(otto_eye2_polygon_pts)):
    otto_eye2_polygon_pts[i][0] /= otto_polygon_max_cnt[0] 
    otto_eye2_polygon_pts[i][1] /= otto_polygon_max_cnt[1] 
for i in range(len(otto_mouth_polygon_pts)):
    otto_mouth_polygon_pts[i][0] /= otto_polygon_max_cnt[0] 
    otto_mouth_polygon_pts[i][1] /= otto_polygon_max_cnt[1] 

otto_polygon_list_pts = [otto_polygon_pts[:],otto_eye1_polygon_pts[:],otto_eye2_polygon_pts[:],\
                         otto_mouth_polygon_pts[:]] 
otto_color_list_pts = [otto_polygon_colors[:],otto_eye1_polygon_colors[:],otto_eye2_polygon_colors[:],\
                       otto_mouth_polygon_colors[:]]

# class to display a real object - inherits low level Obj class
class Class_Otto(object.Class_Obj):
    def __init__(self, speed = [0.0,0.0], pos = otto_start_pos, size = otto_pixel_size,\
                 list_polygon_pts = otto_polygon_list_pts,\
                 list_colors = otto_color_list_pts, groups = []):
        self.blitImage = None
        self.angle = 0.0
        self.size = copy.deepcopy(size)
        self.list_polygon_pts =  copy.deepcopy(list_polygon_pts) 
        self.list_colors = copy.deepcopy(list_colors)
        self.rotateTimer = ottoRotateTimer 
        # put in groups
        object.Class_Obj.__init__(self, pos, speed, groups + [globals.OTTO, globals.COLLIDABLE])
    def collide(self, victim):
        pass
        # Otto cannot die
        # self.killState = True
    def updateMovement(self, player_obj):
        # head for player
        # calculate a vector from otto to player
        # then pick closest vector movement to get there
        player_pos = player_obj.pos
        speed_vect = [0.0,0.0]
        speed_vect[0] = player_pos[0] - self.pos[0]
        speed_vect[1] = player_pos[1] - self.pos[1]
        # normalize the vector
        hypo = math.sqrt(math.pow(speed_vect[0],2) + math.pow(speed_vect[1],2))
        if (hypo > 0.0):
          speed_vect[0] = speed_vect[0]/hypo
          speed_vect[1] = speed_vect[1]/hypo
          self.speed[0] = otto_speed_mag * speed_vect[0]
          self.speed[1] = otto_speed_mag * speed_vect[1]
        # rotate
        if (self.rotateTimer > 0):
            self.rotateTimer -= 1
        else:
            self.rotateTimer = ottoRotateTimer 
            self.angle += math.pi / 4.0
            misc.rotate(self.angle,self.list_polygon_pts)


