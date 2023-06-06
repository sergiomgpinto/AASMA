import dataclasses
import enum
import numpy as np
import grid as grid
from dataclasses import field


class Direction(enum.Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    UP_RIGHT = 4
    UP_LEFT = 5
    DOWN_RIGHT = 6
    DOWN_LEFT = 7

    def __repr__(self) -> str:
        return f"Direction({self.name})"


class Goal(enum.Enum):
    PLANT = 1
    CHARGE = 2
    WAIT = 3

    def __repr__(self) -> str:
        return f"Goal({self.name})"


@dataclasses.dataclass
class Drone:
    loc: grid.Position
    map: grid.Map
    id: int
    max_battery_available: int
    max_number_of_seeds: int

    nr_seeds: list = field(default_factory=lambda: [100, 100, 100]) # [OAK_TREE,PINE_TREE,EUCALYPTUS]
    total_distance: int = 0
    possible_drone_directions: list = field(default_factory=lambda: [
        Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT,
        Direction.UP_RIGHT, Direction.UP_LEFT, Direction.DOWN_RIGHT, Direction.DOWN_LEFT])
    is_dead: bool = False

    def __post_init__(self):
        self.direction = np.random.choice(self.possible_drone_directions)
        self.battery_available = self.max_battery_available

    def charge(self):
        """
        Charges batery. Will only have effect if drone is positioned in charging station and if the charging station 
        isn't full.
        """
        if self.map.find_charging_station() == self.loc:
            self.battery_available = self.max_battery_available
            self.nr_seeds = [self.max_number_of_seeds, self.max_number_of_seeds, self.max_number_of_seeds]

    def plant(self, map: grid.Map) -> tuple[bool, grid.Cell]:
        """
        Drone plants fertile land where he is located.
        """

        if map.is_fertile_land(self.loc):
            tree_id = map.get_type_of_tree_that_should_be_planted(self.loc)
            if self.nr_seeds[tree_id] > 0:
                self.nr_seeds[tree_id] -= 1
                return True, map.map_id_to_cell_type(tree_id)
        else:
            return False, None
