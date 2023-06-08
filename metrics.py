from agent import Agent
from grid import Map
import numpy as np

""" Metrics to be used for the analysis of the simulation results. """


def get_avg_distance_needed_to_identify_fertile_land(agents: list[Agent]):
    distances = []
    for agent in agents:
        drone = agent.get_drone()
        if len(drone.distance_needed_to_identify_fertile_land) != 0:
            distances.append(np.mean(drone.distance_needed_to_identify_fertile_land))
    return np.mean(distances)


def get_avg_energy_used_per_planted_tree(agents: list[Agent]):
    distances = []
    for agent in agents:
        drone = agent.get_drone()
        if drone.get_avg_of_drone_energy_used_per_planted_tree() != -1:
            distances.append(drone.get_avg_of_drone_energy_used_per_planted_tree())
    return np.mean(distances)


def get_percentage_of_planted_squares(map: Map):
    return map.number_of_planted_squares() / map.get_initial_number_of_plantable_squares()
