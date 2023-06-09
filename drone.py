import enum
import numpy as np
import yaml
from agent import GreedyObservation, CommunicativeObservation
from communication import MapUpdateMessage, EnergyAndSeedLevelsStatusMessage, ChargingStatusMessage, \
    DronePlantingMessage, DroneLocationMessage
from grid import Map
from grid import Cell


class Goal(enum.Enum):
    """Defines the goal for a given agent."""
    PLANT = 1
    CHARGE = 2
    WAIT = 3

    def __repr__(self) -> str:
        return f"Goal({self.name})"


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


class Drone:
    """Defines the drone."""

    def __init__(self, loc, id, max_number_of_seeds, max_battery_available, distance_between_fertile_lands,
                 distance_needed_to_identify_fertile_land, energy_per_planted_tree, charging_station_loc):

        self.loc = loc
        self.id = id
        self.max_number_of_seeds = max_number_of_seeds
        self.max_battery_available = max_battery_available
        self.distance_between_fertile_lands = distance_between_fertile_lands
        self.distance_needed_to_identify_fertile_land = distance_needed_to_identify_fertile_land
        self.energy_per_planted_tree = energy_per_planted_tree
        self.battery_available = self.max_battery_available
        self.energy_used_before_planted_tree = 0
        self.nr_seeds = [self.max_number_of_seeds, self.max_number_of_seeds,
                         self.max_number_of_seeds]  # [OAK_TREE,PINE_TREE,EUCALYPTUS]
        self.total_distance = 0
        self.is_dead = False
        self.actions = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT, Action.STAY, Action.PLANT, Action.CHARGE,
                        Action.UP_RIGHT, Action.UP_LEFT, Action.DOWN_RIGHT, Action.DOWN_LEFT]

        with open("./config.yml", "r") as fp:
            data = yaml.safe_load(fp)

        # Every type of agent starts without knowing the map
        self.map = Map(np.full((data["map_size"], data["map_size"]), Cell.UNKNOWN))
        self.charging_station = charging_station_loc
        self.map.get_grid()[charging_station_loc.y, charging_station_loc.x] = Cell.CHARGING_STATION

    def set_dead(self):
        """Sets drone as dead."""
        self.is_dead = True

    def get_loc(self):
        """Returns drone's location."""
        return self.loc

    def get_nr_seeds(self):
        """Returns drone's number of seeds."""
        return self.nr_seeds

    def get_map(self):
        """Returns drone's map."""
        return self.map

    def get_max_battery_available(self):
        """Returns drone's max battery available."""
        return self.max_battery_available

    # TODO: remove this method
    def get_charging_station(self):
        """Returns charging station's location."""
        return self.charging_station

    def is_drone_dead(self):
        """Returns True if drone is dead, False otherwise."""
        return self.is_dead

    def get_battery_available(self):
        """Returns drone's battery."""
        return self.battery_available

    def charge(self):
        """
        Charges batery. Will only have effect if drone is positioned in charging station, if the charging station
        isn't occupied by another drone and if the agent chooses the action charge.
        """
        if self.map.find_charging_station() == self.loc:
            self.battery_available = self.max_battery_available
            self.nr_seeds = [self.max_number_of_seeds, self.max_number_of_seeds, self.max_number_of_seeds]

    def plant(self, map: Map) -> tuple[bool, Cell]:
        """
        Drone plants fertile land where he is located.
        """
        if map.is_fertile_land(self.loc):
            tree_id = map.get_type_of_tree_that_should_be_planted(self.loc)
            if self.nr_seeds[tree_id] > 0:
                self.nr_seeds[tree_id] -= 1
                self.energy_per_planted_tree.append(self.energy_used_before_planted_tree)
                self.energy_used_before_planted_tree = 0
                return True, map.map_id_to_cell_type(tree_id)
            else:
                # Unknown here means nothing, it's just a filler
                return False, Cell.UNKNOWN
        else:
            # Unknown here means nothing, it's just a filler
            return False, Cell.UNKNOWN

    def move(self, action: Action):
        """Move a drone according to an action."""
        target_loc = None

        if action == Action.UP:
            target_loc = self.loc.up
        elif action == Action.DOWN:
            target_loc = self.loc.down
        elif action == Action.RIGHT:
            target_loc = self.loc.right
        elif action == Action.LEFT:
            target_loc = self.loc.left
        elif action == Action.UP_RIGHT:
            target_loc = self.loc.up_right
        elif action == Action.UP_LEFT:
            target_loc = self.loc.up_left
        elif action == Action.DOWN_RIGHT:
            target_loc = self.loc.down_right
        elif action == Action.DOWN_LEFT:
            target_loc = self.loc.down_left

        if self.map.is_inside_map(target_loc):
            self.loc = target_loc

    def update_metrics(self, map: Map):
        """Updates drone's metrics."""
        self.battery_available -= 1
        self.total_distance += 1
        self.distance_between_fertile_lands += 1
        self.energy_used_before_planted_tree += 1
        self.update_distance_needed_to_identify_fertile_land(map)

    def update_distance_needed_to_identify_fertile_land(self, map: Map):
        """Updates distance needed to identify fertile land."""
        if map.is_fertile_land(self.loc):
            self.distance_needed_to_identify_fertile_land.append(self.distance_between_fertile_lands)
            self.distance_between_fertile_lands = 0

    def get_avg_of_drone_energy_used_per_planted_tree(self):
        """Returns the average of the energy used per planted tree."""
        if len(self.energy_per_planted_tree) != 0:
            return np.mean(self.energy_per_planted_tree)
        else:
            return -1

    def update_map_greedy(self, observation: GreedyObservation):
        """Updates drone's map."""
        adj_positions = observation.get_adj_locations()
        cell_types = observation.get_adj_cell_types()
        location = observation.get_current_loc()
        location_cell_type = observation.get_current_cell_type()
        for i in range(len(adj_positions)):
            self.map.update_position(adj_positions[i], cell_types[i])
        self.map.update_position(location, location_cell_type)

    def update_map_coomunicative(self, observation: CommunicativeObservation):
        """Updates drone's map."""

        # Own observations
        adj_positions = observation.get_adj_locations()
        cell_types = observation.get_adj_cell_types()
        location = observation.get_current_loc()
        location_cell_type = observation.get_current_cell_type()
        for i in range(len(adj_positions)):
            self.map.update_position(adj_positions[i], cell_types[i])
        self.map.update_position(location, location_cell_type)



