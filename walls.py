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
                 wall_color = None,\
                 groups = []):
        if wall_color is not None:
            self.blitImage = pygame.Surface(size)
            self.blitImage.fill(wall_color)
        else:
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
        pass

# Green exit field - safe escape route to the next level
exit_polygon_colors = [[], globals.GREEN]
exit_color_list_pts = [exit_polygon_colors[:]]

class Class_ExitField(object.Class_Obj):
    def __init__(self, pos, size, direction, wall_color = None, groups = []):
        self.direction = direction
        self.angle = 0.0
        self.size = copy.deepcopy(size)
        self.list_polygon_pts = copy.deepcopy(wall_polygon_list_pts)
        self.list_colors = copy.deepcopy(exit_color_list_pts)
        self.blitImage = pygame.Surface(size)
        if wall_color is not None:
            self.blitImage.fill(wall_color)
        else:
            # Bright energetic green for exit field
            self.blitImage.fill((0, 230, 80))
            # Glowing core line through center
            if size[0] >= size[1]:  # Horizontal exit
                pygame.draw.line(self.blitImage, (200, 255, 220), (0, size[1] // 2), (size[0], size[1] // 2), 2)
            else:  # Vertical exit
                pygame.draw.line(self.blitImage, (200, 255, 220), (size[0] // 2, 0), (size[0] // 2, size[1]), 2)
        speed = [0, 0]
        object.Class_Obj.__init__(self, pos, speed, groups + [globals.EXITS, globals.COLLIDABLE])
        self.update()

    def update(self):
        super().update()
        # Generous doorway corridor hitbox so players entering or grazing the doorway
        # safely trigger escape without dying on the adjacent electrified wall edges
        buf = 4
        if self.direction == 'UP':
            self.rect = pygame.Rect(self.top_left_point[0] - buf, self.top_left_point[1], self.size[0] + 2 * buf, self.size[1] + buf)
        elif self.direction == 'DOWN':
            self.rect = pygame.Rect(self.top_left_point[0] - buf, self.top_left_point[1] - buf, self.size[0] + 2 * buf, self.size[1] + buf)
        elif self.direction == 'LEFT':
            self.rect = pygame.Rect(self.top_left_point[0], self.top_left_point[1] - buf, self.size[0] + buf, self.size[1] + 2 * buf)
        elif self.direction == 'RIGHT':
            self.rect = pygame.Rect(self.top_left_point[0] - buf, self.top_left_point[1] - buf, self.size[0] + buf, self.size[1] + 2 * buf)

    def collide(self, victim):
        # Exit fields are not destructible
        # If player touches, signal exit
        if victim in globals.PLAYER.sprites():
            globals.PENDING_EXIT = self.direction
        self.update()

