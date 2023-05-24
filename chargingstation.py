import dataclasses
import grid


@dataclasses.dataclass
class ChargingStation:

    loc: grid.Position 
    capacity: int = 1
    nr_charging_drones: int = 0
    pos: grid.Position = None

    @property
    def get_position(self):
        return self.pos

    @property
    def get_capacity(self):
        return self.capacity

    @property
    def has_enough_capacity(self):
        if self.nr_charging_drones < self.capacity:
            return True
        else:
            return False
