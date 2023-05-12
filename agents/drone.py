from agents.agent import Agent


class Drone(Agent):

    def __init__(self):
        super(Agent, self).__init__("Drone Agent")

    def action(self) -> int:
        raise NotImplementedError()
