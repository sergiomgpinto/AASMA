import numpy as np
from agent import CommunicativeAgent
from grid import Map


class Environment:
    """Defines the environment for the drones."""
    def __init__(self, printer, map):
        self.timestep = 0
        self.occupied_squares_with_drones = []
        self.map = map
        self.printer = printer
        self.rng = np.random.default_rng()

    def get_map(self) -> Map:
        """Returns the map of the environment."""
        return self.map

    def render(self, drones) -> None:
        """Renders the environment."""
        self.printer.print(self, drones)

    def get_timestep(self) -> int:
        """Returns the current timestep."""
        return self.timestep

    def step(self, actions, agents) -> bool:
        from drone import Action

        """Performs a step in the environment."""

        # Garantees that the charging station only has one drone charging at
        # each timestep. Only valid for Random and Greedy agents.
        # Since for the Communicative agent they communicate with each other.
        CHARGING_STATION_FULL = False

        # Perform agents actions
        for agent, act in zip(agents, actions):
            drone = agent.get_drone()
            if drone.get_battery_available() != 0: # Unless the drone has energy, it cant do actions.
                if act in (Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT,
                           Action.UP_RIGHT, Action.UP_LEFT, Action.DOWN_RIGHT, Action.DOWN_LEFT):
                    # Enters if a moving action was chosen.
                    drone.move(act)

                elif act == Action.PLANT:
                    p = drone.get_loc()
                    planted_with_sucess, s = drone.plant(self.map)
                    if planted_with_sucess:
                        self.map.change_cell_type(p, s)
                        self.map.add_planted_square(p, s)
                        drone.get_map().add_planted_square(p, s)

                elif act == Action.CHARGE:
                    if not isinstance(agent, CommunicativeAgent):
                        if CHARGING_STATION_FULL:
                            continue
                        drone.charge()
                        CHARGING_STATION_FULL = True
                    else:
                        # Cooperative charging strategy.
                        agent_id_with_the_highest_priority = agent.get_cooperative_charging_strategy().run(agent, self.timestep)
                        if agent_id_with_the_highest_priority == agent.get_id():
                            drone.charge()
                        else:
                            continue
                elif act == Action.STAY:
                    pass

                drone.update_metrics(self.map)

            else:
                drone.set_dead()
        self.timestep += 1

        # Return True if all the initial fertile land squares are planted with trees
        return len(self.map.plantable_squares()) == 0
