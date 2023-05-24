import abc
import env as env
import grid
import numpy as np
import pygame
import drone as drone
from typing import Tuple


class EnvironmentPrinter(env.Printer):

    def __init__(self, local_grid: np.array):
        # Mapping between the passenger Drop-Off location
        # and its colour.
        # self._tree_colours = {}
        self.grid = local_grid
        # self._colour_picker = colour.Picker()

    def print(self, local_env: env.Environment):
        env_grid = local_env.map.grid
        n_cols, n_rows = env_grid.shape

        assert self.__height % n_cols == 0, "display height is not divisible by number of columns in grid"
        assert self.__width % n_rows == 0, "display width is not divisible by number of rows in grid"

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

        for pos in local_env.map.all_positions:
            if local_env.map.is_fertile_land(pos):
                fertile_land_printer.print(pos)
            elif local_env.map.is_oak_tree(pos):
                oak_tree_printer.print(pos)
            elif local_env.map.is_pine_tree(pos):
                pine_tree_printer.print(pos)
            elif local_env.map.is_eucalyptus_tree(pos):
                eucalyptus_tree_printer.print(pos)
            elif local_env.map.is_charging_station(pos):
                charging_station_printer.print(pos)
            elif local_env.map.is_obstacle(pos):
                obstacle_printer.print(pos)
            else:
                raise ValueError(f"Position not road or sidewalk: {pos}")

        # Print drones
        drone_printer = DronePrinter(
            screen=self.__screen,
            cell_width=cell_width,
            cell_height=cell_height,
        )
        for d in local_env.drones:
            drone_printer.print(d)

        self._add_colour_to_planted_squares(local_env)

        pygame.display.flip()

    def _add_colour_to_planted_squares(self, local_env: env.Environment):

        planted_squares = local_env.planted_squares
        env_grid = local_env.map.grid
        n_cols, n_rows = env_grid.shape

        assert self.__height % n_cols == 0, "display height is not divisible by number of columns in grid"
        assert self.__width % n_rows == 0, "display width is not divisible by number of rows in grid"

        cell_height = self.__height // n_cols
        cell_width = self.__width // n_rows

        for tuples in planted_squares:
            pos = tuples[0]
            cell_type = tuples[1]
            if cell_type == grid.Cell.OAK_TREE:
                OakTreePrinter(screen=self.__screen, cell_width=cell_width, cell_height=cell_height, ).print(pos)
            if cell_type == grid.Cell.PINE_TREE:
                PineTreePrinter(screen=self.__screen, cell_width=cell_width, cell_height=cell_height, ).print(pos)
            if cell_type == grid.Cell.EUCALYPTUS_TREE:
                EucalyptusTreePrinter(screen=self.__screen, cell_width=cell_width, cell_height=cell_height, ).print(pos)

        return None

    def __enter__(self):
        pygame.init()
        n_cells = self.grid.shape[0] * self.grid.shape[1]
        self.__width = self.__height = ((min(pygame.display.Info().current_w,
                                             pygame.display.Info().current_h) * 0.8) // n_cells) * n_cells
        self.__screen = pygame.display.set_mode((self.__width, self.__height))
        return self

    def __exit__(self, ex_type, ex_val, ex_traceback) -> bool:
        pygame.quit()
        return False


class BasePrinter:
    def __init__(self, screen: pygame.Surface, cell_width: int, cell_height: int):
        self._screen = screen
        self._cell_width = cell_width
        self._cell_height = cell_height

    def get_upper_left(self, pos: grid.Position) -> Tuple[int, int]:
        """Computes the upper left corner for a given position."""
        return pos.x * self._cell_width, pos.y * self._cell_height

    def get_cell_center(self, pos: grid.Position) -> Tuple[int, int]:
        """Computes the center pixels for a given position."""
        left, top = self.get_upper_left(pos)
        return left + self._cell_width // 2, top + self._cell_height // 2

    def get_px_side(self):
        """Computes the pixelart pixel size."""
        return int(self._cell_width // 16)


class CellPrinter(abc.ABC, BasePrinter):
    @abc.abstractmethod
    def colour(self):
        pass

    def print(self, pos: grid.Position) -> None:
        """Draws a rectangle of a given colour for the given position."""
        left = pos.x * self._cell_width
        top = pos.y * self._cell_height
        # Change function colour name
        self._screen.blit(self.colour(), (left, top))


class FertileLandPrinter(CellPrinter):
    def colour(self):
        return pygame.transform.scale(pygame.image.load("Images/Fertile.png"), (self._cell_width, self._cell_height))


class OakTreePrinter(CellPrinter):
    def colour(self):
        return pygame.transform.scale(pygame.image.load("Images/Oak.png"), (self._cell_width, self._cell_height))


class PineTreePrinter(CellPrinter):
    def colour(self):
        return pygame.transform.scale(pygame.image.load("Images/Pine.png"), (self._cell_width, self._cell_height))


class EucalyptusTreePrinter(CellPrinter):
    def colour(self):
        return pygame.transform.scale(pygame.image.load("Images/Eucalyptus.png"), (self._cell_width, self._cell_height))


class ChargingStationPrinter(CellPrinter):
    def colour(self):
        return pygame.transform.scale(pygame.image.load("Images/Station.png"), (self._cell_width, self._cell_height))


class ObstaclePrinter(CellPrinter):
    def colour(self):
        return pygame.transform.scale(pygame.image.load("Images/Obstacle.png"), (self._cell_width, self._cell_height))


class DronePrinter(BasePrinter):
    def __init__(
            self,
            screen: pygame.Surface,
            cell_width: int,
            cell_height: int,
    ):
        super().__init__(screen=screen, cell_width=cell_width, cell_height=cell_height)

    def print(self, d: drone.Drone):

        drone_icon = pygame.transform.scale(pygame.image.load("Images/Drone.png"),
                                            (0.8 * self._cell_width, 0.8 * self._cell_height))

        left = d.loc.x * self._cell_width + 0.1 * self._cell_width
        top = d.loc.y * self._cell_height + 0.1 * self._cell_height

        # Por agora a nossa imagem é simétrica mas se metermos um drone com frente e trás isto pode ser util 
        # por isso é que deixei aqui 
        if d.direction == drone.Direction.UP:
            drone_sprite = pygame.transform.rotate(drone_icon, 0)

        elif d.direction == drone.Direction.DOWN:
            drone_sprite = pygame.transform.rotate(drone_icon, -180)

        elif d.direction == drone.Direction.LEFT:
            drone_sprite = pygame.transform.rotate(drone_icon, 90)

        elif d.direction == drone.Direction.RIGHT:
            drone_sprite = pygame.transform.rotate(drone_icon, -90)
        else:
            raise ValueError(f"Invalid direction: {d.direction}")

        # if d.has_passenger is not None:
        # taxi_center = self.get_cell_center(taxi.loc)
        # px_side = self.get_px_side()
        # x, y = self.get_upper_left(d.loc)

        # drone_rect = pygame.Rect(x, y, self._cell_width, self._cell_height)
        # pygame.draw.rect(self._screen, drone_rect)

        # taxi_rect1 = pygame.Rect(taxi_center[0] - (2 * px_side), taxi_center[1] + px_side, 4 * px_side, 4 * px_side)
        # taxi_rect2 = taxi_rect1.copy().inflate(2 * px_side, -2 * px_side)
        # taxi_rect3 = taxi_rect1.copy().inflate(-2 * px_side, 2 * px_side)
        # pygame.draw.rect(self._screen, draw_colour, taxi_rect1)
        # pygame.draw.rect(self._screen, draw_colour, taxi_rect2)
        # pygame.draw.rect(self._screen, draw_colour, taxi_rect3)

        self._screen.blit(drone_sprite, (left, top))

        # taxi_center = self.get_cell_center(taxi.loc)
        # draw_text(self._screen, f"{taxi.id}", taxi_center, (0, 0, 0), 18, bold=True)


def draw_text(
        screen: pygame.Surface,
        text: str,
        center: Tuple[int, int],
        color: Tuple[int, int, int],
        size: int,
        font: str = "arial",
        bold: bool = False,
):
    font = pygame.font.SysFont(font, size, bold)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    rect.center = center

    screen.blit(surf, rect)
