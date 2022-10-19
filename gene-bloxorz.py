from copy import copy
from random import choices, randrange
import sys
from typing import List

from bloxorz import DESTINATION


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
    print("ManaBoa:")
    for item in managedBoard:
        print(item)
    print("======================================")
    return MAP_ROW, MAP_COL, xStart, yStart, sourceMap, managedBoard


class GeneticAlgorithm:
    def evolve(self, population): return self._mutation_popluation(
        self._crossover_population(population))

    def _crossover_population(self, pop):
        ''' call to select top of random population '''

    def _crossover_path(self, path1, path2):
        ''' '''

    def _mutation_popluation(self, pop):
        ''''''

    def _mutation_path(self, path):
        ''''''

    def _select_top_path(self, pop):
        ''''''


class Land:
    def __init__(self, land_map: List[str], rows, columns):
        self.land_map = land_map
        self.rows = rows
        self.columns = columns

    def get_destination_coordinate(self):
        for row in MAP_ROW:
            column = self.land_map.find(DESTINATION)
            if (column != -1):
                return (row, column)


class PathSolution:
    def __init__(self):
        self.path = []

    def initialize(self):
        land_size = MAP_ROW * MAP_COL
        rand_path_size = randrange(land_size, 2*land_size)
        self.path = choices(['U', 'D', 'L', 'R'], k=rand_path_size)
        return self

    def dist_fitness(self):
        goal_x, goal_y = land.get_destination_coordinate()


        # START
passState = []

MAP_ROW, MAP_COL, xStart, yStart, sourceMap, ManaBoa = readMap(
    'map/map'+sys.argv[1:][0]+'.txt')

land = Land(sourceMap, MAP_ROW, MAP_COL)
