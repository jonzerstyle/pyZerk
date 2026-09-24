import os
import globals
import object
import copy
import misc
import pygame

#define wall
wall_polygon_max_cnt = (10.0,10.0)
wall_polygon_pts =      [[0.0,0.0],
                         [10.0,0.0],
                         [10.0,10.0],
                         [0.0,10.0],
                         [0.0,0.0]]
# first list is line color
# second list is fill color
wall_polygon_colors = [[],\
                       globals.BLUE]
wall_pixel_size = [10,10]
#normalize points so that x,y are percent of relative max
for i in range(len(wall_polygon_pts)):
    wall_polygon_pts[i][0] /= wall_polygon_max_cnt[0] 
    wall_polygon_pts[i][1] /= wall_polygon_max_cnt[1] 

wall_polygon_list_pts = [wall_polygon_pts[:]] 
wall_color_list_pts = [wall_polygon_colors[:]]

wall_image = None

def loadImages():
    global wall_image
    #load images here - because surface needs to have been created
    #load in the image to display
    for candidate in ["images/wall.png", "images/wall.bmp"]:
        path = misc.get_asset_path(candidate)
        if os.path.exists(path):
            try:
                wall_image = pygame.image.load(path)
                break
            except Exception:
                pass
    if wall_image is None:
        try:
            wall_image = pygame.image.load(misc.get_asset_path("images/wall.bmp"))
        except Exception:
            try:
                wall_image = pygame.image.load(misc.get_asset_path("images/wall.png"))
            except Exception:
                wall_image = pygame.Surface(wall_pixel_size)
                wall_image.fill(globals.BLUE)
    if pygame.display.get_surface() and wall_image:
        try:
            wall_image = wall_image.convert()
        except Exception:
            pass

# class to display a real object - inherits low level Obj class
class Class_Wall(object.Class_Obj):
    def __init__(self, pos, size = wall_pixel_size, \
                 list_polygon_pts = wall_polygon_list_pts,\
                 list_colors = wall_color_list_pts,\
                 groups = []):
        global wall_image
        if wall_image is None:
            loadImages()
        # if we are using an image scale it to the size we want
        self.blitImage = pygame.transform.smoothscale(wall_image, size)
        self.angle = 0.0
        self.size = copy.deepcopy(size)
        self.list_polygon_pts =  copy.deepcopy(list_polygon_pts) 
        self.list_colors = copy.deepcopy(list_colors)
        speed = [0,0]
        # put in groups
        object.Class_Obj.__init__(self, pos, speed, groups + [globals.WALLS, globals.COLLIDABLE])
        # draw once on init
        self.update()
    def collide(self, victim):
        #walls are not destructable - do not kill through collision
        #just redraw
        self.update()
        #self.killState = True
        pass
