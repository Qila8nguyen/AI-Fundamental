from copy import copy, deepcopy
from math import sqrt
from operator import truediv
from random import choice, choices, randint, randrange, random
import time
import sys
from typing import List, Tuple

from utils import BFS_weigh

# constant genetic variables
POPULATION_SIZE = 20
# NUMB_OF_ELITE_PATH_SOLUTION = 1
# TOURNAMENT_SELECTION_SIZE = 5
# MUTATION_RATE = 0.1 -> 1/step
GENERATION_LIMIT = 10000

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


def read_map(fileMap):
    with open(fileMap) as f:
        MAP_ROW, MAP_COL, xStart, yStart = [
            int(x) for x in next(f).split()]  # read first line
        source_map = []
        countMapLine = 1
        for line in f:  # read map
            countMapLine += 1
            source_map.append([int(x) for x in line.split()])
            if countMapLine > MAP_ROW:
                break

        # read managedBoard
        managedBoard = []
        for line in f:  # read man_board
            # 2 2 4 4 4 5
            managedBoard.append([int(x) for x in line.split()])

    print("\nYOUR MAP LOOK LIKE THIS:")
    for item in source_map:
        print(item)
    print("Start at (", xStart, ",", yStart, ")")
    print("Managed Board:")
    for item in managedBoard:
        print(item)
    print("======================================")
    return MAP_ROW, MAP_COL, xStart, yStart, source_map, managedBoard


## GENETIC ALGORITHM ##
def generate_population(population_size: int) -> Population:
    land_size = MAP_ROW * MAP_COL
    rand_path_size = randrange(land_size//2, 2*land_size)
    population: Population = []
    while (len(population) < population_size):
        new_path = PathSolution().initialize(rand_path_size)
        fitness_path(new_path)
        if (new_path.last_step > 5):
            population.append(new_path)
    return population


def selection_pair(population: Population) -> Population:
    weight_of_fitness = []
    for path in population:
        value = fitness_path(path)
        weight_of_fitness.append(1/value if value != 0 else 1)
    choice = deepcopy(choices(population=population, weights=weight_of_fitness, k=2))
    return choice


def crossover_single_or_two(a: 'PathSolution', b: 'PathSolution', probability = 0.8):
    if (a == b): return a,b
    path1 = a.path
    path2 = b.path

    # Cross at last step
    pos = min(a.last_step, b.last_step) if min(
        a.last_step, b.last_step) > 2 else 1
    pos1 = randrange(0, pos)
    if (pos1 == 0 or random() < probability): return a,b

    if len(path1) > pos1+2 and len(path2) > pos1+2 and pos > pos1+1:
        pos2 = randrange(pos1+1, pos)
        a.path = path1[0:pos1] + path2[pos1:pos2] + path1[pos2:]
        b.path = path2[0:pos1] + path1[pos1:pos2] + path2[pos2:]

    else:
        a.path = path1[0:pos1] + path2[pos1:]
        b.path = path2[0:pos1] + path1[pos1:]

    # uniform_point = choices([0,1], k=pos)

    # for i in range(pos):
    #     if uniform_point[i] == 1:
    #         ''' :>>>> '''
    
    return a, b

def uniform_crossover(a: 'PathSolution', b: 'PathSolution', probability = 0.8):
    if (a == b): return a,b
    path1 = a.path
    path2 = b.path
    child_path1 = ''
    child_path2 = ''

    leng = min(len(path1), len(path2)) 
    for idx in range(leng):
        rand = random()

        if (rand > 0.8):
            child_path1 += path1[idx]
            child_path2 += path2[idx]
        elif rand > 0.3:
            child_path1 += path2[idx]
            child_path2 += path1[idx]
        else:
            child_path1 += choice('UDLR')
            child_path2 += choice('UDLR')

    a.path = child_path1
    b.path = child_path2
    return a,b


def mutation(path_obj: 'PathSolution', probability: float = 0.5) -> 'PathSolution':
    path = path_obj.path
    direction = 'UDLR'
    mutated_path = ''

    for idx in range(len(path)):
        random_prob = random()
        if (random_prob > probability): 
            mutated_path += path[idx]

        else:
            rand_direction = choice(direction.replace(path[idx], ''))
            mutated_path += rand_direction

    path_obj.path = mutated_path
    return path_obj


def evolve(population: Population):
    for gen in range(GENERATION_LIMIT):
        sorted_paths = sorted(
            population, key=lambda path: fitness_path(path), reverse=False)

        print(f'Gen {gen} has {sorted_paths[0].distance_to_destination}, with length {len(sorted_paths)}')
        if sorted_paths[0].distance_to_destination == 0:
            break

        next_generation = deepcopy(sorted_paths[0:2])

        for _ in range(len(sorted_paths)//2 - 1):
            parents = selection_pair(population)
            offspring_a, offspring_b = uniform_crossover(
                parents[0], parents[1])
            # print(f'Gen {gen} has {sorted_paths[0].distance_to_destination}, with length {len(next_generation)}')
            next_generation += [offspring_a, offspring_b]

        population = next_generation
    

    population = sorted(
        population, key=lambda path: fitness_path(path), reverse=False)

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
        init_path = self.path_info.initialize(rand_size)
        self.path_info = fitness_path(init_path)

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
                continue
                #     print("destination hasn't been found")


class PathSolution:
    def __init__(self, path: str = '', last_step=0, distance: float = 0, x=0, y=0, actual_path='', rotation=None):
        self.path = path
        self.distance_to_destination = distance
        self.last_step = last_step
        self.x_finish = x
        self.y_finish = y
        self.actual_path = actual_path
        self.rotation = rotation

    def initialize(self, rand_path_size):
        rand_path = choices([UP, DOWN, RIGHT, LEFT], k=rand_path_size)
        self.path = ''.join(rand_path)
        return self


def distance_to_goal(x, y):
    return weigh_map[y][x]


def fitness_path(rand_path: PathSolution) -> float:
    block = Block(xStart, yStart, STANDING, None, source_map)

    path = rand_path.path
    actual_path: str = ''
    dist: float = 0
    for idx, direction in enumerate(path):
        x = block.x
        y = block.y

        if (block.rotation == SPLIT):
            x1 = block.x1
            y1 = block.y1
            dist = max(distance_to_goal(x, y),
                       distance_to_goal(x1, y1))
        else:
            dist = distance_to_goal(x, y)
            current_rotation = block.rotation
        if direction == UP:
            block.move_up()
        elif direction == DOWN:
            block.move_down()
        elif direction == RIGHT:
            block.move_right()
        elif direction == LEFT:
            block.move_left()
        else:
            pass

        if dist <=3: 
            rand_path.x_finish = x
            rand_path.y_finish = y
            rand_path.last_step = idx
            rand_path.distance_to_destination = dist
            rand_path.actual_path = actual_path
            rand_path.rotation = current_rotation

            if get_in_hole(rand_path):
                rand_path.distance_to_destination = 0
                return 0

        if (isValidBlock(block) == False):
            rand_path.x_finish = x
            rand_path.y_finish = y
            rand_path.last_step = idx
            rand_path.distance_to_destination = dist
            rand_path.actual_path = actual_path
            rand_path.rotation = current_rotation

            break
        else:
            actual_path += direction

    # print(f'weigh_map ({x},{y}) = {weigh_map[y][x]}')
    return dist

# Case 3: Chữ X
def isHeavyToggleSwitch(block: Block, x, y):
    board = block.board

    for item in man_board:
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

    # print(f'(x,y) = ({x},{y})')

    for item in man_board:
        if (x, y) == (item[0], item[1]):
            num = item[2]
            for i in range(num):
                bX = item[2*i+3]
                bY = item[2*i+4]
                board[bX][bY] = 0

# Case 5: Cục tròn đặc (toggle)


def isSoftToggleSwitch(block: Block, x, y):
    board = block.board
    # print(f'(x,y) = ({x},{y})')

    for item in man_board:
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

    for item in man_board:
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
    for item in man_board:
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

    for item in man_board:
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
            if x+1 < MAP_COL and board[y][x] != 0:
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


def isValidBlock(block: Block, dist: float = 0):
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

def get_in_hole (path: PathSolution):
    x = path.x_finish
    y = path.y_finish
    rotation = path.rotation

    if rotation == LYING_X and y == land.y_dest:
        if weigh_map[y][x+1] == 2 and x < land.x_dest:
            path.actual_path += 'R'
            path.last_step += 1
            return True
        

        if weigh_map[y][x] == 2 and x > land.x_dest:
            path.actual_path += 'L'
            path.last_step += 1
            return True

        

    if rotation == LYING_Y and x == land.x_dest:
        if land.y_dest < y and weigh_map[y][x] == 2:
            path.actual_path += 'U'
            path.last_step += 1
            return True
        
        if land.y_dest > y and weigh_map[y+1][x] == 2:
            path.actual_path += 'D'
            path.last_step += 1
            return True
    
    if rotation == STANDING and source_map[y][x] == DESTINATION: 
        return True
    
    return False


def print_2d_arr(arr):
    for row in arr:
        print(row)


# START PROGRAM HERE
passState: List[Block] = []

MAP_ROW, MAP_COL, xStart, yStart, source_map, man_board = read_map(
    'map/map'+sys.argv[1:][0]+'.txt')
# MAP_ROW, MAP_COL, xStart, yStart, source_map, man_board = read_map(
#     'map/map02.txt')
land = Land(source_map, MAP_ROW, MAP_COL)
weigh_map = BFS_weigh(land.y_dest, land.x_dest, MAP_ROW, MAP_COL, source_map, man_board)
start = time.time()
population = generate_population(POPULATION_SIZE)
print_2d_arr(weigh_map)
population, geneneration = evolve(population=population)
end = time.time()

print(f"Time taken: {(end-start)*10**3:.03f}ms")
print(
    f'Population with destination length = {fitness_path(population[0])} with path [{population[0].actual_path}] at generation {geneneration}')

# test = 'RUUDDRRRRLURULDDDRRRRRULU'
# init = PathSolution(path=test)
# print(fitness_path(init))
