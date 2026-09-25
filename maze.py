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
        for i in range(0,self.xmax):
            for y in range(0,self.ymax):
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
        for x in range(1,self.xmax):
            for y in range(0,self.ymax):
                self.cells[x][y].neighbors[cellDirEnum.CUP] = self.cells[x - 1][y]
        # assign bottom neighbor
        for x in range(0,self.xmax - 1):
            for y in range(0,self.ymax):
                self.cells[x][y].neighbors[cellDirEnum.CDOWN] = self.cells[x + 1][y]

        # assign left neighbor
        for x in range(0,self.xmax):
            for y in range(1,self.ymax):
                self.cells[x][y].neighbors[cellDirEnum.CLEFT] = self.cells[x][y - 1]
        # assign right neighbor
        for x in range(0,self.xmax):
            for y in range(0,self.ymax - 1):
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

            for i in range(0, len(currentCell.neighbors)):
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
                for i in range(0, len(work_on_neighbor.neighbors)):
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

import pygame
import player

# class to create a maze of wall objects with escape route exits
class Class_Maze():
    def __init__(self, screensize, exit_dirs=None, wall_color=None, instantiate=True, entry_wall=None):
        mazex = 3
        mazey = 3
        self.screensize = screensize
        self.wallThickness = walls.wall_pixel_size[0]
        self.pmaze = Class_PerfectMaze(mazex, mazey, [])
        self.wall_color = wall_color
        self.entry_wall = entry_wall

        # Guarantee at least 1 exit, randomly up to 4 exits covering UP, DOWN, LEFT, RIGHT
        # Rule: The wall location closest to where the player entered is allocated LAST.
        if exit_dirs is None:
            all_walls = ['UP', 'DOWN', 'LEFT', 'RIGHT']
            if entry_wall in all_walls:
                other_walls = [w for w in all_walls if w != entry_wall]
                random.shuffle(other_walls)
                # Allocation order: other 3 walls first, entry_wall is the LAST allocation (4th)
                ordered_candidates = other_walls + [entry_wall]
            else:
                ordered_candidates = all_walls[:]
                random.shuffle(ordered_candidates)

            num_exits = random.randint(1, 4)
            self.exit_dirs = ordered_candidates[:num_exits]
        else:
            self.exit_dirs = list(exit_dirs)

        self.wall_specs = []
        self.exit_specs = []
        self.wall_objects = []
        self.exit_objects = []

        self.buildMazeSpecs(screensize, self.pmaze.cells)
        if instantiate:
            self.instantiateObjects(wall_color)

    def buildMazeSpecs(self, screen, cells):
        # Exit length is exactly twice the width of the player character
        exit_len = 2.0 * player.player_pixel_size[0]  # 30.0 pixels
        w_thick = self.wallThickness

        # Center coordinates for exits along outer perimeter
        mid_x = screen[0] / 2.0
        mid_y = screen[1] / 2.0

        top_exit_x = mid_x - exit_len / 2.0
        bot_exit_x = mid_x - exit_len / 2.0
        left_exit_y = mid_y - exit_len / 2.0
        right_exit_y = mid_y - exit_len / 2.0

        # 1. TOP Perimeter (Y = 0)
        if 'UP' in self.exit_dirs:
            self.wall_specs.append((0, 0, top_exit_x, w_thick))
            self.exit_specs.append((top_exit_x, 0, exit_len, w_thick, 'UP'))
            self.wall_specs.append((top_exit_x + exit_len, 0, screen[0] - (top_exit_x + exit_len), w_thick))
        else:
            self.wall_specs.append((0, 0, screen[0], w_thick))

        # 2. BOTTOM Perimeter (Y = screen[1] - w_thick)
        bot_y = screen[1] - w_thick
        if 'DOWN' in self.exit_dirs:
            self.wall_specs.append((0, bot_y, bot_exit_x, w_thick))
            self.exit_specs.append((bot_exit_x, bot_y, exit_len, w_thick, 'DOWN'))
            self.wall_specs.append((bot_exit_x + exit_len, bot_y, screen[0] - (bot_exit_x + exit_len), w_thick))
        else:
            self.wall_specs.append((0, bot_y, screen[0], w_thick))

        # 3. LEFT Perimeter (X = 0)
        if 'LEFT' in self.exit_dirs:
            self.wall_specs.append((0, 0, w_thick, left_exit_y))
            self.exit_specs.append((0, left_exit_y, w_thick, exit_len, 'LEFT'))
            self.wall_specs.append((0, left_exit_y + exit_len, w_thick, screen[1] - (left_exit_y + exit_len)))
        else:
            self.wall_specs.append((0, 0, w_thick, screen[1]))

        # 4. RIGHT Perimeter (X = screen[0] - w_thick)
        right_x = screen[0] - w_thick
        if 'RIGHT' in self.exit_dirs:
            self.wall_specs.append((right_x, 0, w_thick, right_exit_y))
            self.exit_specs.append((right_x, right_exit_y, w_thick, exit_len, 'RIGHT'))
            self.wall_specs.append((right_x, right_exit_y + exit_len, w_thick, screen[1] - (right_exit_y + exit_len)))
        else:
            self.wall_specs.append((right_x, 0, w_thick, screen[1]))

        # 5. Internal maze walls generated by DFS
        xsize = int((screen[0] - (w_thick * len(cells))) / len(cells))
        ysize = int((screen[1] - (w_thick * len(cells[0]))) / len(cells[0]))

        # Internal vertical walls
        for x in range(len(cells)):
            for y in range(len(cells[0]) - 1):
                if cells[x][y].walls[cellDirEnum.CRIGHT] == True:
                    wx = (y + 1) * xsize
                    wy = x * ysize
                    self.wall_specs.append((wx, wy, w_thick, ysize))

        # Internal horizontal walls
        for x in range(len(cells) - 1):
            for y in range(len(cells[0])):
                if cells[x][y].walls[cellDirEnum.CDOWN] == True:
                    wx = y * xsize
                    wy = (x + 1) * ysize
                    self.wall_specs.append((wx, wy, xsize, w_thick))

    def instantiateObjects(self, wall_color=None):
        """Instantiate real Pygame sprite objects for active gameplay."""
        self.wall_objects = []
        self.exit_objects = []
        for x, y, w, h in self.wall_specs:
            center = [x + w / 2.0, y + h / 2.0]
            w_obj = walls.Class_Wall(center, [w, h], wall_color=wall_color)
            self.wall_objects.append(w_obj)

        for x, y, w, h, d in self.exit_specs:
            center = [x + w / 2.0, y + h / 2.0]
            e_obj = walls.Class_ExitField(center, [w, h], d, wall_color=wall_color)
            self.exit_objects.append(e_obj)

    def render_to_surface(self, surface, offset=(0, 0), grey_mode=False):
        """Render the maze walls and exits directly to any surface at an offset (used for scroll transitions)."""
        wall_color = (160, 160, 160) if grey_mode else globals.BLUE
        exit_color = (120, 120, 120) if grey_mode else (0, 230, 80)
        ox, oy = int(offset[0]), int(offset[1])

        # Draw walls
        for x, y, w, h in self.wall_specs:
            rect = pygame.Rect(int(x + ox), int(y + oy), int(w), int(h))
            pygame.draw.rect(surface, wall_color, rect)
            if not grey_mode:
                if w > h:
                    pygame.draw.line(surface, (80, 140, 255), (rect.left, rect.centery), (rect.right, rect.centery), 1)
                else:
                    pygame.draw.line(surface, (80, 140, 255), (rect.centerx, rect.top), (rect.centerx, rect.bottom), 1)

        # Draw exit fields
        for x, y, w, h, d in self.exit_specs:
            rect = pygame.Rect(int(x + ox), int(y + oy), int(w), int(h))
            pygame.draw.rect(surface, exit_color, rect)
            if not grey_mode:
                if w > h:
                    pygame.draw.line(surface, (200, 255, 220), (rect.left, rect.centery), (rect.right, rect.centery), 2)
                else:
                    pygame.draw.line(surface, (200, 255, 220), (rect.centerx, rect.top), (rect.centerx, rect.bottom), 2)

    def destroy(self):
        for o in self.wall_objects:
            o.kill()
        for o in self.exit_objects:
            o.kill()


if __name__ == '__main__':
    x = Class_MCells()
    maze = Class_PerfectMaze(2,2,[])
    for x in range(0,len(maze.cells)):
        row = maze.cells[x]
        for y in range(0,len(row)):
            row[y].walls
            assert (row[y].walls != [True, True, True, True]),"all walls true!"
            assert (row[y].walls != [False, False, False, False]),"all walls false!"
