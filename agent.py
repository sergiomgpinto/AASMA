import abc
import dataclasses
import numpy as np
from grid import Map
from drone import Drone, Action


@dataclasses.dataclass
class Observation(abc.ABC):
    """Defines the observation for a given agent."""


@dataclasses.dataclass
class RandomObservation(Observation):

    def __init__(self, map, drone):
        self.adj_locations = map.adj_positions(drone.loc)
        self.current_energy = drone.battery_available
        self.current_loc = drone.loc
        self.current_seeds = drone.nr_seeds
        self.adj_cell_types = [map.get_cell_type(loc) for loc in self.adj_locations]


class Agent(abc.ABC):
    """Base class for all agents."""

    def __init__(self, agent_id: int, max_number_of_seeds: int, max_battery_available: int, map: Map) -> None:
        self.last_observation = None
        self._agent_id = agent_id
        self.rng = np.random.default_rng()
        self.drone = self.create_drone(agent_id, max_number_of_seeds, max_battery_available, map)

    @abc.abstractmethod
    def see(self, map: Map) -> None:
        """Observes the current state of the environment through its sensors."""
        pass

    @abc.abstractmethod
    def choose_action(self) -> Action:
        """Acts based on the last observation and any other information."""
        pass

    @abc.abstractmethod
    def reset(self) -> Action:
        pass

    def create_drone(self, id: int, max_number_of_seeds: int, max_battery_available: int, map: Map) -> Drone:
        """Creates a drone with a random location.
        The drone initial location will not overlap with another drone."""

        possible_drone_locations = [location for location in map.possible_drone_positions]
        location = self.rng.choice(possible_drone_locations)
        drone = Drone(loc=location, id=id, max_number_of_seeds=max_number_of_seeds,
                      max_battery_available=max_battery_available, distance_between_fertile_lands=0,
                      distance_needed_to_identify_fertile_land=list(), energy_per_planted_tree=list())

        return drone

    def get_drone(self):
        return self.drone


class RandomAgent(Agent):
    """Baseline agent that randomly chooses an action at each timestep."""

    def __init__(self, agent_id: int, max_number_of_seeds: int, max_battery_available: int, map: Map) -> None:
        super().__init__(agent_id, max_number_of_seeds, max_battery_available, map)

    def see(self, map: Map) -> None:
        self.last_observation = RandomObservation(map, self.drone)
        self.drone.update_map(self.last_observation)

    def choose_action(self) -> Action:
        action = self.rng.choice(self.drone.actions)
        return action

    def reset(self):
        self.drone = self.create_drone(self._agent_id, self.drone.max_number_of_seeds, self.drone.max_battery_available, self.drone.map)
