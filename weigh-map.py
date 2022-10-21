from queue import SimpleQueue
from bloxorz import read_map
import numpy as np

# def weigh_surrounding


def weight_map(sourceMap):
    temp = [10]*MAP_ROW

    for row in range(MAP_ROW):
        temp[row] = [10]*MAP_COL
    record = SimpleQueue()
    new_map = np.array(temp)

    record.put((13, 1))

    weight_value = 0
    parent_numb = 1

    while record.empty() == False:
        children_numb = 0
        r, c = record.get()
        print(f'row, col = {r}, {c}')

        sub_map = [[weight_value]*3 for _ in range(3)]
        print(sub_map)

        new_map[r-1:r+1, c-1:c+1]= sub_map
        print(new_map)


MAP_ROW, MAP_COL, xStart, yStart, sourceMap, ManaBoa = read_map(
    'map/map02.txt')
weight_map(sourceMap)
