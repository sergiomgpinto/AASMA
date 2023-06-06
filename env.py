import abc
import dataclasses
import enum
import grid as grid
import log
import numpy as np
import drone as drone
import chargingstation as chargingstation
from typing import List, Optional, Any


@dataclasses.dataclass
class Observation:
    """Defines the observation for a given agent.
    
    Attributes:
        map: each drone has its own map of the environment, updated at each time step
        drones: list of other drones ??? 
        --------------------------------------------------
        FIXME
        loc: position of the agent drone in the grid.
        has_seeds: whether the agent drone has a seeds or not. (???)
        energy_levels: how much energy the drone has.
        drones_pos: positions of all the drones in the grid.
    """

    map: grid.Map
    drones: List[drone.Drone]


class Action(enum.Enum):
    """Specifies possible actions the drones can perform."""

    UP = 0
    """Moves the drone up."""

    DOWN = 1
    """Moves the drone down."""

    LEFT = 2
    """Moves the drone to the left."""

    RIGHT = 3
    """Moves the drone to the right."""

    STAY = 4
    """Stays in the same position."""

    PLANT = 5
    """Plants fertile land."""

    CHARGE = 6
    """Charges drone's batery."""

    UP_RIGHT = 7
    """Moves the drone diagonally to the upper right square."""

    UP_LEFT = 8
    """Moves the drone diagonally to the upper right square."""

    DOWN_RIGHT = 9
    """Moves the drone down diagonally to the right square."""

    DOWN_LEFT = 10
    """Moves the drone down diagonally to the right square."""

    def __repr__(self) -> str:
        return f"Action({self.name})"


@dataclasses.dataclass
class Environment:
    drones: List[drone.Drone]
    chargingstations: chargingstation.ChargingStation

    def __init__(self, map: grid.Map, init_drones: int, printer: "Optional[Printer]" = None,
                 log_level: Optional[str] = "info", max_timesteps: Optional[int] = 150, seed: Optional[int] = None):
        self.all_drones_dead = None
        self._timestep = None
        self.terminal = None
        self.map = map
        self.planted_squares = map.planted_squares()
        self._rng = np.random.default_rng(seed=seed)
        self._printer = printer
        self._logger = log.new(__name__, lvl=log_level)
        self._init_drones = init_drones
        self._max_timesteps = max_timesteps
        self.occupied_squares_with_drones = []

    def reset(self, max_number_of_seeds, max_battery_available) -> List[Observation]:
        self._timestep = 0
        self.terminal = False
        self.occupied_squares_with_drones = []
        self.drones = []

        for i in range(self._init_drones):
            self.drones.append(self.create_drone(i, max_number_of_seeds, max_battery_available))
        observation = Observation(map=self.map, drones=self.drones)
        return [observation for _ in range(len(self.drones))]

    def render(self):
        self._printer.print(self)

    def create_drone(self, id: int, max_number_of_seeds: int, max_battery_available: int) -> drone.Drone:
        """Creates a drone with a random location and direction.
        
        The drone initial location will not overlap with another drone."""

        possible_drone_locations = [l for l in self.map.possible_drone_positions
                                    if l not in self.occupied_squares_with_drones]
        loc = self._rng.choice(possible_drone_locations)
        self.occupied_squares_with_drones.append(loc)
        temp_drone = drone.Drone(loc=loc, map=self.map, id=id, max_number_of_seeds=max_number_of_seeds,
                                    max_battery_available=max_battery_available)
        log.create_drone(self._logger, self._timestep, temp_drone)
        return temp_drone

    def move_drone(self, drone: drone.Drone, action: Action):
        """Move a drone according to an action."""
        target_loc = None
        target_dir = None

        if action == Action.UP:
            target_loc = drone.loc.up
            target_dir = drone.direction.UP
        elif action == Action.DOWN:
            target_loc = drone.loc.down
            target_dir = drone.direction.DOWN
        elif action == Action.RIGHT:
            target_loc = drone.loc.right
            target_dir = drone.direction.RIGHT
        elif action == Action.LEFT:
            target_loc = drone.loc.left
            target_dir = drone.direction.LEFT
        elif action == Action.UP_RIGHT:
            target_loc = drone.loc.up_right
            target_dir = drone.direction.UP_RIGHT
        elif action == Action.UP_LEFT:
            target_loc = drone.loc.up_left
            target_dir = drone.direction.UP_LEFT
        elif action == Action.DOWN_RIGHT:
            target_loc = drone.loc.down_right
            target_dir = drone.direction.DOWN_RIGHT
        elif action == Action.DOWN_LEFT:
            target_loc = drone.loc.down_left
            target_dir = drone.direction.DOWN_LEFT

        if self.map.is_inside_map(target_loc):
            drone.loc = target_loc
            drone.direction = target_dir

    def step(self, actions: List[Action]) -> tuple[list[Observation], bool, bool | Any]:
        """Performs an environment step.

        Args:
            actions: List of actions returned by the agents.

        Returns: List of observations for the agents.
        """

        self._timestep += 1

        for i, act in enumerate(actions):
            log.choosen_action(self._logger, self._timestep, i, act)

        # Perform agent actions
        for drone, act in zip(self.drones, actions):
            if drone.battery_available != 0:
                if act in (Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT,
                           Action.UP_RIGHT, Action.UP_LEFT, Action.DOWN_RIGHT, Action.DOWN_LEFT):
                    self.move_drone(drone, act)
                elif act == Action.PLANT:
                    p = drone.loc
                    planted_with_sucess, s = drone.plant(self.map)
                    if planted_with_sucess:
                        self.map.change_cell_type(p, s)
                        self.planted_squares.append((p, s))

                elif act == Action.CHARGE:
                    drone.charge()

                elif act == Action.STAY:
                    pass
                drone.battery_available -= 1
                drone.total_distance += 1
            else:
                drone.is_dead = True
            log.drone(self._logger, self._timestep, drone)

        observation = Observation(map=self.map, drones=self.drones)

        for d in self.drones:
            d.map = observation.map

        self.terminal = len(self.map.plantable_squares()) == 0
        self.all_drones_dead = all([d.is_dead for d in self.drones])
        #self.percentage_of_planted_trees =
        return [observation for _ in range(len(actions))], self.terminal, self.all_drones_dead #\
               #self.percentage_of_planted_trees


class Printer(abc.ABC):
    @abc.abstractmethod
    def print(self, env: Environment):
        pass
