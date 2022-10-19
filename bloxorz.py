from copy import copy, deepcopy
from math import sqrt
from random import choice, choices, randint, randrange, random
import sys
from typing import List, Tuple

# constant genetic variables
POPULATION_SIZE = 10
NUMB_OF_ELITE_PATH_SOLUTION = 1
TOURNAMENT_SELECTION_SIZE = 5
MUTATION_RATE = 0.1
GENERATION_LIMIT = 100

# special point
DESTINATION = 9
NO_TILE = 0
TILE = 1
# 2
LIGHT_ORANGE_TILE = 2
# 3
HEAVY_SWITCH = 3
# 4
CLOSE_SOFT_SWITCH = 4
# 5
TOGGLE_SOFT_SWITCH = 5
# 6
OPEN_SOFT_SWITCH = 6
# 7
TELEPORT = 7
# 8
OPEN_HEAVY_SWITCH = 8

# rotation
STANDING = 'STANDING'
LYING_X = 'LYING_X'
LYING_Y = 'LYING_Y'
SPLIT = 'SPLIT'

# DIRECTION
UP = 'U'
DOWN = 'D'
LEFT = 'L'
RIGHT = 'R'

Population = List['PathSolution']


def readMap(fileMap):
    with open(fileMap) as f:
        MAP_ROW, MAP_COL, xStart, yStart = [
            int(x) for x in next(f).split()]  # read first line
        sourceMap = []
        countMapLine = 1
        for line in f:  # read map
            countMapLine += 1
            sourceMap.append([int(x) for x in line.split()])
            if countMapLine > MAP_ROW:
                break

        # read managedBoard
        managedBoard = []
        for line in f:  # read manaBoa
            # 2 2 4 4 4 5
            managedBoard.append([int(x) for x in line.split()])

    print("\nYOUR MAP LOOK LIKE THIS:")
    for item in sourceMap:
        print(item)
    print("Start at (", xStart, ",", yStart, ")")
    print("Managed Board:")
    for item in managedBoard:
        print(item)
    print("======================================")
    return MAP_ROW, MAP_COL, xStart, yStart, sourceMap, managedBoard


## GENETIC ALGORITHM ##
def generate_population(population_size: int) -> Population:
    land_size = MAP_ROW * MAP_COL
    rand_path_size = randrange(land_size//2, 2*land_size)
    return [Block(xStart, yStart, STANDING, None, sourceMap).initialize_path(rand_path_size) for _ in range(population_size)]


def selection_pair(population: Population) -> Population:
    weight_dist = []
    for path_temp in population:
        weight_dist.append(path_temp.distance_to_destination)
    return choices(population=population, weights=weight_dist, k=2)


def crossover_single_point(a: 'PathSolution', b: 'PathSolution'):
    path1 = a.path
    path2 = b.path

    length = min(len(path1), len(path2))
    if length < 2:
        return a, b

    pos = randint(1, length-1)
    a.path = path1[0:pos] + path2[pos:]
    b.path = path2[0:pos] + path1[pos:]
    return a, b


def mutation(path_obj: 'PathSolution', num: int = 1, probability: float = 0.5) -> 'PathSolution':
    path = path_obj.path
    direction = 'UDLR'
    if len(path) <= 1:
        return path
    for _ in range(num):
        index = randrange(0, len(path)-1, 1)
        rand_direction = choice(direction.replace(path[index], ''))
        pos_dir = path[index] if random(
        ) > probability else rand_direction
        path_obj.path = path[0:index] + pos_dir + path[index+1:]
    return path_obj


def evolve(population: Population):
    for gen in range(GENERATION_LIMIT):
        sorted_paths = sorted(
            population, key=lambda path: path.distance_to_destination, reverse=False)

        if sorted_paths[0].distance_to_destination == 0:
            break

        next_generation = sorted_paths[0:2]

        for j in range(len(sorted_paths)//2 - 1):
            parents = selection_pair(population)
            offspring_a, offspring_b = crossover_single_point(
                parents[0], parents[1])
            offspring_a = mutation(offspring_a)
            offspring_b = mutation(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation

    return population, gen
## GENETIC ALGORITHM ##


class Block:
    def __init__(self, x, y, rotation, parent, board, x1=None, y1=None):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.parent = parent
        self.board = deepcopy(board)
        self.x1 = x1
        self.y1 = y1
        self.path_info = PathSolution()

    def initialize_path(self, rand_size: int) -> 'PathSolution':
        path = self.path_info.initialize(rand_size).path
        actual_path: str = ''
        dist: float = 0
        for direction in path:
            x = self.x
            y = self.y
            print(f'>>> (x,y) = ({x},{y})')
            print("\n>>> current direction " + direction)
            if (self.rotation == SPLIT):
                x1 = self.x1
                y1 = self.y1
                dist = max(distance_fitness(x, y),
                           distance_fitness(x1, y1))
            else:
                dist = distance_fitness(x, y)

            if direction == UP:
                self.move_up()
            elif direction == DOWN:
                self.move_down()
            elif direction == RIGHT:
                self.move_right()
            elif direction == LEFT:
                self.move_left()
            else:
                pass

            if (isValidBlock(self) == False):
                self.path_info = PathSolution(actual_path, dist, x, y)
                break
            else:
                actual_path += direction

        if (actual_path == path):
            print('\n>>>> The same generated path')
        print('\n >>>> this is path = ' + self.path_info.path)
        print(
            f'\n >>> after moving => (x,y) = ({self.path_info.x_finish}, {self.path_info.y_finish}) with distance to goal = {self.path_info.distance_to_destination}')
        return self.path_info

    def __lt__(self, block):
        return True

    def __gt__(self, block):
        return True

    def move_up(self):
        if self.rotation == STANDING:
            self.y -= 2
            self.rotation = LYING_Y

        elif self.rotation == LYING_X:
            self.y -= 1

        elif self.rotation == LYING_Y:
            self.y -= 1
            self.rotation = STANDING

    def move_down(self):
        if self.rotation == STANDING:
            self.y += 1
            self.rotation = LYING_Y

        elif self.rotation == LYING_X:
            self.y += 1

        elif self.rotation == LYING_Y:
            self.y += 2
            self.rotation = STANDING

    def move_right(self):
        if self.rotation == STANDING:
            self.x += 1
            self.rotation = LYING_X

        elif self.rotation == LYING_X:
            self.x += 2
            self.rotation = STANDING

        elif self.rotation == LYING_Y:
            self.x += 1

    def move_left(self):

        if self.rotation == STANDING:
            self.rotation = LYING_X
            self.x -= 2

        elif self.rotation == LYING_X:
            self.x -= 1
            self.rotation = STANDING

        elif self.rotation == LYING_Y:
            self.x -= 1

    # FOR CASE SPLIT

    def split_move_up(self):
        self.y -= 1

    def split_move_down(self):
        self.y += 1

    def split_move_left(self):
        self.x -= 1

    def split_move_right(self):
        self.x += 1

    def split1_move_up(self):
        self.y1 -= 1

    def split1_move_down(self):
        self.y1 += 1

    def split1_move_left(self):
        self.x1 -= 1

    def split1_move_right(self):
        self.x1 += 1

    def disPlayPosition(self):
        if self.rotation != SPLIT:
            print(self.rotation, self.x, self.y)
        else:
            print(self.rotation, self.x, self.y, self.x1, self.y1)

    def displayBoard(self):
        # local definition
        x = self.x
        y = self.y
        x1 = self.x1
        y1 = self.y1
        rotation = self.rotation
        board = self.board

        # let's go

        if rotation != SPLIT:

            for i in range(len(board)):  # for ROW
                print("", end='  ')
                for j in range(len(board[i])):  # for COL in a ROW

                    if (i == y and j == x and rotation == STANDING) or \
                            ((i == y and j == x) or (i == y and j == x+1) and rotation == LYING_X) or \
                            ((i == y and j == x) or (i == y+1 and j == x) and rotation == LYING_Y):

                        print("x", end=' ')

                    elif (board[i][j] == 0):
                        print(" ", end=' ')
                    else:
                        print(board[i][j], end=' ')
                print("")
        else:  # CASE SPLIT
            for i in range(len(board)):  # for ROW
                print("", end='  ')
                for j in range(len(board[i])):  # for COL

                    if (i == y and j == x) or (i == y1 and j == x1):
                        print("x", end=' ')

                    elif (board[i][j] == 0):
                        print(" ", end=' ')
                    else:
                        print(board[i][j], end=' ')
                print("")


class Land:
    def __init__(self, land_map: List[str], rows, columns):
        self.land_map = land_map
        self.rows = rows
        self.columns = columns
        self.x_dest, self.y_dest = self.get_destination_coordinate()

    def get_destination_coordinate(self):
        for row in range(MAP_ROW - 1):
            try:
                column = self.land_map[row].index(DESTINATION)
                print(f'DES (x,y) = ({column},{row})')
                return (column, row)

            except ValueError as ve:
                print("destination hasn't been found")


class PathSolution:
    def __init__(self, path: str = '', distance: float = 0, x=0, y=0):
        self.path = path
        self.distance_to_destination = distance
        self.x_finish = x
        self.y_finish = y

    def initialize(self, rand_path_size):
        print('\n >>>> Random size for path = ', rand_path_size)
        rand_path = choices([UP, DOWN, RIGHT, LEFT], k=rand_path_size)

        temp = ''
        for p in rand_path:
            temp += p

        self.path = temp
        return self

    # def set_distance(self, dis: float):
    #     self.distance_to_destination = dis

    def eliminate_circular(self):
        '''' '''


def distance_fitness(x, y):
    x_dest = land.x_dest
    y_dest = land.y_dest
    return sqrt(
        (x-x_dest)**2 + (y-y_dest)**2)

# Case 3: Chữ X


def isHeavyToggleSwitch(block: Block, x, y):
    board = block.board

    for item in ManaBoa:
        if (x, y) == (item[0], item[1]):

            # TOGGLEEEE

            numToggle = item[2]   # num toggle
            index = 2   # index to check more element

            for i in range(numToggle):    # traverse toggle array
                bX = item[2*i+3]
                bY = item[2*i+4]
                if board[bX][bY] == 0:
                    board[bX][bY] = 1
                else:
                    board[bX][bY] = 0

            index = index + 1 + 2 * numToggle

            # CLOSEEEE

            # check if "item" has more element
            if index < len(item):   # case has more

                # read num close
                numClose = item[index]

                # traverse list close if num > 0
                for i in range(numClose):
                    bX = item[index+2*i+1]
                    bY = item[index+2*i+2]
                    board[bX][bY] = 0

                index = index + 1 + 2 * numClose

            # OPEENNNN

            # check if "item" has more element
            if index < len(item):   # case also has more item
                # get num open
                numOpen = item[index]

                # traverse list open if num > 0
                for i in range(numOpen):
                    bX = item[index+2*i+1]
                    bY = item[index+2*i+2]
                    board[bX][bY] = 1


# Case 4: Cục tròn đặc (only đóng).
def isSoftSwitchCloseOnly(block: Block, x, y):
    board = block.board

    # print("(x-y) = (", x,"-", y,")")

    for item in ManaBoa:
        if (x, y) == (item[0], item[1]):
            num = item[2]
            for i in range(num):
                bX = item[2*i+3]
                bY = item[2*i+4]
                board[bX][bY] = 0

# Case 5: Cục tròn đặc (toggle)


def isSoftToggleSwitch(block: Block, x, y):
    board = block.board

    for item in ManaBoa:
        if (x, y) == (item[0], item[1]):

            numToggle = item[2]     # numtoggle
            index = 2   # index to check more element

            for i in range(numToggle):
                bX = item[2*i+3]
                bY = item[2*i+4]
                if board[bX][bY] == 0:
                    board[bX][bY] = 1
                else:
                    board[bX][bY] = 0

            index = index + 1 + 2 * numToggle

            # CLOSEEEE

            # check if "item" has more element
            if index < len(item):   # case has more

                # read num close
                numClose = item[index]

                # traverse list close if num > 0
                for i in range(numClose):
                    bX = item[index+2*i+1]
                    bY = item[index+2*i+2]
                    board[bX][bY] = 0

                index = index + 1 + 2 * numClose

            # OPEENNNN

            # check if "item" has more element
            if index < len(item):   # case also has more item
                # get num open
                numOpen = item[index]

                # traverse list open if num > 0
                for i in range(numOpen):
                    bX = item[index+2*i+1]
                    bY = item[index+2*i+2]
                    board[bX][bY] = 1


# Case 6: Cục tròn đặc (only mở)
def isSoftSwitchOpenOnly(block: Block, x, y):
    board = block.board

    for item in ManaBoa:
        if (x, y) == (item[0], item[1]):
            num = item[2]
            for i in range(num):
                bX = item[2*i+3]
                bY = item[2*i+4]
                board[bX][bY] = 1

# Case 7: Cục phân thân


def isTeleport(block: Block, x, y):
    board = block.board
    array = []
    for item in ManaBoa:
        if (x, y) == (item[0], item[1]):
            num = item[2]
            # format x7 y7 2 x y x1 y1
            for i in range(num):
                bX = item[2*i+3]
                bY = item[2*i+4]
                array.append([bX, bY])

    (block.y, block.x, block.y1, block.x1) = (
        array[0][0], array[0][1], array[1][0], array[1][1])

    block.rotation = SPLIT

# Case 8: Chữ X (only mở)


def isHeavySwitchOpenOnly(block: Block, x, y):
    board = block.board

    for item in ManaBoa:
        if (x, y) == (item[0], item[1]):

            num = item[2]
            for i in range(num):
                bX = item[2*i+3]
                bY = item[2*i+4]
                board[bX][bY] = 1


def isFloor(block: Block):
    x = block.x
    y = block.y
    rotation = block.rotation
    board = block.board

    if x >= 0 and y >= 0 and y < MAP_ROW and x < MAP_COL and board[y][x] != 0:

        if rotation == STANDING:
            return True
        elif rotation == LYING_Y:
            if y+1 < MAP_ROW and board[y+1][x] != 0:
                return True
        elif rotation == LYING_X:
            if x+1 < MAP_COL and board[y][x+1] != 0:
                return True
        else:  # case SPLIT
            x1 = block.x1
            y1 = block.y1

            if x1 >= 0 and y1 >= 0 and \
                    y1 < MAP_ROW and x1 < MAP_COL and \
                    board[y1][x1] != 0:
                return True

    else:
        return False

# isValidBLock


def isValidBlock(block: Block):
    if isFloor(block):

        # local definition
        x = block.x
        y = block.y
        x1 = block.x1
        y1 = block.y1
        rotation = block.rotation
        board = block.board

        # Case 2: fragile tile
        if rotation == STANDING and board[y][x] == LIGHT_ORANGE_TILE:
            return False

        # Case 3: Chữ X
        if rotation == STANDING and board[y][x] == HEAVY_SWITCH:
            isHeavyToggleSwitch(block, x, y)

        # Case 4: Cục tròn đặc (only đóng).
        if board[y][x] == 4:
            isSoftSwitchCloseOnly(block, x, y)
        if rotation == LYING_X and board[y][x+1] == CLOSE_SOFT_SWITCH:
            isSoftSwitchCloseOnly(block, x+1, y)
        if rotation == LYING_Y and board[y+1][x] == CLOSE_SOFT_SWITCH:
            isSoftSwitchCloseOnly(block, x, y+1)
        if rotation == SPLIT and board[y1][x1] == CLOSE_SOFT_SWITCH:
            isSoftSwitchCloseOnly(block, x1, y1)

        # Case 5: Cục tròn đặc (toggle)
        if board[y][x] == 5:
            isSoftToggleSwitch(block, x, y)
        if rotation == LYING_X and board[y][x+1] == TOGGLE_SOFT_SWITCH:
            isSoftToggleSwitch(block, x+1, y)
        if rotation == LYING_Y and board[y+1][x] == TOGGLE_SOFT_SWITCH:
            isSoftToggleSwitch(block, x, y+1)
        if rotation == SPLIT and board[y1][x1] == TOGGLE_SOFT_SWITCH:
            isSoftToggleSwitch(block, x1, y1)

        # Case 6: Cục tròn đặc (only mở)
        if board[y][x] == 6:
            isSoftSwitchOpenOnly(block, x, y)
        if rotation == LYING_X and board[y][x+1] == OPEN_SOFT_SWITCH:
            isSoftSwitchOpenOnly(block, x+1, y)
        if rotation == LYING_Y and board[y+1][x] == OPEN_SOFT_SWITCH:
            isSoftSwitchOpenOnly(block, x, y+1)
        if rotation == SPLIT and board[y1][x1] == OPEN_SOFT_SWITCH:
            isSoftSwitchOpenOnly(block, x1, y1)

        # Case 7: Phân thân
        if rotation == STANDING and board[y][x] == TELEPORT:
            isTeleport(block, x, y)
        # Case7_1: MERGE BLOCK
        if rotation == SPLIT:  # check IS_MERGE
            # case LAYING_X: x first
            if y == y1 and x == x1 - 1:
                block.rotation = LYING_X

            # case LAYING_X: x1 first
            if y == y1 and x == x1 + 1:
                block.rotation = LYING_X
                block.x = x1

            # case LAYING_Y: y first
            if x == x1 and y == y1 - 1:
                block.rotation = LYING_Y

            # case LAYING_Y: y1 first
            if x == x1 and y == y1 + 1:
                block.rotation = LYING_Y
                block.y = y1

        # Case 8: Chữ X (only mở)
        if rotation == STANDING and board[y][x] == OPEN_HEAVY_SWITCH:
            isHeavySwitchOpenOnly(block, x, y)

        return True
    else:
        return False


def isGoal(block: Block):
    x = block.x
    y = block.y
    rotation = block.rotation
    board = block.board

    if rotation == STANDING and board[y][x] == DESTINATION:
        return True
    else:
        return False


def isVisited(block: Block):
    if block.rotation != SPLIT:

        for item in passState:
            if item.x == block.x and item.y == block.y and \
                    item.rotation == block.rotation and item.board == block.board:
                return True

    else:  # case SPLIT
        for item in passState:
            if item.x == block.x and item.y == block.y and \
               item.x1 == block.x1 and item.y1 == block.y1 and \
                    item.rotation == block.rotation and item.board == block.board:
                return True

    return False


def printSuccessRoad(block: Block):

    print("\nTHIS IS SUCCESS ROAD")
    print("================================")

    successRoad = [block]
    temp = block.parent

    while temp != None:

        if temp.rotation != SPLIT:
            newBlock = Block(temp.x, temp.y,
                             temp.rotation, temp.parent, temp.board)
        else:  # case SPLIT
            newBlock = Block(temp.x, temp.y,
                             temp.rotation, temp.parent, temp.board, temp.x1, temp.y1)

        successRoad = [newBlock] + successRoad

        temp = temp.parent

    step = 0
    for item in successRoad:
        step += 1
        print("\nStep:", step, end=' >>>   ')
        item.disPlayPosition()
        print("=============================")
        item.displayBoard()

    print("COMSUME", step, "STEP!!!!")


# START PROGRAM HERE
passState: List[Block] = []

MAP_ROW, MAP_COL, xStart, yStart, sourceMap, ManaBoa = readMap(
    'map.txt')

land = Land(sourceMap, MAP_ROW, MAP_COL)
init_block = Block(xStart, yStart, STANDING, None, sourceMap)
population = generate_population(POPULATION_SIZE)
population, geneneration = evolve(population=population)
