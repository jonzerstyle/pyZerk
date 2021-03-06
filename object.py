import pygame
import globals
import copy
import misc

# lowest level object class: that other sprites in the game will
# inherit
# --------------------------------------------------------------
# self.polygon_pts - is a x,y list of polygon pts in % numbers
# relative to top left corner of rectangle sprite object
# the size(x,y) must hold the max x y length of the rectangle
# that the sprite is contained in
class Class_Obj(pygame.sprite.Sprite):
    def __init__(self, pos, speed, groups = []):
        pygame.sprite.Sprite.__init__(self, groups + [globals.OBJECTS])
        self.pos = copy.deepcopy(pos)
        self.speed = copy.deepcopy(speed) # pixel movement per second
        self.killState = False
        self.update()
    def update(self):
        if self.killState == True:
            self.kill()
        self.pos[0] = misc.wrap(self.pos[0], 0, globals.SCREENSIZE[0])
        self.pos[1] = misc.wrap(self.pos[1], 0, globals.SCREENSIZE[1])
        self.pos[0] += self.speed[0] / globals.FPS
        self.pos[1] += self.speed[1] / globals.FPS
        # pts are defined in % from top left corner - in % of xsize and ysize of
        # a rectangle.
        # here in order to draw we need to find the screen position of the top 
        # left corner based on the center of the object
        # top left corner = obj_center_x,y - x,y size / 2 
        self.top_left_point = copy.deepcopy(self.pos)
        for i in range(len(self.pos)):
            self.top_left_point[i] = self.pos[i] - (self.size[i]) / 2
        # update the sprite rect - so pygame can handle collisions
        self.rect = pygame.Rect(self.top_left_point[0], self.top_left_point[1],\
                                self.size[0], self.size[1])
    def draw(self, surface):
        dirtyrects = []
        if self.blitImage != None:
            # draw the image at rect location
            image_surface = surface.blit(self.blitImage, self.rect) 
            # rotate if needed
            if (self.angle != 0.0):
                #rotate it - unfortunately can only rotate surfaces and not
                #   polygons - so if thats needed it has to be manually
                #   before drawing in polygon section 
                image_surface = pygame.transform.rotate(image_surface, self.angle)
            dirtyrects.append(image_surface)
        else:
            # polygon pts just need top left corner added in before drawing
            # also scale up pts by coordinate size
            point_list = [[]]
            for i in range(len(self.list_polygon_pts)):
                # skip it if there are not at least 3 pts
                if len(self.list_polygon_pts[i]) > 3:
                    temp_points = []
                    point_list = self.list_polygon_pts[i]
                    # work on each point in list
                    for point in point_list:
                        temp_points.append([point[0] * self.size[0] + self.top_left_point[0], \
                                        point[1] * self.size[1] + self.top_left_point[1]])
                    # draw polygon
                    if len(self.list_colors[i][1]) > 1:
                        dirtyrects.append(pygame.draw.polygon(surface, self.list_colors[i][1], temp_points, 0))
                    # draw lines around polygon
                    if len(self.list_colors[i][0]) > 1:
                        dirtyrects.append(pygame.draw.lines(surface, self.list_colors[i][0], 0, temp_points, 1))
        return dirtyrects

