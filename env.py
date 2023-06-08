import numpy as np
from typing import List
from grid import Map


class Environment:
    """Defines the environment for the drones."""
    def __init__(self, printer, map):
        self.timestep = 0
        self.occupied_squares_with_drones = []
        self.map = map
        self.printer = printer
        self.planted_squares = self.map.planted_squares()
        self.rng = np.random.default_rng()
        # self.chargingstations = self.map.charging_stations()

    def get_map(self) -> Map:
        """Returns the map of the environment."""
        return self.map

    def get_planted_squares(self) -> List:
        """Returns the planted squares of the environment."""
        return self.planted_squares

    def render(self, drones) -> None:
        """Renders the environment."""
        self.printer.print(self, drones)

    def step(self, actions: List["Action"], agents: List["Agent"]) -> bool:
        from drone import Action

        """Performs a step in the environment."""

        self.timestep += 1

        # Perform agents actions
        for agent, act in zip(agents, actions):
            drone = agent.get_drone()
            if drone.get_battery_available() != 0:
                if act in (Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT,
                           Action.UP_RIGHT, Action.UP_LEFT, Action.DOWN_RIGHT, Action.DOWN_LEFT):
                    drone.move(act)
                    print("passei")
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

                drone.update_metrics(self.map)

            else:
                drone.set_dead()

        # Return True if all the initial fertile land squares are planted with trees
        return len(self.map.plantable_squares()) == 0
