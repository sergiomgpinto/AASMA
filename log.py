import env
import agent
import logging

logging.basicConfig(format="t = %(timestep)s \t %(levelname)s \t %(name)s \t %(message)s")

def new(name: str, lvl: str = "info") -> logging.Logger:
    logger = logging.getLogger(name=name)
    lvl = getattr(logging, lvl.upper(), None)
    if not isinstance(lvl, int):
        raise ValueError(f"Invalid log level: {lvl}")
    logger.setLevel(lvl)
    return logger

def create_drone(logger: logging.Logger, t: int, drone: agent.Drone):
    logger.info("Created %r", drone, extra={"timestep": t})

def choosen_action(logger: logging.Logger, t: int, agent: int, action: "env.Action"):
    logger.info("Agent %d wants to %r", agent, action, extra={"timestep": t})

def drone(logger: logging.Logger, t: int, drone: agent.Drone):
    logger.info("Drone %r", drone, extra={"timestep": t})
