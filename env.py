import abc
import dataclasses
import enum
import grid
import log
import numpy as np
import drone as drone
import chargingstation as chargingstation
from typing import List, Optional, Tuple


@dataclasses.dataclass(frozen=True)
class Observation:
    """Defines the observation for a given agent."""

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

    def __repr__(self) -> str:
        return f"Action({self.name})"


def move_drone(d: drone.Drone, action: Action):
    """Move a drone according to an action."""
    if action == Action.UP:
        target_loc = d.loc.up
        target_dir = d.direction.UP
    elif action == Action.DOWN:
        target_loc = d.loc.down
        target_dir = d.direction.DOWN
    elif action == Action.RIGHT:
        target_loc = d.loc.right
        target_dir = d.direction.RIGHT
    elif action == Action.LEFT:
        target_loc = d.loc.left
        target_dir = d.direction.LEFT
    else:
        raise ValueError(f"Unknown direction in drone movement {d.direction}")

    d.loc = target_loc
    d.direction = target_dir


@dataclasses.dataclass
class Environment:
    drones: List[drone.Drone]
    charging_station: chargingstation.ChargingStation
    map: grid.Map

    def __init__(
            self,
            env_map: grid.Map,
            planted_squares: list[Tuple],
            init_drones: int,
            printer: "Optional[Printer]" = None,
            log_level: Optional[str] = "info",
            max_timesteps: Optional[int] = 150,
            seed: Optional[int] = None,
    ):
        self._timestep = 0
        self.map = env_map
        self.planted_squares = planted_squares
        self._rng = np.random.default_rng(seed=seed)
        self._printer = printer
        self._logger = log.new(__name__, lvl=log_level)
        self._init_drones = init_drones
        self._max_timesteps = max_timesteps
        self.terminal = False

    def reset(self) -> List[Observation]:
        self._timestep = 0
        self.terminal = False
        self.drones = []

        for i in range(self._init_drones):
            self.drones.append(self.create_drone(i))
        observation = Observation(map=self.map, drones=self.drones)
        return [observation for _ in range(len(self.drones))]

    def step(self, *actions: Action) -> tuple[list[Observation], bool]:
        """Performs an environment step.
        
        Args:
            actions: List of actions returned by the agents.

        Returns: List of observations for the agents.
        """
        actions = list(actions)
        assert len(self.drones) == len(actions), f"Received {len(actions)} actions for {len(self.drones)} agents."

        self._timestep += 1

        # Log actions
        for i, act in enumerate(actions):
            log.choosen_action(self._logger, self._timestep, i, act)

        # Perform agent actions
        for d, act in zip(self.drones, actions):
            if act in (Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT):
                move_drone(d, act)
                d.batery_available -= 1
                d.total_distance += 1

            elif act == Action.PLANT:
                d.plant()
            elif act == Action.CHARGE:
                d.charge()
            elif act == Action.STAY:
                pass

            else:
                raise ValueError(f"Unknown action: {act}")
            log.drone(self._logger, self._timestep, d)

        observation = Observation(map=self.map, drones=self.drones)

        self.terminal = len(self.map.plantable_squares()) == 0 or self._timestep == self._max_timesteps

        return [observation for _ in range(len(actions))], self.terminal

    def render(self):
        if not self._printer:
            raise ValueError("Unable to render without printer")
        self._printer.print(self)

    def create_drone(self, drone_id: int) -> drone.Drone:
        """Creates a drone with a random location and direction.
        
        The drone initial location will not overlap with another drone."""

        occupied_locations = set()
        for d in self.drones:
            occupied_locations.add(d.loc)

        possible_drone_locations = [
            loc for loc in self.map.possible_drone_positions
            if loc not in occupied_locations
        ]

        if len(possible_drone_locations) == 0:
            raise ValueError("Unable to create drone: Not enough free locations.")
        loc = self._rng.choice(possible_drone_locations)

        possible_drone_directions = [drone.Direction.UP,
                                     drone.Direction.DOWN,
                                     drone.Direction.LEFT, drone.Direction.RIGHT]

        direction = self._rng.choice(possible_drone_directions)
        temp_drone = drone.Drone(loc=loc, map=self.map, direction=direction, id=drone_id)
        log.create_drone(self._logger, self._timestep, temp_drone)
        return temp_drone


class Printer(abc.ABC):
    @abc.abstractmethod
    def print(self, env: Environment):
        pass
