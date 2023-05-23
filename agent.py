import abc
import drone 
import chargingstation
import env as env
import grid
import numpy as np

from typing import List

class Base(abc.ABC):
    """Base class for all agents."""

    _last_observation: env.Observation
    
    def see(self, obs: env.Observation) -> None:
        """Observes the current state of the environment through its sensores."""
        self._last_observation = obs

    @abc.abstractmethod
    def act(self) -> env.Action:
        """Acts based on the last observation and any other information."""
        pass

class Random(Base):
    """Baseline agent that randomly chooses an action at each timestep."""

    def __init__(self, seed: int = None) -> None:
        self._rng = np.random.default_rng(seed=seed)
        self._actions = [
            env.Action.UP,
            env.Action.DOWN,
            env.Action.LEFT,
            env.Action.RIGHT,
            env.Action.STAY,
            env.Action.PLANT,
            env.Action.CHARGE,
        ]

    def act(self) -> env.Action:
        return self._rng.choice(self._actions)

class EnergyBased(Base):
    """Utility class with path based functions."""

    def _has_enough_energy(self, agent_drone: drone.Drone, target: grid.Position) -> bool:
        """
        Checks that there is enough energy to go to nearest plantable square and head back to charging station,
        considering the drone's current position, the target and the target's distance to the charging station.
        
        """
        return len(self._bfs_with_positions(agent_drone.map,agent_drone.loc,target)) + len(self._bfs_with_positions(agent_drone.map,target,agent_drone.map.
        find_charging_station())) > agent_drone.batery_available


class PathBased(EnergyBased):
    """Utility class with path based functions."""

    def _plant_nearest_square(self, agent_drone: drone.Drone) -> env.Action:
        plantable_pos = agent_drone.map.plantable_squares()
        print('plantable_pos',plantable_pos)
        if len(plantable_pos) == 0:
            return env.Action.STAY

        shortest_paths = [
            self._bfs_with_positions(agent_drone.map, agent_drone.loc, p) 
            for p in plantable_pos
        ]
        path_idx = np.argmin([len(p) for p in shortest_paths])

        if self._has_enough_energy(agent_drone,plantable_pos[path_idx]):
            action = self._move_in_path_and_act(shortest_paths[path_idx], env.Action.PLANT)
            print('ACTION',action)
            return action
        else:
            return self._go_to_charging_station(agent_drone)
    
    
    def _go_to_charging_station(self, agent_drone: drone.Drone) -> env.Action:
        
        charging_station_pos = agent_drone.map.find_charging_station(agent_drone.map)
        shortest_path = self._bfs_with_positions(agent_drone.map, agent_drone.loc, charging_station_pos)
        return self._move_in_path_and_act(shortest_path, env.Action.CHARGE)


    def _move_in_path_and_act(self, path: List[grid.Position], last_action: env.Action) -> env.Action:
        if len(path) == 1:
            print('path 1')
            return last_action
        curr_pos = path[0]
        next_pos = path[1]
        print('not path 1')
        if next_pos == curr_pos.up:
            return env.Action.UP
        elif next_pos == curr_pos.down:
            return env.Action.DOWN
        elif next_pos == curr_pos.left:
            return env.Action.LEFT
        elif next_pos == curr_pos.right:
            return env.Action.RIGHT
        else:
            raise ValueError(
                f"Unknown adj direction: (curr_pos: {curr_pos}, next_pos: {next_pos})"
            )

    def _bfs_with_positions(
        self, map: grid.Map, source: grid.Position, target: grid.Position,
    ) -> List[grid.Position]:
        """Computes the list of positions in the path from source to target.
        
        It uses a BFS so the path is the shortest path."""
        
        # The queue stores tuple with the nodes to explore
        # and the path taken to the node.
        queue = [(source, (source,))]
        # Visited stores already explored positions to avoid
        # loops.
        visited = set()
        while len(queue) > 0:
            curr, curr_path = queue.pop(0)
            if curr in target.adj:
                return list(curr_path)
            for neighbour in curr.adj:
                if neighbour not in visited:
                    neighbour_path = curr_path + (neighbour,)
                    queue.append((neighbour, neighbour_path))
                    visited.add(neighbour)
        raise ValueError("No path found")


class PathPlanner(PathBased):
    """Agent that plans its path using a BFS."""

    def __init__(self, agent_id: int = 0) -> None:
        super().__init__()
        self._agent_id = agent_id

    def act(self) -> env.Action:
        agent_drone = self._last_observation.drones[self._agent_id]
        
        # Conditions in which the drone needs to go to charging station ???
        # deviamos adicionar uma função reutilizavel para isto 
        if agent_drone.nr_seeds.count(0) == 3 or len(self._bfs_with_positions(agent_drone.map,agent_drone.loc,agent_drone.map.
        find_charging_station())) == agent_drone.batery_available :
            print("go to charging station")
            return self._go_to_charging_station(agent_drone)
        else:
            print("go plant")
            self._plant_nearest_square(agent_drone)
            p = agent_drone.loc
            s = env.map.choose_seed(agent_drone.loc)
            print("pos",p)
            print("cell type before",self.map.grid[p.y, p.x])
            env.map.change_cell_type(p,s)
            print("cell type after:",self.map.grid[p.y, p.x])
            print('change cell type to',s)
            env.planted_squares.append(tuple([p,s]))
            
    
'''
class QuadrantsSocialConventions(PathBased):
    """Agent that uses social conventions to attribute passengers.
    
    Each agent picks up from a quadrant, as follows:
    |-------------------|-------------------|
    | agent (0, 4, ...) | agent (1, 5, ...) |
    |-------------------|-------------------|
    | agent (2, 6, ...) | agent (3, 7, ...) |
    |-------------------|-------------------|
    """

    def __init__(self, agent_id: int = 0) -> None:
        super().__init__()
        self._agent_id = agent_id
        self._quadrant = (agent_id % 4) + 1

    def act(self) -> env.Action:
        map = self._last_observation.map
        agent_taxi = self._last_observation.taxis[self._agent_id]
        passengers = self._last_observation.passengers
        
        if agent_taxi.has_passenger is None:
            check_quadrant_mapper = {
                1: self._is_first_quadrant,
                2: self._is_second_quadrant,
                3: self._is_third_quadrant,
                4: self._is_fourth_quadrant,
            }
            check_quadrant_fn = check_quadrant_mapper[self._quadrant]
            passengers = [
                p for p in passengers
                if check_quadrant_fn(map, p.pick_up) and p.in_trip == entity.TripState.WAITING
            ]
            return self._plant_nearest_square(map, agent_taxi, passengers)
        return self._dropoff_current_passenger(map, agent_taxi)

    def _is_first_quadrant(self, map: grid.Map, pos: grid.Position):
        return pos.x < map.width // 2 and pos.y < map.height // 2

    def _is_second_quadrant(self, map: grid.Map, pos: grid.Position):
        return pos.x >= map.width // 2 and pos.y < map.height // 2

    def _is_third_quadrant(self, map: grid.Map, pos: grid.Position):
        return pos.x < map.width // 2 and pos.y >= map.height // 2

    def _is_fourth_quadrant(self, map: grid.Map, pos: grid.Position):
        return pos.x >= map.width // 2 and pos.y >= map.height // 2


class IDsSocialConventions(PathBased):
    """Agent that uses social conventions to attribute passengers by using their ID.
    
    Each agent picks up a passenger as follows:
    
    """

    def __init__(self, agent_id: int = 0) -> None:
        super().__init__()
        self._agent_id = agent_id

    def act(self) -> env.Action:
        map = self._last_observation.map
        agent_taxi = self._last_observation.taxis[self._agent_id]
        nr_agents = len(self._last_observation.taxis)
        passengers = self._last_observation.passengers
        
        if agent_taxi.has_passenger is None:
            
            passengers = [
                p for p in passengers
                if (p.id % nr_agents) == self._agent_id and p.in_trip == entity.TripState.WAITING
            ]
            return self._plant_nearest_square(map, agent_taxi, passengers)
        return self._dropoff_current_passenger(map, agent_taxi)


class Roles(PathBased):
    """Agent that attributes passengers based on distance to pick up location."""

    def __init__(self, agent_id: int = 0) -> None:
        super().__init__()
        self._agent_id = agent_id

    def act(self) -> env.Action:
        map = self._last_observation.map
        taxis = self._last_observation.taxis
        passengers = self._last_observation.passengers

        roles = []

        # First assign passengers already in trip to their taxis.
        for t in taxis:
            if t.has_passenger is not None:
                roles.append((t, t.has_passenger))
            
        possible_passengers = [p for p in passengers if p.in_trip == entity.TripState.WAITING]
        possible_taxis = [t for t in taxis if t.has_passenger is None]
        assigned_taxis = []
        for p in possible_passengers:
            shortest_paths = [
                self._bfs_with_positions(map, t.loc, p.pick_up)
                for t in possible_taxis
            ]
            taxi = None
            min_dist = np.inf
            for t, path in zip(possible_taxis, shortest_paths):
                if len(path) < min_dist and t not in assigned_taxis:
                    min_dist = len(path)
                    taxi = t
            assigned_taxis.append(taxi)
            roles.append((taxi, p))

        agent_taxi = taxis[self._agent_id]
        for t, p in roles:
            if t == agent_taxi:
                if agent_taxi.has_passenger:
                    return self._dropoff_current_passenger(map, agent_taxi)
                shortest_path = self._bfs_with_positions(map, agent_taxi.loc, p.pick_up)
                return self._move_in_path_and_act(shortest_path, env.Action.PICK_UP)
        return env.Action.STAY    
'''

class Debug(Base):
    """Debug agent that prompts the user for the next action."""

    def __init__(self, agent_id: int = 0) -> None:
        self._prompt = f"Choose agent {agent_id} action [W(Up),S(Down),A(Left),D(Right),Z(Stay),X(Plant),C(Charge)]?"

    def act(self) -> env.Action:
        action = None
        while action is None:
            # Lower to ignore uppercase letters
            action_input = input(self._prompt).lower()
            if action_input in ("w", "up"):
                action = env.Action.UP
            elif action_input in ("s", "down"):
                action = env.Action.DOWN
            elif action_input in ("a", "left"):
                action = env.Action.LEFT
            elif action_input in ("d", "right"):
                action = env.Action.RIGHT
            elif action_input in ("z", "stay"):
                action = env.Action.STAY
            elif action_input in ("x", "plant"):
                action = env.Action.PLANT
            elif action_input in ("c", "charge"):
                action = env.Action.CHARGE

        return action