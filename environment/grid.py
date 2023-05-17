import dataclasses
import enum
from typing import List

import numpy as np


@dataclasses.dataclass(frozen=True)
class Position:
    """Represents the coordinates of a grid position."""
    x: int
    y: int

    @property
    def up(self) -> "Position":
        """Position above this position."""
        # Y-axis is inverted as arrays are indexed as follows:
        # 0      -> [[...],
        # 1      ->  [...],
        # ...         ...
        # len(a) ->  [...]]
        # and so y=y-1 increases the position.
        return Position(x=self.x, y=self.y - 1)

    @property
    def down(self) -> "Position":
        """Position below of this position."""
        # Y-axis is inverted as arrays are indexed as follows:
        # 0      -> [[...],
        # 1      ->  [...],
        # ...         ...
        # len(a) ->  [...]]
        # and so y=y+1 decreases the position.
        return Position(x=self.x, y=self.y + 1)

    @property
    def left(self) -> "Position":
        """Position to the left of this position."""
        return Position(x=self.x - 1, y=self.y)

    @property
    def right(self) -> "Position":
        """Position to the right of this position."""
        return Position(x=self.x + 1, y=self.y)

    @property
    def up_right(self) -> "Position":
        """Position up and to the right of this position."""
        return self.up.right

    @property
    def up_left(self) -> "Position":
        """Position up and to the left of this position."""
        return self.up.left

    @property
    def down_left(self) -> "Position":
        """Position down and to the left of this position."""
        return self.down.left

    @property
    def down_right(self) -> "Position":
        """Position down and to the right of this position."""
        return self.down.right

    @property
    def adj(self) -> "List[Position]":
        """Positions that are adjacent to this position."""
        return [self.up, self.down, self.left, self.right,
                self.up_left, self.up_right,
                self.down_left, self.down_right]


class Cell(enum.Enum):
    """Represents each cell of the grid."""
    UNKOWN = -1  # Represents the houses in the project proposal figure.
    OBSTACLE = 0  # Represents the houses in the project proposal figure.
    FERTILE_LAND = 1
    OAK_TREE = 2
    PINE_TREE = 3
    EUCALYPTUS_TREE = 4
    CHARGING_STATION = 5  # We assume a single charging station by now. Position is also fixed.

    # Did not include a cell yet for the drone since it can be anywhere in the grid. May reconsider.

    def __repr__(self) -> str:
        return f"Cell({self.name})"


class Map:
    """Represents the combination of the grid with the cell values."""

    def __init__(self, grid: np.ndarray):
        self.grid = grid

    @property
    def height(self):
        """Returns the height of the map."""
        return self.grid.shape[0]

    @property
    def width(self):
        """Returns the width of the map."""
        return self.grid.shape[1]

    @property
    def all_positions(self) -> List[Position]:
        """Returns all the positions in the map."""
        positions = []
        with np.nditer(self.grid, flags=["multi_index", "refs_ok"]) as it:
            for _ in it:
                x, y = it.multi_index
                positions.append(Position(x=x, y=y))
        return positions

    @property
    def possible_drone_positions(self) -> List[Position]:
        """Returns all the positions in the map where the drone can be."""
        return self.all_positions

    def is_obstacle(self, p: Position) -> bool:
        """Returns True if the position is an obstacle, False otherwise."""
        return self.grid[p.y, p.x] == Cell.OBSTACLE

    def is_fertile_land(self, p: Position) -> bool:
        """Returns True if the position is fertile land, False otherwise."""
        return self.grid[p.y, p.x] == Cell.FERTILE_LAND

    def is_tree(self, p: Position) -> bool:
        """Returns True if the position is a tree, False otherwise."""
        return self.grid[p.y, p.x] in [Cell.OAK_TREE, Cell.PINE_TREE, Cell.EUCALYPTUS_TREE]

    def is_oak_tree(self, p: Position) -> bool:
        """Returns True if the position is an oak tree, False otherwise."""
        return self.grid[p.y, p.x] == Cell.OAK_TREE

    def is_pine_tree(self, p: Position) -> bool:
        """Returns True if the position is a pine tree, False otherwise."""
        return self.grid[p.y, p.x] == Cell.PINE_TREE

    def is_eucalyptus_tree(self, p: Position) -> bool:
        """Returns True if the position is a eucalyptus tree, False otherwise."""
        return self.grid[p.y, p.x] == Cell.EUCALYPTUS_TREE

    def is_charging_station(self, p: Position) -> bool:
        """Returns True if the position is a charging station, False otherwise."""
        return self.grid[p.y, p.x] == Cell.CHARGING_STATION

    # TODO: Understand if we need this.
    """    
    @property
    def is_inside_map(self, p: Position) -> bool:
        return 0 <= p.y < self.height and 0 <= p.x < self.width
    """

    # TODO: What more behaviour do we need?
