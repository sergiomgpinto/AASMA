import numpy as np
import yaml
from grid import Cell
from scipy.ndimage.filters import convolve


def blur_map(map):
    """Blurs the map."""
    kernel = np.ones((3, 3))

    blurred_map = convolve(map, kernel, mode='constant', cval=1.0)

    norm_blurred_map = (blurred_map / blurred_map.max()) * 4
    norm_blurred_map = norm_blurred_map.astype(int)
    return norm_blurred_map


class DefaultMap:
    """Generates a random map with a charging station."""

    cell_mapping = {
        0: Cell.FERTILE_LAND,
        1: Cell.OAK_TREE,
        2: Cell.PINE_TREE,
        3: Cell.EUCALYPTUS_TREE,
        4: Cell.OBSTACLE,
        5: Cell.CHARGING_STATION,
    }

    def __init__(self):
        with open("./config.yml", "r") as fp:
            data = yaml.safe_load(fp)

        size = data["map_size"]
        fertile_land_ratio = data["fertile_land_ratio"]
        nr_charging_stations = data["nr_charging_stations"]

        if size < 7 or size > 26:
            raise ValueError("Map size inserted in the config file must be between 7 and 26, both inclusive.")
        if fertile_land_ratio < 0.5 or fertile_land_ratio > 0.85:
            raise ValueError("Fertile land ratio inserted in the config file must be between 0.5 and 0.85, both inclusive.")

        probabilities = [0.1, 0.1, 0.1, 0.1, 0.6]
        self.integer_map = np.random.choice([0, 1, 2, 3, 4], (size, size), p=probabilities)

        n_fertile_land = int(fertile_land_ratio * size * size)

        fertile_land_indices = np.random.choice(size * size, n_fertile_land, replace=False)
        self.integer_map.ravel()[fertile_land_indices] = 0
        self.integer_map = blur_map(self.integer_map)

        for _ in range(nr_charging_stations):
            while True:
                station_x = np.random.randint(size)
                station_y = np.random.randint(size)
                if self.integer_map[station_x][station_y] != 0 and self.integer_map[station_x][station_y] != 5:
                    self.integer_map[station_x][station_y] = 5
                    break

        self.vectorized_mapping = np.vectorize(self.cell_mapping.get)
        self.MAP = self.vectorized_mapping(self.integer_map)


# Global map variable
MAP = DefaultMap().MAP

