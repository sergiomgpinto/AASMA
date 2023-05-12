from abc import ABC, abstractmethod
import numpy as np


class Agent(ABC):

    def __init__(self, name: str):
        self.name = name
        self.observation = None
        self.internal_state = None

    def see(self, observation: np.ndarray):
        self.observation = observation

    @abstractmethod
    def action(self) -> int:
        raise NotImplementedError()
