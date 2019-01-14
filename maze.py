import globals
import copy
import walls
import random
import misc

#create enum for cell directions 
cellDirEnum = misc.enum('CUP','CDOWN','CLEFT','CRIGHT')

# DFS algorithm from: http://www.mazeworks.com/mazegen/mazetut/index.htm 
#       create a CellStack (LIFO) to hold a list of cell locations 
#       set TotalCells = number of cells in grid 
#       choose a cell at random and call it CurrentCell 
#       set VisitedCells = 1 
#         
#       while VisitedCells < TotalCells 
#           find all neighbors of CurrentCell with all walls intact  
#           if one or more found 
#               choose one at random 
#               knock down the wall between it and CurrentCell 
#               push CurrentCell location on the CellStack 
#               make the new cell the neighbor cell selected 
#               add 1 to VisitedCells 
#           else 
#               pop the most recent cell entry off the CellStack 
#               make it CurrentCell endIf 
#       endWhile  
class Class_MCells():
    def __init__(self):
        # place walls on all cells
        # leave borders zero for now 
        # user of this class determines border settings
        #   directions are N,S,W,E
        self.walls = [True,True,True,True]
        self.neighbors = []
        self.NoneObj = 0
        # place a None element for each of four directions
        self.neighbors.append(None) 
        self.neighbors.append(None) 
        self.neighbors.append(None) 
        self.neighbors.append(None) 

class Class_PerfectMaze():
    def __init__(self, maze_x_max, maze_y_max, borders_grid):
        self.borders_grid = copy.deepcopy(borders_grid)
        self.xmax = copy.deepcopy(maze_x_max)
        self.ymax = copy.deepcopy(maze_y_max)
        cell_grid_rows = [] 
        for i in xrange(0,self.xmax):
            for y in xrange(0,self.ymax):
                cell_grid_rows.append(Class_MCells()) 

        # to make the cells more C like create 
        # row indexable array of y cells
        self.cells = []
        iter = 0 
        while (iter < (self.xmax * self.ymax)):
            # grab rows of cells at a time and place in list as a list item
            self.cells.append(cell_grid_rows[iter:(iter + self.ymax)])
            # iterate past row
            iter += self.ymax

        # assign a list of neighbor cell references
        # for each cell - notice borders for maze 
        # are implied by cell not having a neighbor
        # in a particular direction

        # assign top neighbor
        for x in xrange(1,self.xmax):
            for y in xrange(0,self.ymax):
                self.cells[x][y].neighbors[cellDirEnum.CUP] = self.cells[x - 1][y]
        # assign bottom neighbor
        for x in xrange(0,self.xmax - 1):
            for y in xrange(0,self.ymax):
                self.cells[x][y].neighbors[cellDirEnum.CDOWN] = self.cells[x + 1][y]

        # assign left neighbor
        for x in xrange(0,self.xmax):
            for y in xrange(1,self.ymax):
                self.cells[x][y].neighbors[cellDirEnum.CLEFT] = self.cells[x][y - 1]
        # assign right neighbor
        for x in xrange(0,self.xmax):
            for y in xrange(0,self.ymax - 1):
                self.cells[x][y].neighbors[cellDirEnum.CRIGHT] = self.cells[x][y + 1]

        totalCells = self.xmax * self.ymax
        # choose random cell
        currentCell = self.cells[random.randint(0, self.xmax - 1)][random.randint(0, self.ymax - 1)]
        visitedCells = 1
        cellStack = []
        while visitedCells < totalCells:
            #find neighbors of current with all walls intact
            good_neighbors_list = []
            good_neighbors_dir_list = []

            for i in xrange(0, len(currentCell.neighbors)):
                # not a null neighbor - i.e. border area
                if currentCell.neighbors[i] != None:
                    if (currentCell.neighbors[i].walls == [True, True, True, True]):
                        # add to list
                        good_neighbors_list.append(currentCell.neighbors[i])
                        # add index to list so we can discover direction later
                        good_neighbors_dir_list.append(i)
                
            #one or more good neighbors found
            if (len(good_neighbors_list) > 0):
                #randomly pick a good neighbor from list
                pick = random.randint(0, len(good_neighbors_list) - 1)
                work_on_neighbor = good_neighbors_list[pick]
                work_on_neighbor_dir = good_neighbors_dir_list[pick]

                #knock down the wall between the cells
                #for both cells
                currentCell.walls[work_on_neighbor_dir] = False
                #find currentCell index in neighbor we are working on
                for i in xrange(0, len(work_on_neighbor.neighbors)):
                    if (work_on_neighbor.neighbors[i] != None):
                        if (work_on_neighbor.neighbors[i] == currentCell):
                            # we found index
                            work_on_neighbor.walls[i] = False
                #push currentcell location on cellstack
                cellStack.append(currentCell)
                #make new cell the cell neighbor
                currentCell = work_on_neighbor
                #add one to visited cells
                visitedCells += 1
            #no good neighbors found
            else:
                #pop the most recent cellstack entry
                #make it the currentCell
                currentCell = cellStack.pop(-1)

# class to create a maze of wall objects
class Class_Maze():
    def __init__(self, screensize):
        #create maze
        # problem with maze when mazex is not same as mazey - TBD
        # when they are the same - seems to work ok
        mazex = 3
        mazey = 3
        self.wallThickness = walls.wall_pixel_size[0]
        #pass null for borders now - need to implement in PerfectMaze - TBD
        pmaze = Class_PerfectMaze(mazex, mazey, [])
        self.drawMaze(screensize, pmaze.cells)

    #x,y is top left coor to draw wall box
    #width is the width of the wall
    #heigh is the height of the wall
    def drawMazeWall(self, x, y, width, height):
        # first parameter is position
        # since x,y is top left 
        #   to get center
        #   pos[0] = x + width/2
        #   pos[1] = y + height/2
        walls.Class_Wall([x + width/2,y + height/2], [width,height])

    def drawMaze(self, screen, cells):
        xsize = int((screen[0] - (self.wallThickness * len(cells)))/ len(cells))
        ysize = int((screen[1] - (self.wallThickness * len(cells[0])))/ len(cells[0]))

        # iterate throw each cell from left to right
        # and draw walls if they exist
        for x in xrange(0,len(cells)):
            for y in xrange(0,len(cells[0])):
                for z in xrange(0,len(cells[x][y].walls)):
                    if (cells[x][y].walls[z] == True):
                        drawTL = [y * xsize, x * ysize]
                        #draw wall
                        if (z == cellDirEnum.CUP):
                            #top wall
                            #start at top left of cell
                            self.drawMazeWall(drawTL[0],drawTL[1],xsize,self.wallThickness) 
                        elif (z == cellDirEnum.CDOWN):
                            #bottom wall
                            #start at bottom left of cell
                            self.drawMazeWall(drawTL[0],drawTL[1] + ysize,xsize,self.wallThickness) 
                        elif (z == cellDirEnum.CLEFT):
                            #left wall
                            #start at top left of cell
                            self.drawMazeWall(drawTL[0],drawTL[1],self.wallThickness,ysize) 
                        elif (z == cellDirEnum.CRIGHT):
                            #right wall
                            #start at top right of cell
                            self.drawMazeWall(drawTL[0] + xsize,drawTL[1],self.wallThickness,ysize) 
    def destroy(self):
        pass

if __name__ == '__main__':
    x = Class_MCells()
    maze = Class_PerfectMaze(2,2,[])
    for x in xrange(0,len(maze.cells)):
        row = maze.cells[x]
        for y in xrange(0,len(row)):
            row[y].walls
            assert (row[y].walls != [True, True, True, True]),"all walls true!"
            assert (row[y].walls != [False, False, False, False]),"all walls false!"
