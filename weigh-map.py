from copy import deepcopy
from queue import SimpleQueue
from bloxorz import read_map
import numpy as np

# def weigh_surrounding

def weigh_pos_recursive (map, row, col, weight):
  # temp = deepcopy(weight)
  if row < 0 or row >= MAP_ROW or col < 0 or col >= MAP_COL or source_map[row][col] == 0:
    return None


  if map[row][col] == False and (source_map[row][col] != 0 or (row,col) in bridges):
    map[row][col] = weight

  # print(f'Address = {id(weight)} with value = {row}, {col} with weight {weight}')
  weigh_pos_recursive( map, row,col-1,weight+1)
  weigh_pos_recursive( map, row,col+1,weight+1)
  weigh_pos_recursive( map, row-1,col,weight+1)
  weigh_pos_recursive( map, row+1,col,weight+1)



  return
  
  



def weight_map():
  new_map = [False]*MAP_ROW
  for r in range(MAP_ROW):
    new_map[r] = [False]*MAP_COL

  # new_map[1][13] = 0
  weigh_pos_recursive(new_map, 1, 13, 1)

  for r in range(MAP_ROW):
    print(f'\nrow {r} = {new_map[r]}')

def bridge_list():
  bri = []
  for r in range(len(man_board)):
    bri.append(man_board[r][3:])
  
  flatten_list = [item for sublist in bri for item in sublist]
  print(flatten_list)
  it = iter(flatten_list)
  tuple_row_col = list(zip(it,it))
  print(tuple_row_col)

  return tuple_row_col


MAP_ROW, MAP_COL, xStart, yStart, source_map, man_board = read_map(
    'map/map02.txt')

bridges = bridge_list()
weight_map()

def main ():
  new_map = [False]*MAP_ROW
  for r in range(MAP_ROW):
    new_map[r] = [False]*MAP_COL

  
  # DFS_map(1, 13, new_map)


