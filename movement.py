import misc

#movement vectors
up =            [0.0,   -1.0]
down =          [0.0,   1.0]
left =          [-1.0,  0.0]
right =         [1.0,   0.0]
upleft =        [-.707, -.707]
upright =       [.707,  -.707]
downleft =      [-.707, .707]
downright =     [.707,  .707]
none =          [0.0,   0.0]

#create enum for directions to avoid using hardcoded numbers
dirEnum = misc.enum('UP','DOWN','LEFT','RIGHT','UPLEFT','UPRIGHT','DOWNLEFT','DOWNRIGHT','NONE')

number_to_speed_vect = {dirEnum.UP:up,dirEnum.DOWN:down,\
                        dirEnum.LEFT:left,dirEnum.RIGHT:right,\
                        dirEnum.UPLEFT:upleft,dirEnum.UPRIGHT:upright,\
                        dirEnum.DOWNLEFT:downleft,dirEnum.DOWNRIGHT:downright,\
                        dirEnum.NONE:none}

number_to_opposite_direction = [dirEnum.DOWN,dirEnum.UP,\
                                dirEnum.RIGHT,dirEnum.LEFT,\
                                dirEnum.DOWNRIGHT,dirEnum.DOWNLEFT,\
                                dirEnum.UPRIGHT,dirEnum.UPLEFT]

