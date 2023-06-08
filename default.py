import numpy as np
import yaml
from grid import Cell


class DefaultMap:
    """Generates a random map with a charging station."""

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
        fertile_land_ratio = data["fertile_land_ratio"]
        nr_charging_stations = data["nr_charging_stations"]

        self.integer_map = np.random.choice([1, 2, 3, 5], (size, size))

        n_fertile_land = int(fertile_land_ratio * size * size)

        fertile_land_indices = np.random.choice(size * size, n_fertile_land, replace=False)
        self.integer_map.ravel()[fertile_land_indices] = 0

        for _ in range(nr_charging_stations):
            while True:
                station_x = np.random.randint(size)
                station_y = np.random.randint(size)
                if self.integer_map[station_x][station_y] != 4:  # Ensure we don't overwrite an existing station
                    self.integer_map[station_x][station_y] = 4
                    break

        self.vectorized_mapping = np.vectorize(self.cell_mapping.get)
        self.MAP = self.vectorized_mapping(self.integer_map)


# Global map variable
MAP = DefaultMap().MAP
