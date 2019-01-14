import globals
import object
import copy
import random
import movement
import sounds
import pygame
import misc
import bullets


#define robot
robot_polygon_max_cnt = (110.0,130.0)
robot_polygon_pts = [[30.0,0.0],\
                     [30.0,10.0],\
                     [20.0,10.0],\
                     [20.0,20.0],\
                     [10.0,20.0],\
                     [10.0,30.0],\
                     [0.0,30.0],\
                     [0.0,70.0],\
                     [20.0,70.0],\
                     [20.0,50.0],\
                     [30.0,50.0],\
                     [30.0,110.0],\
                     [20.0,110.0],\
                     [20.0,130.0],\
                     [50.0,130.0],\
                     [50.0,80.0],\
                     [60.0,80.0],\
                     [60.0,130.0],\
                     [90.0,130.0],\
                     [90.0,110.0],\
                     [80.0,110.0],\
                     [80.0,50.0],\
                     [90.0,50.0],\
                     [90.0,70.0],\
                     [110.0,70.0],\
                     [110.0,30.0],\
                     [100.0,30.0],\
                     [100.0,20.0],\
                     [90.0,20.0],\
                     [90.0,10.0],\
                     [80.0,10.0],\
                     [80.0,0.0],\
                     [30.0,0.0]]
robot_eyeball_pts= [[40.0,20.0],\
                    [40.0,30.0],\
                    [70.0,30.0],\
                    [70.0,20.0],\
                    [40.0,20.0]] 
# first list is line color
# second list is fill color
robot_polygon_colors = [globals.BLACK,\
                        globals.YELLOW]
robot_eyeball_colors = [[],\
                        globals.BLACK]
robot_pixel_size = [20.0,20.0]
#speed in pixels per second
robot_speed_mag = globals.ROBOT_OBJECT_SPEED
#normalize points so that x,y are percent of relative max
for i in range(len(robot_polygon_pts)):
    robot_polygon_pts[i][0] /= robot_polygon_max_cnt[0] 
    robot_polygon_pts[i][1] /= robot_polygon_max_cnt[1] 
for i in range(len(robot_eyeball_pts)):
    robot_eyeball_pts[i][0] /= robot_polygon_max_cnt[0]
    robot_eyeball_pts[i][1] /= robot_polygon_max_cnt[1]

robot_polygon_list_pts = [robot_polygon_pts[:],robot_eyeball_pts[:]] 
robot_color_list_pts = [robot_polygon_colors[:],robot_eyeball_colors[:]]

robot_max_bullets = 1
#cool down time for gun in frame counts
#help prevent bullets colliding with themselves on init
#if running at approx 30 frames per second then count of 30 
#give one second
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
        self.list_polygon_pts =  copy.deepcopy(list_polygon_pts) 
        self.list_colors = copy.deepcopy(list_colors)
        self.lastDir = movement.dirEnum.NONE
        self.gunHeatCnt = 0 
        self.bullets = 0
        self.max_bullets = robot_max_bullets
        self.speed_mag = robot_speed_mag 
        self.gunheatcnt_max = robot_gunheatcnt_max 
        # start gunheat at something reasonable so robots dont shoot right after creation
        self.gunHeatCnt = random.uniform(self.gunheatcnt_max / 2, self.gunheatcnt_max)
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
        for i in xrange(0, len(hitList)):
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
            for i in xrange(0, len(hitList)):
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
            #create a bullet - if player bullet no longer exists 
            if (self.bullets < self.max_bullets):
                #make robot bullets red
                bullets.Class_Bullet(self, self.speed, direction, bullets.robot_bullet_color_list_pts)
                # stop player movement while shooting
                self.speed[0] = 0.0
                self.speed[1] = 0.0
                self.bullets += 1



