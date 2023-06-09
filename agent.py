import abc
import numpy as np
from communication import Communication, MapUpdatePayload, EnergyAndSeedLevelsStatusPayload, DroneLocationPayload
from grid import Map, Position
from strategy import Strategy, FertilityFocused, CooperativeCharging, ConsensusDecisionMaking


class Observation(abc.ABC):
    """Defines the observation for a given agent."""


class RandomObservation(Observation):
    """Defines the observation for the random agent."""

    def __init__(self):
        # TODO rethink we need stuff here
        pass


class GreedyObservation(Observation):
    """Defines the observation for the greedy agent."""

    def __init__(self, map, drone):
        self.adj_locations = map.adj_positions(drone.loc)
        self.current_energy = drone.get_battery_available()
        self.current_loc = drone.get_loc()
        self.current_cell_type = map.get_cell_type(self.current_loc)
        self.current_seeds = drone.get_nr_seeds()
        self.adj_cell_types = [map.get_cell_type(loc) for loc in self.adj_locations]
        #self.distance_to_fertile_land = drone.get_distance_needed_to_identify_fertile_land()
        #self.distance_between_fertile_lands = drone.get_distance_between_fertile_lands()
        self.avg_energy_used_per_planted_tree = drone.get_avg_of_drone_energy_used_per_planted_tree()

    def get_adj_locations(self):
        """Returns the adjacent locations."""
        return self.adj_locations

    def get_current_cell_type(self):
        """Returns the current cell type."""
        return self.current_cell_type

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

    def get_distance_to_fertile_land(self):
        """Returns the distance to the nearest fertile land."""
        return self.distance_to_fertile_land

    def get_distance_between_fertile_lands(self):
        """Returns the distance between fertile lands."""
        return self.distance_between_fertile_lands

    def get_avg_energy_used_per_planted_tree(self):
        """Returns the average energy used per planted tree."""
        return self.avg_energy_used_per_planted_tree


class CommunicativeObservation(Observation):
    """Defines the observation for the communicative agent."""

    def __init__(self, map, drone):
        self.adj_locations = map.adj_positions(drone.loc)
        self.current_energy = drone.get_battery_available()
        self.current_loc = drone.get_loc()
        self.current_seeds = drone.get_nr_seeds()
        self.adj_cell_types = [map.get_cell_type(loc) for loc in self.adj_locations]
        self.messages = drone.read_messages()

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

    def get_messages(self):
        """Returns the messages."""
        return self.messages

    def get_loc(self):
        """Returns the location."""
        return self.current_loc


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
    def choose_action(self):
        """Acts based on the last observation and any other information."""
        pass

    @abc.abstractmethod
    def reset(self):
        """Resets the agent to its initial state."""
        pass

    def create_drone(self, id: int, max_number_of_seeds: int, max_battery_available: int, map: Map):
        from drone import Drone
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


class RandomAgent(Agent):
    """Baseline agent that randomly chooses an action at each timestep."""

    def __init__(self, agent_id: int, max_number_of_seeds: int, max_battery_available: int, map: Map) -> None:
        super().__init__(agent_id, max_number_of_seeds, max_battery_available, map)

    def see(self, map: Map) -> None:
        """Observes the current state of the environment through its sensors."""
        self.last_observation = RandomObservation()

    def choose_action(self):
        """Chooses action randomly."""
        action = self.rng.choice(self.drone.actions)
        return action

    def reset(self):
        """Resets the drone associated with the agent."""
        self.drone = self.create_drone(self._agent_id, self.drone.max_number_of_seeds, self.drone.max_battery_available,
                                       self.drone.map)


def has_enough_energy(drone, target):
    """
    Checks that there is enough energy to go to nearest plantable square and head back to charging station,
    considering the drone's current position, the target and the target's distance to the charging station.

    """
    target_cost = len(breadth_first_search(drone.get_loc(), target))
    battery_cost = target_cost + len(breadth_first_search(target, drone.get_charging_station()))

    return drone.get_battery_available() > battery_cost


def breadth_first_search(source: Position, target: Position) -> list[Position]:
    """Computes the list of positions in the path from source to target.
    It uses a BFS so the path is the shortest path."""

    queue = [(source, (source,))]

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


def move_in_path_and_act(agent_drone, path: list[Position], goal):
    from drone import Action, Goal

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


def go_to_charging_station(drone):
    from drone import Goal

    shortest_path = breadth_first_search(drone.get_loc(), drone.get_charging_station())
    action = move_in_path_and_act(drone, shortest_path, Goal.CHARGE)

    return action


def plant_nearest_square(drone):
    from drone import Action, Goal

    plantable_squares = drone.get_map().plantable_squares()

    if len(plantable_squares) == 0:
        actions = drone.actions.copy()
        actions.remove(Action.PLANT)
        actions.remove(Action.CHARGE)
        actions.remove(Action.STAY)
        return np.random.choice(drone.actions)

    shortest_paths = [breadth_first_search(drone.get_loc(), p) for p in plantable_squares]
    shortest_path_id = np.argmin([len(p) for p in shortest_paths])

    if has_enough_energy(drone, plantable_squares[shortest_path_id]):
        if len(shortest_paths[shortest_path_id]) == 1 and drone.get_loc() == shortest_paths[shortest_path_id][0]:
            return Action.PLANT
        else:
            action = move_in_path_and_act(drone, shortest_paths[shortest_path_id], Goal.PLANT)
            return action
    else:
        return go_to_charging_station(drone)


class GreedyAgent(Agent):
    """Agent that plans its path using a BFS."""

    def __init__(self, agent_id: int, max_number_of_seeds: int, max_battery_available: int, map: Map) -> None:
        super().__init__(agent_id, max_number_of_seeds, max_battery_available, map)

    def see(self, map: Map) -> None:
        self.last_observation = GreedyObservation(map, self.drone)
        self.drone.update_map_greedy(self.last_observation)
        self.drone.get_map().update_planted_squares()

    def choose_action(self):
        from drone import Action

        location = self.drone.get_loc()
        charging_station = self.drone.get_charging_station()

        # No seeds
        if self.drone.get_nr_seeds().count(0) >= 1:
            return go_to_charging_station(self.drone)

        path_size_to_cs = len(breadth_first_search(location, charging_station))

        if path_size_to_cs == 0:
            return Action.CHARGE

        # Greedy because it assumes once it gets to the charging station it will be able to charge
        if path_size_to_cs + 1 == self.drone.get_battery_available():
            return go_to_charging_station(self.drone)
        else:
            return plant_nearest_square(self.drone)

    def reset(self):
        self.drone = self.create_drone(self._agent_id, self.drone.max_number_of_seeds, self.drone.max_battery_available,
                                       self.drone.map)


class CommunicativeAgent(Agent):
    """Agent that communicates with other agents."""

    def __init__(self, agent_id: int, max_number_of_seeds: int, max_battery_available: int, map: Map) -> None:
        super().__init__(agent_id, max_number_of_seeds, max_battery_available, map)
        # TODO: Make this changable through config file
        self.strategies = [FertilityFocused(), CooperativeCharging(), ConsensusDecisionMaking()]
        self.communication = None

    def see(self, map: Map) -> None:
        self.last_observation = CommunicativeObservation(map, self.drone)
        self.drone.update_map_coomunicative(self.last_observation)
        self.drone.update_energy_and_seed_level_status(self.last_observation)
        self.drone.update_drone_location(self.last_observation)
        self.send_sensors_messages(self.last_observation)

    def choose_action(self):
        from drone import Action, Goal
        goal = None
        energy_to_station = 0

        # Charge goal
        if self.drone.get_map().find_charging_station() is not None:
            if self.drone.get_battery_available() <= energy_to_station * 2:
                goal = Goal.CHARGE
        else:
            if self.drone.get_battery_available() < self.drone.get_max_battery_available() * 0.5:
                goal = Goal.CHARGE

        # Charge seeds
        if self.drone.get_nr_seeds().count(0) == 1:
            goal = Goal.CHARGE

        #

    def reset(self) -> None:
        pass

    def add_strategy(self, strategy: Strategy) -> None:
        """Adds a strategy to the agent."""
        self.strategies.append(strategy)

    def remove_strategy(self, strategy: Strategy) -> None:
        """Removes a strategy from the agent."""
        self.strategies.remove(strategy)

    def get_strategies(self) -> list[Strategy]:
        """Returns the strategies of the agent."""
        return self.strategies

    def set_agents(self, agents: list[Agent]) -> None:
        """Sets the agents of the agent."""
        self.communication = Communication(self._agent_id, agents)

    def get_communication(self):
        """Returns the communication of the agent."""
        return self.communication

    def send_sensors_messages(self, observation: CommunicativeObservation) -> None:
        """Sends the sensors status to the other agents."""
        adj_locations = observation.get_adj_locations()
        adj_cell_types = observation.get_adj_cell_types()
        payload = MapUpdatePayload(adj_locations, adj_cell_types)
        self.get_communication().send_map_update(payload)

        energy = observation.get_current_energy()
        seeds = observation.get_current_seeds()
        payload = EnergyAndSeedLevelsStatusPayload(energy, seeds)
        self.get_communication().send_energy_and_seed_levels_status(payload)

        location = observation.get_loc()
        payload = DroneLocationPayload(location)
        self.get_communication().send_drone_location(payload)

    # def send_actuartors_messages(self):
