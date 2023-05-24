import numpy as np
from grid import Cell

# Initial integer representation of the map
integer_map = np.array([
    [0, 0, 5, 0, 0, 1, 0],
    [0, 5, 5, 0, 1, 1, 1],
    [2, 0, 0, 0, 4, 0, 0],
    [0, 2, 0, 2, 0, 3, 3],
    [2, 2, 1, 0, 0, 5, 3],
    [2, 0, 1, 0, 0, 5, 0],
    [0, 0, 0, 0, 3, 2, 0]
])

# Mapping from integer to corresponding grid cell
cell_mapping = {
    0: Cell.FERTILE_LAND,
    1: Cell.OAK_TREE,
    2: Cell.PINE_TREE,
    3: Cell.EUCALYPTUS_TREE,
    4: Cell.CHARGING_STATION,
    5: Cell.OBSTACLE
}

# Vectorized function for mapping conversion
vectorized_mapping = np.vectorize(cell_mapping.get)

# Apply the mapping to the initial map
MAP = vectorized_mapping(integer_map)
