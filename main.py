import numpy as np
import environment.grid as grid

from typing import List

import random

    
def map_generator(rows: int, columns: int, n_charging_stations: int = 1, n_agents: int = 2, p_obstacles: float = 0.3, p_fertile_land: float = 0.4, p_tree: List[float] = [0.3, 0.3, 0.4]) -> np.ndarray:
    MAP = np.zeros((rows, columns))
    
    for i in range(rows):
        for j in range(columns):
            r = random.random()
            if r < p_obstacles:
                MAP[i][j] = grid.Cell.OBSTACLE
            elif r < p_obstacles+p_fertile_land:
                MAP[i][j] = grid.Cell.FERTILE_LAND
            else:
                r = random.random()
                if r < p_tree[0]:
                    MAP[i][j] = grid.Cell.OAK_TREE
                elif r < p_tree[0]+p_tree[1]:
                    MAP[i][j] = grid.Cell.PINE_TREE
                else:
                    MAP[i][j] = grid.Cell.EUCALYPTUS_TREE
                    
    return MAP
    


def main():
    MAP = map_generator(10, 10)


if __name__ == '__main__':
    main()
