import abc
import numpy as np
import pygame
from typing import Tuple
from grid import Position, Cell
from drone import Drone


class Printer(abc.ABC):
    """Abstract base class for all printers."""
    @abc.abstractmethod
    def print(self, env, drones) -> None:
        pass


class EnvironmentPrinter(Printer):
    """Prints the environment."""
    def __init__(self, grid: np.array):
        self.grid = grid

    def print(self, env, drones) -> None:
        """Prints the environment."""
        local_map = env.get_map()
        env_grid = local_map.get_grid()
        n_cols, n_rows = env_grid.shape

        cell_height = self.__height // n_cols
        cell_width = self.__width // n_rows

        # Print grid squares of different types
        fertile_land_printer = FertileLandPrinter(
            screen=self.__screen, cell_width=cell_width, cell_height=cell_height,
        )
        oak_tree_printer = OakTreePrinter(
            screen=self.__screen, cell_width=cell_width, cell_height=cell_height,
        )
        pine_tree_printer = PineTreePrinter(
            screen=self.__screen, cell_width=cell_width, cell_height=cell_height,
        )
        eucalyptus_tree_printer = EucalyptusTreePrinter(
            screen=self.__screen, cell_width=cell_width, cell_height=cell_height,
        )
        charging_station_printer = ChargingStationPrinter(
            screen=self.__screen, cell_width=cell_width, cell_height=cell_height,
        )
        obstacle_printer = ObstaclePrinter(
            screen=self.__screen, cell_width=cell_width, cell_height=cell_height,
        )
        local_map = env.get_map()
        for pos in local_map.all_positions:
            if local_map.is_fertile_land(pos):
                fertile_land_printer.print(pos)
            elif local_map.is_oak_tree(pos):
                oak_tree_printer.print(pos)
            elif local_map.is_pine_tree(pos):
                pine_tree_printer.print(pos)
            elif local_map.is_eucalyptus_tree(pos):
                eucalyptus_tree_printer.print(pos)
            elif local_map.is_charging_station(pos):
                charging_station_printer.print(pos)
            elif local_map.is_obstacle(pos):
                obstacle_printer.print(pos)
            else:
                raise ValueError(f"Position not road or sidewalk: {pos}")

        self.add_colour_to_planted_squares(env)

        # Print drones
        drone_printer = DronePrinter(
            screen=self.__screen,
            cell_width=cell_width,
            cell_height=cell_height,
        )
        for drone in drones:
            drone_printer.print(drone)

        pygame.display.flip()

    def add_colour_to_planted_squares(self, env):
        """Adds colour to planted squares."""
        planted_squares = env.get_map().get_planted_squares()
        env_grid = env.get_map().get_grid()
        n_cols, n_rows = env_grid.shape

        assert self.__height % n_cols == 0, "display height is not divisible by number of columns in grid"
        assert self.__width % n_rows == 0, "display width is not divisible by number of rows in grid"

        cell_height = self.__height // n_cols
        cell_width = self.__width // n_rows

        for tuples in planted_squares:
            pos = tuples[0]
            cell_type = tuples[1]
            if cell_type == Cell.OAK_TREE:
                OakTreePrinter(screen=self.__screen, cell_width=cell_width, cell_height=cell_height, ).print(pos)
            if cell_type == Cell.PINE_TREE:
                PineTreePrinter(screen=self.__screen, cell_width=cell_width, cell_height=cell_height, ).print(pos)
            if cell_type == Cell.EUCALYPTUS_TREE:
                EucalyptusTreePrinter(screen=self.__screen, cell_width=cell_width, cell_height=cell_height, ).print(pos)

        return None

    def __enter__(self):
        """Initialises pygame and sets the screen size."""
        pygame.init()
        n_cells = self.grid.shape[0] * self.grid.shape[1]
        self.__width = self.__height = ((min(pygame.display.Info().current_w,
                                             pygame.display.Info().current_h) * 0.8) // n_cells) * n_cells
        self.__screen = pygame.display.set_mode((self.__width, self.__height))
        return self

    def __exit__(self, ex_type, ex_val, ex_traceback) -> bool:
        """Quits pygame."""
        pygame.quit()
        return False


class BasePrinter:
    """Abstract base class for all cell printers."""
    def __init__(self, screen: pygame.Surface, cell_width: int, cell_height: int):
        self._screen = screen
        self._cell_width = cell_width
        self._cell_height = cell_height

    def get_upper_left(self, pos: Position) -> Tuple[int, int]:
        """Computes the upper left corner for a given position."""
        return pos.x * self._cell_width, pos.y * self._cell_height

    def get_cell_center(self, pos: Position) -> Tuple[int, int]:
        """Computes the center pixels for a given position."""
        left, top = self.get_upper_left(pos)
        return left + self._cell_width // 2, top + self._cell_height // 2

    def get_px_side(self) -> int:
        """Computes the pixelart pixel size."""
        return int(self._cell_width // 16)


class CellPrinter(abc.ABC, BasePrinter):
    """Abstract base class for all cell printers."""
    @abc.abstractmethod
    def colour(self) -> pygame.Surface:
        pass

    def print(self, pos: Position) -> None:
        """Draws a rectangle of a given colour for the given position."""
        left = pos.x * self._cell_width
        top = pos.y * self._cell_height
        # Change function colour name
        self._screen.blit(self.colour(), (left, top))


class FertileLandPrinter(CellPrinter):
    """Prints fertile land."""
    def colour(self) -> pygame.Surface:
        return pygame.transform.scale(pygame.image.load("Images/Fertile.png"), (self._cell_width, self._cell_height))


class OakTreePrinter(CellPrinter):
    """Prints oak trees."""
    def colour(self) -> pygame.Surface:
        return pygame.transform.scale(pygame.image.load("Images/Oak.png"), (self._cell_width, self._cell_height))


class PineTreePrinter(CellPrinter):
    """Prints pine trees."""
    def colour(self) -> pygame.Surface:
        return pygame.transform.scale(pygame.image.load("Images/Pine.png"), (self._cell_width, self._cell_height))


class EucalyptusTreePrinter(CellPrinter):
    """Prints eucalyptus trees."""
    def colour(self) -> pygame.Surface:
        return pygame.transform.scale(pygame.image.load("Images/Eucalyptus.png"), (self._cell_width, self._cell_height))


class ChargingStationPrinter(CellPrinter):
    """Prints charging stations."""
    def colour(self) -> pygame.Surface:
        return pygame.transform.scale(pygame.image.load("Images/Station.png"), (self._cell_width, self._cell_height))


class ObstaclePrinter(CellPrinter):
    """Prints obstacles."""
    def colour(self) -> pygame.Surface:
        return pygame.transform.scale(pygame.image.load("Images/Obstacle.png"), (self._cell_width, self._cell_height))


class DronePrinter(BasePrinter):
    """Prints drones."""
    def __init__(self, screen: pygame.Surface, cell_width: int, cell_height: int):
        super().__init__(screen=screen, cell_width=cell_width, cell_height=cell_height)

    def print(self, d: Drone) -> None:
        """Draws a drone icon for the given drone."""
        if d.is_drone_dead():
            drone_icon = pygame.transform.scale(pygame.image.load("Images/coffin.png"),
                                                (0.8 * self._cell_width, 0.8 * self._cell_height))
        else:
            drone_icon = pygame.transform.scale(pygame.image.load("Images/Drone.png"),
                                                (0.8 * self._cell_width, 0.8 * self._cell_height))

        left = d.loc.x * self._cell_width + 0.1 * self._cell_width
        top = d.loc.y * self._cell_height + 0.1 * self._cell_height

        drone_sprite = pygame.transform.rotate(drone_icon, 0)

        self._screen.blit(drone_sprite, (left, top))
