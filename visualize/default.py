from environment import grid
import numpy as np

MAP = np.array([
    [0, 0, 5, 0, 0, 1, 0],
    [0, 5, 5, 0, 1, 1, 1],
    [2, 0, 0, 0, 4, 0, 0],
    [0, 2, 0, 2, 0, 3, 3],
    [2, 2, 1, 0, 0, 5, 3],
    [2, 0, 1, 0, 0, 5, 0],
    [0, 0, 0, 0, 3, 2, 0],
    
])

MAP = np.where(MAP == 0, grid.Cell.FERTILE_LAND, grid.Cell.OAK_TREE, 
               grid.Cell.PINE_TREE, grid.Cell.EUCALYPTUS_TREE, grid.Cell.CHARGING_STATION, grid.Cell.OBSTACLE)

'''FERTILE_LAND = 0
    OAK_TREE = 1
    PINE_TREE = 2
    EUCALYPTUS_TREE = 3
    CHARGING_STATION = 4 
    OBSTACLE = 5 '''