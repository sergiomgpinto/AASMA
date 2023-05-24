import dataclasses
import enum
import numpy as np
from typing import List, Optional
import random


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
    FERTILE_LAND = 0
    OAK_TREE = 1
    PINE_TREE = 2
    EUCALYPTUS_TREE = 3
    CHARGING_STATION = 4  # We assume a single charging station by now. Position is also fixed.
    OBSTACLE = 5  # Represents the houses in the project proposal figure.

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

    '''
    @property
    def possible_station_positions(self) -> List[Position]:
        return [
            p 
            for p in self.all_positions 
            if self.is_fertile(p) # the station will appear in 1 of the fertile land squares
        ]
    '''

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
        print(self.grid[p.y, p.x])
        return self.grid[p.y, p.x] == Cell.CHARGING_STATION

    # @property
    def is_inside_map(self, p: Position) -> bool:
        return 0 <= p.y < self.height and 0 <= p.x < self.width

    def adj_positions(self, p: Position) -> List[Position]:
        positions = [adj for adj in p.adj if
                     self.is_inside_map(adj)]  # aqui devia ser is_inside_map(adj) mas dava erro entao substitui por p
        return positions

    def adj_pos_of_type(self, p: Position, cell_type: Optional[Cell]) -> List[Position]:
        positions = self.adj_positions(p)
        if cell_type == Cell.FERTILE_LAND:
            positions = [adj for adj in positions if self.is_fertile_land(adj)]
        elif cell_type == Cell.OAK_TREE:
            positions = [adj for adj in positions if self.is_oak_tree(adj)]
        elif cell_type == Cell.PINE_TREE:
            positions = [adj for adj in positions if self.is_pine_tree(adj)]
        elif cell_type == Cell.EUCALYPTUS_TREE:
            positions = [adj for adj in positions if self.is_eucalyptus_tree(adj)]
        elif cell_type == Cell.OBSTACLE:
            positions = [adj for adj in positions if self.is_obstacle(adj)]
        else:
            raise ValueError(f"Unknown cell type: {cell_type}")
        return positions

    def has_adj_of_type(self, p: Position, cell_type: Optional[Cell]) -> bool:
        positions = self.adj_positions(p)
        if cell_type == Cell.FERTILE_LAND:
            return any(self.is_fertile_land(adj) for adj in positions)
        elif cell_type == Cell.OAK_TREE:
            return any(self.is_oak_tree(adj) for adj in positions)
        elif cell_type == Cell.PINE_TREE:
            return any(self.is_pine_tree(adj) for adj in positions)
        elif cell_type == Cell.EUCALYPTUS_TREE:
            return any(self.is_eucalyptus_tree(adj) for adj in positions)
        elif cell_type == Cell.OBSTACLE:
            return any(self.is_obstacle(adj) for adj in positions)
        else:
            raise ValueError(f"Unknown cell type: {cell_type}")

    def change_cell_type(self, p: Position, cell_type: Cell):
        """
        Modifies cell type of position p in the environment grid.
        """
        self.grid[p.y, p.x] = cell_type

    # TODO: What more behaviour do we need?
    def plantable_squares(self) -> List[Position]:
        """
        Looks at the grid and returns fertile land squares that have not yet
        been planted. 
        
        """
        plantable_positions = []
        for p in self.all_positions:
            if self.is_fertile_land(p):
                plantable_positions.append(p)
        return plantable_positions

    def find_charging_station(self):
        """
        Looks at the grid and returns the position of the charging station
            
        """
        for p in self.all_positions:
            if self.is_charging_station(p):
                return p
        pass

    def choose_adj_fertile_land(self, p: Position):
        """
        Looks for the closest fertile cell and decides which seed to plant
        Args:
            p (Position): Drone Position in the grid

        Returns:
            Pos: Returns the position of the closest fertile land. 
                       If there's none return null.
        """
        # FIXME: Add a shuffle
        fertile_land_nearby = self.adj_positions(p)

        for fertile_land in fertile_land_nearby:
            return fertile_land

        return None

    # retorna os índices correspondentes ao inventário de seeds dos agentes drones
    def choose_seed(self, p: Position) -> Cell:
        if self.has_adj_of_type(p, Cell.OAK_TREE):
            return Cell.OAK_TREE
        elif self.has_adj_of_type(p, Cell.PINE_TREE):
            return Cell.PINE_TREE
        elif self.has_adj_of_type(p, Cell.EUCALYPTUS_TREE):
            return Cell.EUCALYPTUS_TREE
        else:
            return random.choice([Cell.OAK_TREE, Cell.PINE_TREE, Cell.EUCALYPTUS_TREE])
