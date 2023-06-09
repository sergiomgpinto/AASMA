import time
import numpy as np
import pygame
import yaml
from typing import Any
from drone import Drone
from env import Environment
from agent import Agent, RandomAgent, GreedyAgent, CommunicativeAgent
from graphical import EnvironmentPrinter
from metrics import get_percentage_of_planted_squares, get_avg_distance_needed_to_identify_fertile_land, \
    get_avg_energy_used_per_planted_tree
from grid import Map
from default import MAP


def run_graphical(map: Map, agents: list[Agent], drones: list[Drone], timestep: any) -> tuple[int, bool, bool | Any, float | Any, Any, Any]:
    with EnvironmentPrinter(map.get_initial_grid()) as printer:
        environment = Environment(printer, map)

        environment.render(drones)

        running = True
        terminal = False
        all_drones_dead = False
        n_steps = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            for agent in agents:
                agent.see(map)
            actions = [agent.choose_action() for agent in agents]
            terminal = environment.step(actions, agents)
            all_drones_dead = all([drone.is_drone_dead() for drone in drones])

            n_steps += 1
            environment.render(drones)

            # Terminal conditions
            if terminal:
                break
            if all_drones_dead:
                break

            time.sleep(timestep)

    # Metrics
    percentage_of_planted_squares = get_percentage_of_planted_squares(map)
    avg_distance_needed_to_identify_fertile_land = get_avg_distance_needed_to_identify_fertile_land(agents)
    avg_energy_used_per_planted_tree = get_avg_energy_used_per_planted_tree(agents)

    return n_steps, terminal, all_drones_dead, percentage_of_planted_squares, avg_distance_needed_to_identify_fertile_land, avg_energy_used_per_planted_tree


def main():
    with open("./config.yml", "r") as fp:
        data = yaml.safe_load(fp)

    # Parameters from config file
    max_number_of_seeds = data["max_number_of_seeds"]
    max_battery_capacity = data["max_battery_capacity"]
    num_agents = data[data["agent_type"]]["nr_agents"]
    n_runs = data["n_runs"]

    if max_number_of_seeds < 5:
        raise ValueError("Max number of seeds inserted in the config file must be greater than 5 inclusive.")
    if max_battery_capacity <= 1.5 * data["map_size"]:
        raise ValueError("Max battery capacity inserted in the config file must be greater than 1.5 * map_size.")
    if n_runs <= 0:
        raise ValueError("Number of runs inserted in the config file must be greater than 0.")
    timestep = data["timestep"]
    if timestep < 0:
        raise ValueError("Timestep inserted in the config file must be greater than 0 inclusive.")

    # Variables to store metrics
    all_n_steps = []
    number_of_dead_drones = []
    percentage_of_planted_trees = []
    avg_energy_used = []
    avg_distance_needed_to_identify_fertile_land = []
    avg_drone_distance = []

    # Environment map
    map = Map(MAP)

    # Agents
    drones = []
    if data["agent_type"] == "RandomAgent":
        agents = [RandomAgent(i, max_number_of_seeds, max_battery_capacity, map) for i in range(num_agents)]
    elif data["agent_type"] == "GreedyAgent":
        agents = [GreedyAgent(i, max_number_of_seeds, max_battery_capacity, map) for i in range(num_agents)]
    elif data["agent_type"] == "CommunicativeAgent":
        agents = [CommunicativeAgent(i, max_number_of_seeds, max_battery_capacity, map) for i in range(num_agents)]
    else:
        raise Exception("Agent type not recognized")

    # Main loop
    for _ in range(n_runs):

        # Create drones
        for agent in agents:
            if isinstance(agent, CommunicativeAgent):
                agent.set_agents(agents)
            drones.append(agent.get_drone())

        # Run simulation
        n_steps, terminal, all_drones_dead, percentage_of_planted_squares, avg_distance_needed_to_fertile_land, avg_energy_used_per_planted_tree = \
            run_graphical(map, agents, drones, timestep)

        # Metrics
        avg_drone_distance.append(np.mean([drone.total_distance for drone in drones]))
        all_n_steps.append(n_steps)
        number_of_dead_drones.append(len([drone for drone in drones if drone.is_drone_dead]))
        percentage_of_planted_trees.append(percentage_of_planted_squares)
        avg_distance_needed_to_identify_fertile_land.append(avg_distance_needed_to_fertile_land)
        avg_energy_used.append(avg_energy_used_per_planted_tree)

        # Reset environment and agents for next run
        for agent in agents:
            agent.reset()
        map.reset()
        drones = []

        # Terminal conditions for a run
        if all_drones_dead:
            all_drones_dead = False
            continue
        if terminal:
            break

    # Write metrics to file
    with open(f"metrics-{data['agent_type']}-agents-{num_agents}.csv", "w") as metrics:
        metrics.write(
            "Average energy used per planted tree, Average distance to identify fertile land, Percentage of planted squares, Number of drones that died, Drones average distance traveled, Number of steps to complete the map\n")
        for a, b, c, d, e, f in zip(avg_energy_used, avg_distance_needed_to_identify_fertile_land,
                                    percentage_of_planted_trees,
                                    number_of_dead_drones, avg_drone_distance, all_n_steps):
            metrics.write(f"{a}, {b}, {c}, {d}, {e}, {f}\n")


# Run main
if __name__ == "__main__":
    main()
