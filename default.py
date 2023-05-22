import grid
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

MAP = np.where(MAP == 0, grid.Cell.FERTILE_LAND, MAP)
MAP = np.where(MAP == 1, grid.Cell.OAK_TREE, MAP)
MAP = np.where(MAP == 2, grid.Cell.PINE_TREE, MAP)
MAP = np.where(MAP == 3, grid.Cell.EUCALYPTUS_TREE, MAP)
MAP = np.where(MAP == 4, grid.Cell.CHARGING_STATION, MAP)
MAP = np.where(MAP == 5, grid.Cell.OBSTACLE, MAP)