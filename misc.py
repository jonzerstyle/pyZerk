import pygame
import math

def hang():
    #wait for a keypress
    while (pygame.event.wait().type != pygame.KEYDOWN): 
        pass

def wrap(num, start, end):
    while num < start:
        num += end - start
    while num > end:
        num -= end - start
    return num

# return a list of where to put obj evenly
# distributed within pixelMax space
# xslots is number of slots to place on x axis
# yslots is number of slots to place on y axis
def distPoints(pixelMax, xslots, yslots):
    assert ((xslots > 0) & (yslots > 0)), "slots have to be > 0"
    retList = []
    # distribute x pts - add 2 to total so that we
    # wont put items on extreme ends of scale
    xslots += 1
    yslots += 1
    placementx = 0.0
    for i in xrange(0, xslots):
        placementx += pixelMax[0] / xslots
        placementy = 0.0
        for j in xrange(0, yslots):
            placementy += pixelMax[1] / yslots
            if ((i != (xslots - 1)) & (j != (yslots - 1))): 
                retList.append([int(placementx), int(placementy)])
    return retList

def rotate(angle, list_polygon_pts):
    #in order to transform properly we need to bring 
    #polygon to origin: just subtract x distance to center from xs
    #  subtract y distance to center from ys
    #since polygon points are normalized we only need to use 0.5
    # * optimization - skip all this math if angle is zero!
    if (angle != 0.0):
        for list in list_polygon_pts:
            for point in list:
                point[0] -= 0.5
                point[1] -= 0.5
    
        #transform polygons based on angle
        for list in list_polygon_pts:
            for point in list:
                new_point = [0,0]
                new_point[0] = point[0] * math.cos(angle) - point[1] * math.sin(angle)
                new_point[1] = point[1] * math.cos(angle) + point[0] * math.sin(angle)
                #point = copy.deepcopy(new_point)
                #why does it assign new value if each element is assigned
                #versus just copying?
                #   it is because point is just a pointer to the data
                #   to actually change the data the pointer must be 
                #   subscripted
                point[:] = new_point[:]
    
        #point is at origin move it back to its original position
        for list in list_polygon_pts:
            for point in list:
                point[0] += 0.5
                point[1] += 0.5


#usage:
# x = enum('A','B','C')
# x.A == 0 and so on
def enum(*args, **kwargs):
    return type('Enum', (), dict((y, x) for x, y in enumerate(args), **kwargs))
