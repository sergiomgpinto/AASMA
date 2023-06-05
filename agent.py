import abc
import env as env
import numpy as np


class Base(abc.ABC):
    """Base class for all agents."""

    def __init__(self, agent_id) -> None:
        self.last_observation = None
        self._agent_id = agent_id
        self._actions = [
            env.Action.UP,
            env.Action.DOWN,
            env.Action.LEFT,
            env.Action.RIGHT,
            env.Action.UP_RIGHT,
            env.Action.UP_LEFT,
            env.Action.DOWN_RIGHT,
            env.Action.DOWN_LEFT,
            env.Action.STAY,
            env.Action.PLANT,
            env.Action.CHARGE,
        ]

    def see(self, new_observation: env.Observation) -> None:
        """Observes the current state of the environment through its sensores."""
        self.last_observation = new_observation

    @abc.abstractmethod
    def choose_action(self) -> env.Action:
        """Acts based on the last observation and any other information."""
        pass


class Random(Base):
    """Baseline agent that randomly chooses an action at each timestep."""

    def __init__(self, seed: int = None, agent_id: int = 0) -> None:
        super().__init__(agent_id)
        self._rng = np.random.default_rng(seed=seed)

    def choose_action(self) -> env.Action:
        action = self._rng.choice(self._actions)
        return action
