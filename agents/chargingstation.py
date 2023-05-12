from agents.agent import Agent


class ChargingStation(Agent):

    def __init__(self):
        super(Agent, self).__init__("Charging Station Agent")

    def action(self) -> int:
        raise NotImplementedError()
