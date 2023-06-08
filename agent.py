import abc
import dataclasses
import numpy as np
import env as env
from grid import Map, Position
from drone import Drone, Action, Goal
from abc import ABC
from strategy import Strategy


@dataclasses.dataclass
class Observation(abc.ABC):
    """Defines the observation for a given agent."""


@dataclasses.dataclass
class RandomObservation(Observation):
    """Defines the observation for the random agent."""
    def __init__(self, map, drone):
        self.adj_locations = map.adj_positions(drone.loc)
        self.current_energy = drone.get_battery_available()
        self.current_loc = drone.get_loc()
        self.current_seeds = drone.get_nr_seeds()
        self.adj_cell_types = [map.get_cell_type(loc) for loc in self.adj_locations]

    def get_adj_locations(self):
        """Returns the adjacent locations."""
        return self.adj_locations

    def get_current_energy(self):
        """Returns the current energy level."""
        return self.current_energy

    def get_current_loc(self):
        """Returns the current location."""
        return self.current_loc

    def get_current_seeds(self):
        """Returns the current seeds."""
        return self.current_seeds

    def get_adj_cell_types(self):
        """Returns the adjacent cell types."""
        return self.adj_cell_types


class Agent(abc.ABC):
    """Base class for all agents."""

    def __init__(self, agent_id: int, max_number_of_seeds: int, max_battery_available: int, map: Map) -> None:
        self.last_observation = None
        self._agent_id = agent_id
        self.rng = np.random.default_rng()
        self.drone = self.create_drone(agent_id, max_number_of_seeds, max_battery_available, map)
        self.messages = []

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
        """Resets the agent to its initial state."""
        pass

    def create_drone(self, id: int, max_number_of_seeds: int, max_battery_available: int, map: Map) -> Drone:
        """Creates a drone in a random location.
        The drone initial location may overlap with another drone."""

        possible_drone_locations = [location for location in map.possible_drone_positions]
        location = self.rng.choice(possible_drone_locations)
        drone = Drone(loc=location, id=id, max_number_of_seeds=max_number_of_seeds,
                      max_battery_available=max_battery_available, distance_between_fertile_lands=0,
                      distance_needed_to_identify_fertile_land=list(), energy_per_planted_tree=list(),
                      charging_station_loc=map.find_charging_station())

        return drone

    def get_drone(self):
        """Returns the drone."""
        return self.drone

    def get_id(self):
        """Returns the agent id."""
        return self._agent_id

    def receive_message(self, message):
        """Receives a message."""
        self.messages.append(message)

    def read_messages(self):
        """Reads the messages."""
        return self.messages

    def reset_messages(self):
        """Resets the messages."""
        self.messages = []


class RandomAgent(Agent):
    """Baseline agent that randomly chooses an action at each timestep."""

    def __init__(self, agent_id: int, max_number_of_seeds: int, max_battery_available: int, map: Map) -> None:
        super().__init__(agent_id, max_number_of_seeds, max_battery_available, map)

    def see(self, map: Map) -> None:
        """Observes the current state of the environment through its sensors."""
        self.last_observation = RandomObservation(map, self.drone)

    def choose_action(self) -> Action:
        """Chooses action randomly."""
        action = self.rng.choice(self.drone.actions)
        return action

    def reset(self):
        """Resets the drone associated with the agent."""
        self.drone = self.create_drone(self._agent_id, self.drone.max_number_of_seeds, self.drone.max_battery_available,
                                       self.drone.map)


class EnergyBased(Agent, ABC):
    """Utility class with path based functions."""

    def _has_enough_energy(self, agent_drone: Drone, target: Position) -> bool:
        """
        Checks that there is enough energy to go to nearest plantable square and head back to charging station,
        considering the drone's current position, the target and the target's distance to the charging station.

        """
        from default import MAP
        map = Map(MAP)
        battery_cost = len(_bfs_with_positions(map, agent_drone.loc, target)) + len(
            _bfs_with_positions(map, target, map.find_charging_station()))
        return agent_drone.battery_available > battery_cost


def _bfs_with_positions(map: Map, source: Position, target: Position) -> list[Position]:
    """Computes the list of positions in the path from source to target.

    It uses a BFS so the path is the shortest path."""

    # The queue stores tuple with the nodes to explore
    # and the path taken to the node.
    queue = [(source, (source,))]
    # Visited stores already explored positions to avoid
    # loops._move_in_path_and_act
    visited = set()

    while len(queue) > 0:
        curr, curr_path = queue.pop(0)

        if curr == target:
            return list(curr_path)
        for neighbour in curr.adj:
            if neighbour not in visited:
                neighbour_path = curr_path + (neighbour,)
                queue.append((neighbour, neighbour_path))
                visited.add(neighbour)

    raise ValueError("No path found")


class PathBased(EnergyBased, ABC):
    """Utility class with path based functions."""

    def _plant_nearest_square(self, agent_drone: Drone) -> Action:
        from default import MAP
        from grid import Map
        plantable_pos = Map(MAP).plantable_squares()
        if len(plantable_pos) == 0:
            return Action.STAY
        shortest_paths = [
            _bfs_with_positions(MAP, agent_drone.loc, p)
            for p in plantable_pos
        ]
        path_idx = np.argmin([len(p) for p in shortest_paths])
        if self._has_enough_energy(agent_drone, plantable_pos[path_idx]):
            if len(shortest_paths[path_idx]) == 1 and agent_drone.loc == shortest_paths[path_idx][0]:
                return Action.PLANT
            else:
                action = self._move_in_path_and_act(agent_drone, shortest_paths[path_idx], env.Action.PLANT,
                                                    Goal.PLANT)
                return action
        else:
            return self._go_to_charging_station(agent_drone)

    def _go_to_charging_station(self, agent_drone: Drone) -> Action:

        charging_station_pos = agent_drone.map.find_charging_station()  # TODO find_closest no caso de querermos ter várias estações ativas
        shortest_path = _bfs_with_positions(agent_drone.map, agent_drone.loc, charging_station_pos)
        action = self._move_in_path_and_act(agent_drone, shortest_path, Action.CHARGE, Goal.CHARGE)
        return action

    def _move_in_path_and_act(self, agent_drone: Drone, path: list[Position], last_action: env.Action,
                              goal: Goal) -> Action:
        if len(path) == 1:
            curr_pos = agent_drone.loc
            next_pos = path[0]
            if curr_pos == next_pos:
                if goal == Goal.PLANT:
                    return Action.PLANT
                if goal == Goal.CHARGE:
                    return Action.CHARGE
        else:
            curr_pos = path[0]
            next_pos = path[1]
        if next_pos == curr_pos.up:
            return Action.UP
        elif next_pos == curr_pos.down:
            return Action.DOWN
        elif next_pos == curr_pos.left:
            return Action.LEFT
        elif next_pos == curr_pos.right:
            return Action.RIGHT
        elif next_pos == curr_pos.up_right:
            return Action.UP_RIGHT
        elif next_pos == curr_pos.up_left:
            return Action.UP_LEFT
        elif next_pos == curr_pos.down_right:
            return Action.DOWN_RIGHT
        elif next_pos == curr_pos.down_left:
            return Action.DOWN_LEFT
        else:
            raise ValueError(
                f"Unknown adj direction: (curr_pos: {curr_pos}, next_pos: {next_pos})"
            )


class GreedyAgent(PathBased):
    """Agent that plans its path using a BFS."""

    def __init__(self, agent_id: int, max_number_of_seeds: int, max_battery_available: int, map: Map) -> None:
        super().__init__(agent_id, max_number_of_seeds, max_battery_available, map)

    def see(self, map: Map) -> None:
        self.last_observation = RandomObservation(map, self.drone)
        self.drone.update_map(self.last_observation)

    def choose_action(self) -> Action:
        from default import MAP

        if self.drone.nr_seeds.count(0) == 3 or len(_bfs_with_positions(MAP, self.drone.get_loc(),
                                                                        self.drone.get_charging_station())) == self.drone.get_battery_available() + 1:
            return self._go_to_charging_station(self.drone)
        else:
            return self._plant_nearest_square(self.drone)

    def reset(self):
        self.drone = self.create_drone(self._agent_id, self.drone.max_number_of_seeds, self.drone.max_battery_available,
                                       self.drone.map)


class CommunicativeAgent(Agent):
    """Agent that communicates with other agents."""
    def __init__(self, agent_id: int, max_number_of_seeds: int, max_battery_available: int, map: Map) -> None:
        super().__init__(agent_id, max_number_of_seeds, max_battery_available, map)
        self.strategies = []

    def see(self, map: Map) -> None:
        pass

    def choose_action(self) -> Action:
        pass

    def reset(self) -> None:
        pass

    def add_strategy(self, strategy: Strategy) -> None:
        self.strategies.append(strategy)

    def remove_strategy(self, strategy: Strategy) -> None:
        self.strategies.remove(strategy)

    def get_strategies(self) -> list[Strategy]:
        return self.strategies
