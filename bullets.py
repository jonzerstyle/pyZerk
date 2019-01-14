import globals
import object
import player
import copy
import movement
import sounds
import math
import misc

#make polygon point straight up for now
#   plan is to transpose it to direction
bullet_polygon_max_cnt = (10.0,10.0)
bullet_polygon_pts =    [[3.0,0.0],
                         [7.0,0.0],
                         [7.0,10.0],
                         [3.0,10.0],
                         [3.0,0.0]]
bullet_pixel_size = [7.0,7.0]
bullet_polygon_colors = [globals.BLACK,\
                         globals.WHITE]
robot_bullet_polygon_colors = [globals.BLACK,\
                               globals.RED]
bullet_speed_mag = globals.BULLET_OBJECT_SPEED

#normalize points so that x,y are percent of relative max
for i in range(len(bullet_polygon_pts)):
    bullet_polygon_pts[i][0] /= bullet_polygon_max_cnt[0] 
    bullet_polygon_pts[i][1] /= bullet_polygon_max_cnt[1] 

bullet_polygon_list_pts = [bullet_polygon_pts[:]] 
bullet_color_list_pts = [bullet_polygon_colors[:]]
robot_bullet_color_list_pts = [robot_bullet_polygon_colors[:]]


class Class_Bullet(object.Class_Obj):
    # src_obj is object from which bullet was created
    def __init__(self, src_obj, speed, direction, \
                 list_colors = bullet_color_list_pts, \
                 size = bullet_pixel_size,\
                 list_polygon_pts = bullet_polygon_list_pts,\
                 groups = []):
        self.blitImage = None
        if (direction == movement.dirEnum.NONE):
            #if a direction is not indicated dont fire
            #  kill yourself
            self.killState = True
            return

        self.size = copy.deepcopy(size)
        #needed deepcopy here... guess if its more than one deep have to deepcopy
        self.list_polygon_pts = copy.deepcopy(list_polygon_pts) 
        self.list_colors = copy.deepcopy(list_colors)

        # keep a reference to obj shooter so when bullet is done
        # we can indicate bullet has been removed
        self.shooter_obj = src_obj

        # place bullet with direction vector from source object center
        #   if the direction is purely left or right then dont modify y
        #       make x = 1/2 src obj x + 1/2 bullet width
        #   if the direction is purely up or down then make x = 1/4 of src obj 
        #       width, make y = 1/2 src obj height + 1/2 bullet height
        #   if the direction is diagonal then make y = 1/4 src obj height +
        #       plus 1/2 bullet width       
        #       make x = 1/2 src obj width + 1/2 bullet width
        #   Also: rotate sprite image depending on orientation
        #       it defaults to up - so if direction is up or down
        #           dont worry about it
        #   Transformation equations:
        #   Px' = Px * cos theta - Py * sin theta
        #   Py' = Py * cos theta + Px * sin theta
        pos = copy.deepcopy(src_obj.pos)
        angle = 0.0
        if (direction == movement.dirEnum.LEFT) | (direction == movement.dirEnum.RIGHT):
            angle = math.pi / 2.0 #90 deg to make it horizontal
            if (direction == movement.dirEnum.LEFT):
                sign = [-1.0,1.0]
            else:
                sign = [1.0,1.0]
            pos[0] += sign[0] * (0.5 * src_obj.size[0] + 0.5 * size[0])
        elif (direction == movement.dirEnum.UP) | (direction == movement.dirEnum.DOWN):
            if (direction == movement.dirEnum.UP):
                sign = [1.0,-1.0]
            else:
                sign = [1.0,1.0]
            pos[0] += sign[0] * (0.25 * src_obj.size[0])
            pos[1] += sign[1] * (0.5 * src_obj.size[1] + 0.5 * size[1])
        else:
            if (direction == movement.dirEnum.UPLEFT):
                sign = [-1.0,-1.0]
                angle = - math.pi / 4.0 
            elif (direction == movement.dirEnum.UPRIGHT):
                sign = [1.0,-1.0]
                angle = math.pi / 4.0 
            elif (direction == movement.dirEnum.DOWNLEFT):
                sign = [-1.0,1.0]
                angle = math.pi / 4.0 
            elif (direction == movement.dirEnum.DOWNRIGHT):
                sign = [1.0,1.0]
                angle = - math.pi / 4.0 
            pos[0] += sign[0] * (0.5 * src_obj.size[0] + 0.5 * size[0])
            pos[1] += sign[1] * (0.25 * src_obj.size[1] + 0.5 * size[1])

        misc.rotate(angle, self.list_polygon_pts)

        # put in groups
        object.Class_Obj.__init__(self, pos, speed, groups + [globals.BULLETS, globals.COLLIDABLE])
        # movement direction never changes after creation - so no one should call
        # movement direction except for object itself
        self.updateMovement(direction)

        # play sound
        if src_obj in globals.ROBOTS:
            sounds.playSound(sounds.robotGunSound)
        else:
            sounds.playSound(sounds.playerGunSound)
    def collide(self, victim):
        #indicate to shooter that bullet is gone
        self.shooter_obj.bullets -= 1
        if victim in globals.BULLETS.sprites():
            sounds.playSound(sounds.bulletClashSound)
        self.killState = True
    def updateMovement(self, movement_dir):
        speed_vect = movement.number_to_speed_vect[movement_dir]
        self.speed[0] = bullet_speed_mag * speed_vect[0]
        self.speed[1] = bullet_speed_mag * speed_vect[1]

