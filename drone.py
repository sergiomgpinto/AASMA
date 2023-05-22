import dataclasses
import enum
import grid as grid
import chargingstation as chargingstation
from dataclasses import field


class Direction(enum.Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    def __repr__(self) -> str:
        return f"Direction({self.name})"


class Goal(enum.Enum):
    PLANT = 1
    CHARGE = 2
    WAIT = 3

    def __repr__(self) -> str:
        return f"Goal({self.name})"


@dataclasses.dataclass
class Drone:
    loc: grid.Position
    map: grid.Map
    direction: Direction

    # Id for agent identification
    id: int = 0

    nr_seeds: list = field(default_factory=lambda: [100, 100, 100])
    # nr_seeds: List[int] = [0,0,0] # number of seeds [OAK_TREE,PINE_TREE,EUCALYPTUS] that the drone is currently transporting
    seed_maxcapacity: list = field(default_factory=lambda: [100, 100, 100])
    batery_available: int = 0
    batery_maxcapacity: int = 100
    goal: Goal = Goal.CHARGE  # iniciam todos com o objetivo de carregar

    # Drone Metrics
    total_distance: int = 0

    # total_energy: int = 0, se para cada quadrado percorrido gastamos 1 de energia n precisamos disto

    def charge(self): # , chargingStation: chargingstation.ChargingStation
        """
        Charges batery. Will only have effect if drone is positioned in charging station and if the charging station 
        isn't full.
        """
        if (self.map.find_charging_station() == self.loc):
            #if chargingStation.has_enough_capacity:
            #if self.batery_available < self.batery_maxcapacity:
            self.batery_available = self.batery_maxcapacity
            self.nr_seeds = self.seed_maxcapacity
            self.goal = Goal.PLANT
            #else:
                #self.goal = Goal.WAIT

        return None

    def plant(self):
        """
        Drone plants fertile land where he is located.
        """
        '''
        closest_fertile_land = self.map.choose_adj_fertile_land(self.loc)
        chosen_seed = self.map.choose_seed(closest_fertile_land)
        print("SEEDS",self.nr_seeds[int(chosen_seed)])
        if self.nr_seeds[int(chosen_seed)] != 0:

            plant = self.map.choose_adj_fertile_land(self.loc)


        else:
            # TODO: Communication Sergio, se o drone não tiver a seed necessária
            pass
        '''

        # Pensar o que é que tem de vir para aqui ??
        # acho que o objetivo é só atualizar os argumentos pq a logica tá no agent 
        if ( self.loc == grid.Cell.FERTILE_LAND ):
            # menos uma seed
            nr_seeds[0] -= 1
        else:
            pass
        return None
