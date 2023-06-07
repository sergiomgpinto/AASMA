import numpy as np
from grid import Position


class Payload:
    pass


class MapUpdatePayload(Payload):
    def __init__(self, adj_postions: np.array, adj_cell_types: np.array):
        self.adj_positions = adj_postions
        self.adj_cell_types = adj_cell_types

    def get_adj_positions(self):
        return self.adj_positions

    def get_adj_cell_types(self):
        return self.adj_cell_types


class EnergyAndSeedLevelsStatusPayload(Payload):

    def __init__(self, energy_level: int, seed_level: list):
        self.energy_level = energy_level
        self.seed_level = seed_level

    def get_energy_level(self):
        return self.energy_level

    def get_seed_level(self):
        return self.seed_level


class ChargingStatusPayload(Payload):

    def __init__(self, charging__agent_id: int):
        self.charging_agent_id = charging__agent_id

    def get_charging_agent_id(self):
        return self.charging_agent_id


class DronePlantingPayload(Payload):

    def __init__(self, planting_location: Position):
        self.planting_location = planting_location

    def get_planting_location(self):
        return self.planting_location


class Message:
    def __init__(self, sender_id: int, receiver_id: int, payload: Payload):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.payload = payload

    def get_sender(self) -> int:
        return self.sender_id

    def get_receiver(self) -> int:
        return self.receiver_id

    def get_payload(self) -> any:
        return self.payload


class MapUpdateMessage(Message):
    def __init__(self, sender_id: int, receiver_id: int, payload: MapUpdatePayload):
        super().__init__(sender_id, receiver_id, payload)


class EnergyAndSeedLevelsStatusMessage(Message):
    def __init__(self, sender_id: int, receiver_id: int, status: EnergyAndSeedLevelsStatusPayload):
        super().__init__(sender_id, receiver_id, status)


class ChargingStatusMessage(Message):
    def __init__(self, sender_id: int, receiver_id: int, status: ChargingStatusPayload):
        super().__init__(sender_id, receiver_id, status)


class DronePlantingMessage(Message):
    def __init__(self, sender_id: int, receiver_id: int, payload: DronePlantingPayload):
        super().__init__(sender_id, receiver_id, payload)


class Communication:
    def __init__(self, sender_id: int, agents: list):
        self.sender_id = sender_id
        self.agents = agents

    def send_map_update(self, payload: MapUpdatePayload):
        for agent in self.agents:
            if agent.get_id() != self.sender_id:
                message = MapUpdateMessage(self.sender_id, agent.get_id(), payload)
                agent.receive_message(message)

    def send_energy_and_seed_levels_status(self, payload: EnergyAndSeedLevelsStatusPayload):
        for agent in self.agents:
            if agent.get_id() != self.sender_id:
                message = EnergyAndSeedLevelsStatusMessage(self.sender_id, agent.get_id(), payload)
                agent.receive_message(message)

    def send_charging_status(self, payload: ChargingStatusPayload):
        for agent in self.agents:
            if agent.get_id() != self.sender_id:
                message = ChargingStatusMessage(self.sender_id, agent.get_id(), payload)
                agent.receive_message(message)

    def send_drone_planting(self, payload: DronePlantingPayload):
        for agent in self.agents:
            if agent.get_id() != self.sender_id:
                message = DronePlantingMessage(self.sender_id, agent.get_id(), payload)
                agent.receive_message(message)
