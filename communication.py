import numpy as np
from grid import Position


class Payload:
    """ Base class for all payloads."""
    pass


class MapUpdatePayload(Payload):
    """ Payload for updating the map."""
    def __init__(self, adj_postions: np.array, adj_cell_types: np.array):
        self.adj_positions = adj_postions
        self.adj_cell_types = adj_cell_types

    def get_adj_positions(self):
        """ Returns the adjacent positions."""
        return self.adj_positions

    def get_adj_cell_types(self):
        """ Returns the adjacent cell types."""
        return self.adj_cell_types


class EnergyAndSeedLevelsStatusPayload(Payload):
    """ Payload for energy and seed levels status."""
    def __init__(self, energy_level: int, seed_level: list):
        self.energy_level = energy_level
        self.seed_level = seed_level

    def get_energy_level(self):
        """ Returns the energy level."""
        return self.energy_level

    def get_seed_level(self):
        """ Returns the seed level."""
        return self.seed_level


class ChargingStatusPayload(Payload):
    """ Payload for charging status."""
    def __init__(self, charging__agent_id: int):
        self.charging_agent_id = charging__agent_id

    def get_charging_agent_id(self):
        """ Returns the charging agent id."""
        return self.charging_agent_id


class DronePlantingPayload(Payload):
    """ Payload for drone planting."""
    def __init__(self, planting_location: Position):
        self.planting_location = planting_location

    def get_planting_location(self):
        """ Returns the planting location."""
        return self.planting_location


class Message:
    """ Base class for all messages."""
    def __init__(self, sender_id: int, receiver_id: int, payload: Payload):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.payload = payload

    def get_sender(self) -> int:
        """ Returns the sender id."""
        return self.sender_id

    def get_receiver(self) -> int:
        """ Returns the receiver id."""
        return self.receiver_id

    def get_payload(self) -> any:
        """ Returns the payload."""
        return self.payload


class MapUpdateMessage(Message):
    """ Message for updating the map."""
    def __init__(self, sender_id: int, receiver_id: int, payload: MapUpdatePayload):
        super().__init__(sender_id, receiver_id, payload)


class EnergyAndSeedLevelsStatusMessage(Message):
    """ Message for energy and seed levels status."""
    def __init__(self, sender_id: int, receiver_id: int, status: EnergyAndSeedLevelsStatusPayload):
        super().__init__(sender_id, receiver_id, status)


class ChargingStatusMessage(Message):
    """ Message for charging status."""
    def __init__(self, sender_id: int, receiver_id: int, status: ChargingStatusPayload):
        super().__init__(sender_id, receiver_id, status)


class DronePlantingMessage(Message):
    """ Message for drone planting."""
    def __init__(self, sender_id: int, receiver_id: int, payload: DronePlantingPayload):
        super().__init__(sender_id, receiver_id, payload)


class Communication:
    """ Class for communication between agents."""
    def __init__(self, sender_id: int, agents: list):
        self.sender_id = sender_id
        self.agents = agents

    def send_map_update(self, payload: MapUpdatePayload):
        """ Sends a map update message to all agents except the sender."""
        for agent in self.agents:
            if agent.get_id() != self.sender_id:
                message = MapUpdateMessage(self.sender_id, agent.get_id(), payload)
                agent.receive_message(message)

    def send_energy_and_seed_levels_status(self, payload: EnergyAndSeedLevelsStatusPayload):
        """ Sends an energy and seed levels status message to all agents except the sender."""
        for agent in self.agents:
            if agent.get_id() != self.sender_id:
                message = EnergyAndSeedLevelsStatusMessage(self.sender_id, agent.get_id(), payload)
                agent.receive_message(message)

    def send_charging_status(self, payload: ChargingStatusPayload):
        """ Sends a charging status message to all agents except the sender."""
        for agent in self.agents:
            if agent.get_id() != self.sender_id:
                message = ChargingStatusMessage(self.sender_id, agent.get_id(), payload)
                agent.receive_message(message)

    def send_drone_planting(self, payload: DronePlantingPayload):
        """ Sends a drone planting message to all agents except the sender."""
        for agent in self.agents:
            if agent.get_id() != self.sender_id:
                message = DronePlantingMessage(self.sender_id, agent.get_id(), payload)
                agent.receive_message(message)
