import numpy as np
import yaml
from grid import Cell


class DefaultMap:
    cell_mapping = {
        0: Cell.FERTILE_LAND,
        1: Cell.OAK_TREE,
        2: Cell.PINE_TREE,
        3: Cell.EUCALYPTUS_TREE,
        4: Cell.CHARGING_STATION,
        5: Cell.OBSTACLE
    }

    def __init__(self):
        with open("./config.yml", "r") as fp:
            data = yaml.safe_load(fp)
        size = data["map_size"]
        self.integer_map = np.random.choice([0, 1, 2, 3, 5], (size, size))

        station_x = np.random.randint(size)
        station_y = np.random.randint(size)
        self.integer_map[station_x][station_y] = 4

        self.vectorized_mapping = np.vectorize(self.cell_mapping.get)

        # Apply the mapping to the initial map
        self.MAP = self.vectorized_mapping(self.integer_map)


MAP = DefaultMap().MAP
