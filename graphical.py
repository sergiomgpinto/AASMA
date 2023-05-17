import pygame


def pathToImage(filename, ext = "png"):
    return f"environment/Images/{filename}.{ext}"


class EnvironmentPrinter(env.Printer):
    def __init__(
        self,
        grid: np.ndarray
    ):
        self.grid = grid
        
        
    def print(self, env: env.Environment):
        env_grid = env.map.grid
        n_cols, n_rows = env_grid.shape
        
        # for cell graphical representation size
        assert self.__height % n_cols == 0, "display height is not divisible by number of columns in grid"
        assert self.__width % n_rows == 0, "display width is not divisible by number of rows in grid"
        
        cell_height = self.__height // n_cols
        cell_width = self.__width // n_rows

        # Print roads and sidewalks
        road_printer = RoadPrinter(
            screen=self.__screen, cell_width=cell_width, cell_height=cell_height,
        )
        sidewalk_printer = SidewalkPrinter(
            screen=self.__screen, cell_width=cell_width, cell_height=cell_height,
        )

        for pos in env.map.all_positions:
            if env.map.is_road(pos):
                road_printer.print(pos)
            elif env.map.is_sidewalk(pos):
                sidewalk_printer.print(pos)
            else:
                raise ValueError(f"Position not road or sidewalk: {pos}")

        # Print taxis
        taxi_printer = TaxiPrinter(
            screen=self.__screen,
            cell_width=cell_width,
            cell_height=cell_height,
            pick_colour_fn=self._pick_passenger_colour
        )
        for t in env.taxis:
            taxi_printer.print(t)

        # Print passengers
        self._remove_colours_for_disapeared_passengers(env.passengers)

        pass_printer = PassengerPrinter(
            screen=self.__screen, 
            cell_width=cell_width, 
            cell_height=cell_height,
            pick_colour_fn=self._pick_passenger_colour,
        )
        for p in env.passengers:
            pass_printer.print(p)

        pygame.display.flip()

        
    def __enter__(self):
        pygame.init()
        n_cells = self.grid.shape[0] * self.grid.shape[1]
        self.__width = self.__height = ((min(pygame.display.Info().current_w, pygame.display.Info().current_h) * 0.8) // n_cells) * n_cells
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
        #Change function colour name
        self._screen.blit(self.colour(), (left,top))
   
     
class PineTreePrinter(CellPrinter):
    def colour(self):
        return pygame.transform.scale(pygame.image.load(pathToImage("Pine")), (self._cell_width, self._cell_height))
    
class OakTreePrinter(CellPrinter):
    def colour(self):
        return pygame.transform.scale(pygame.image.load(pathToImage("Oak")), (self._cell_width, self._cell_height))
    
class EukalyptusTreePrinter(CellPrinter):
    def colour(self):
        return pygame.transform.scale(pygame.image.load(pathToImage("Eucalyptus")), (self._cell_width, self._cell_height))
    
class ObstaclePrinter(CellPrinter):
    def colour(self):
        return pygame.transform.scale(pygame.image.load(pathToImage("Obstacle")), (self._cell_width, self._cell_height))
    
class ChargingStationPrinter(CellPrinter):
    def colour(self):
        return pygame.transform.scale(pygame.image.load(pathToImage("ChargingStation")), (self._cell_width, self._cell_height))
    
class FertileLandPrinter(CellPrinter):
    def colour(self):
        return pygame.transform.scale(pygame.image.load(pathToImage("FertileLand")), (self._cell_width, self._cell_height))