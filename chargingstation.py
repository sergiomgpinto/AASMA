import dataclasses
import grid


@dataclasses.dataclass
class ChargingStation:

    loc: grid.Position 
    capacity: int = 1
    nr_charging_drones: int = 0 

    def get_charging_station_pos(self):
        return self.pos

    def get_capacity(self):
        return self.capacity

    def get_pos(self):
        return self.pos

    @property
    def has_enough_capacity(self):
        if self.nr_charging_drones < self.capacity:
            return True
        else:
            return False

    def stop_charging(self):
        self.nr_charging_drones -= 1

    def start_charging(self):
        self.nr_charging_drones += 1

    def action(self) -> int:
        raise NotImplementedError()
