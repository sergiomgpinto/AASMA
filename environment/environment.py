import abc
import dataclasses
import enum
import grid
import entity
import log
import numpy as np

from typing import List, Optional


@dataclasses.dataclass(frozen=True)
class Observation:
    """Defines the observation for a given agent.
    
    Attributes:
        loc: position of the agent drone in the grid.
        has_seeds: whether the agent drone has a seeds or not. (???)
        energy_levels: how much energy the drone has.
        drones_pos: positions of all the drones in the grid.
    """

    map: grid.Map
    drones: List[entity.Drone]


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

class Environment:

    drones: List[entity.Drone]
    # final_passengers: List[List[int]] necessário ter final list of plantable squares???

    def __init__(
        self,
        map: grid.Map,
        init_drones: int,
        printer: "Optional[Printer]" = None,
        log_level: Optional[str] = "info",
        max_timesteps: Optional[int] = 150,
        seed: Optional[int] = None,
    ):
        self.map = map
        self._rng = np.random.default_rng(seed=seed)
        self._printer = printer

        self._logger = log.new(__name__, lvl=log_level)
        self._init_drones = init_drones
        self._max_timesteps = max_timesteps

    def reset(self) -> List[Observation]:
        self._reset()
        observation = Observation(map=self.map, drones=self.drones)
        return [observation for _ in range(len(self.drones))]

    def step(self, *actions: Action) -> List[Observation]:
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
        for drone, act in zip(self.drones, actions):
            if act in (Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT):
                self._move_drone(drone, act)
                drone.total_distance += 1

            elif act == Action.PLANT:
                drone.pickup_up(self.passengers, self.map)
            elif act == Action.CHARGE:
                drone.drop_off(self.map)
            elif act == Action.STAY:
                # Do nothing
                pass
            else:
                raise ValueError(f"Unknown action: {act}")            
            log.taxi(self._logger,self._timestep, taxi)


        for passenger in self.passengers:
            log.passenger(self._logger, self._timestep, passenger)
            
            if passenger.in_trip == entity.TripState.WAITING:
                passenger.pick_up_time += 1
            elif passenger.in_trip == entity.TripState.INTRIP:
                passenger.travel_time += 1

        self._delete_passengers()
        observation = Observation(map=self.map, taxis=self.taxis, passengers=self.passengers)

        self.terminal = len(self.passengers) == 0 or self._timestep == self._max_timesteps
        # In the end, add the passengers that are not yet delivered to the list of final passengers
        # for metrics.
        if self.terminal:
            self.final_passengers += [[p.pick_up_time, p.travel_time] for p in self.passengers]

        return [observation for _ in range(len(actions))], self.terminal
            
    def render(self):
        if not self._printer:
            raise ValueError("Unable to render without printer")
        self._printer.print(self)

    def _reset(self):
        self._timestep = 0
        self.terminal = False

        self.drones = []
        #self.final_passengers = []

        for i in range(self.init_drones):
            self.drones.append(self._create_drone(i))

        '''
        self.passengers = []
        for i in range(self._init_passengers):
            self.passengers.append(self._create_passenger(i))

        self.passengers_travelling = [i for i in range(len(self.passengers))] 
        '''

    def _create_drone(self, id: int) -> entity.Drone:
        """Creates a drone with a random location and direction.
        
        The drone initial location will not overlap with another drone."""

        occupied_locations = set()
        for d in self.drones:
            occupied_locations.add(d.loc)

        possible_drone_locations = [
            l
            for l in self.map.possible_drone_positions
            if l not in occupied_locations
        ]
    
        if len(possible_drone_locations) == 0:
            raise ValueError("Unable to create taxi: Not enough free locations.")
        loc = self._rng.choice(possible_drone_locations)
        possible_taxi_directions = [
            entity.Direction.UP, 
            entity.Direction.DOWN, 
            entity.Direction.LEFT, 
            entity.Direction.RIGHT,
        ]
        direction = self._rng.choice(possible_taxi_directions)
        taxi = entity.Taxi(loc=loc, direction=direction, id=id)
        log.create_taxi(self._logger, self._timestep, taxi)
        return taxi

    def _move_drone(self, taxi: entity.Drone, action: Action):
        """Move a drone according to an action."""
        if action == Action.UP:
            target_loc = drone.loc.up
            target_dir = entity.Direction.UP
        elif action == Action.DOWN:
            target_loc = drone.loc.down
            target_dir = entity.Direction.DOWN
        elif action == Action.RIGHT:
            target_loc = drone.loc.right
            target_dir = entity.Direction.RIGHT
        elif action == Action.LEFT:
            target_loc = drone.loc.left
            target_dir = entity.Direction.LEFT
        else:
            raise ValueError(f"Unknown direction in taxi movement {self.direction}")
        
        drone.loc = target_loc
        drone.direction = target_dir

    '''
    def _create_passenger(self, id: int):
        """Creates a passenger with random Pick-Up and Drop-Off locations.
        
        Both the passenger locations will not overlap with other passsenger
        locations.
        """

        occupied_locations = set()
        for p in self.passengers:
            occupied_locations.add(p.pick_up)
            occupied_locations.add(p.drop_off)

        possible_passenger_locations = [
            p 
            for p in self.map.possible_passenger_positions 
            if p not in occupied_locations
        ]

        
        if len(possible_passenger_locations) < 2:
            raise ValueError("Unable to create passenger: Not enough free locations.")
        pick_up_loc = self._rng.choice(possible_passenger_locations)
        possible_passenger_locations.remove(pick_up_loc)
        drop_off_loc = self._rng.choice(possible_passenger_locations)
        passenger = entity.Passenger(pick_up=pick_up_loc, drop_off=drop_off_loc, id=id)
        log.create_passenger(self._logger, self._timestep, passenger)
        return passenger


    def _delete_passengers(self):
        """
        Evaluates which passengers are in the corresponding drop-off locations.
        Deletes these passengers after one time-step.
        """

        self.passengers = [self.passengers[i] for i in self.passengers_travelling]

        self.passengers_travelling = []
        for i in range(len(self.passengers)):
            if self.passengers[i].pick_up != self.passengers[i].drop_off:
                self.passengers_travelling.append(i)
            else:
                self.final_passengers += [[self.passengers[i].pick_up_time, self.passengers[i].travel_time]]
    '''

class Printer(abc.ABC):
    @abc.abstractmethod
    def print(self, env: Environment):
        pass