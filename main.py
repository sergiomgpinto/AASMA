import agent
import env
import grid
import default
import graphical
import numpy as np
import pygame
import yaml
import tqdm

import time

from typing import List


def run_graphical(map: grid.Map, agents: List[agent.Base], log_level: str, max_number_of_seeds: int,
                  max_battery_capacity: int):
    with graphical.EnvironmentPrinter(map.initial_grid) as printer:
        map.reset()
        environment = env.Environment(map=map, init_drones=len(agents), printer=printer, log_level=log_level)
        observations = environment.reset(max_number_of_seeds, max_battery_capacity)
        environment.render()
        running = True
        n_steps = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            for observations, agent in zip(observations, agents):
                agent.see(observations)

            actions = [a.choose_action() for a in agents]
            observations, terminal, all_drones_dead = environment.step(actions)

            n_steps += 1
            environment.render()
            if terminal:
                break
            if all_drones_dead:
                break

            time.sleep(0.25)
        percentage_of_planted_squares = map.number_of_planted_squares() / map.initial_number_of_plantable_squares
        avg_distance_needed_to_identify_fertile_land = environment.get_avg_distance_needed_to_identify_fertile_land()
        avg_energy_used_per_planted_tree = environment.get_avg_energy_used_per_planted_tree()

    return environment.drones, n_steps, terminal, all_drones_dead, percentage_of_planted_squares, \
           avg_distance_needed_to_identify_fertile_land, avg_energy_used_per_planted_tree


def main():
    with open("./config.yml", "r") as fp:
        data = yaml.safe_load(fp)

    drones_distances = []
    all_n_steps = []
    number_of_dead_drones = []
    percentage_of_planted_trees = []
    num_charging_stations = data[data["agent_type"]]["nr_charging_stations"]
    max_number_of_seeds = data["max_number_of_seeds"]
    max_battery_capacity = data["max_battery_capacity"]
    num_agents = data[data["agent_type"]]["nr_agents"]
    map = grid.Map(default.MAP)
    run_with_graphics = data["graphical"]
    log_level = data["log_level"]
    n_runs = data["n_runs"]
    all_drones_dead = False
    terminal = False
    n_steps = 0
    percentage_of_planted_squares = 0.0
    percentage_of_planted_trees = []
    agents = []
    drones = []
    avg_distance_needed_to_identify_fertile_land = []
    avg_distance_needed_to_fertile_land = 0
    avg_energy_used_per_planted_tree = 0
    avg_energy_used = []

    if data["agent_type"] == "Random":
        agents = [agent.Random(agent_id=i) for i in range(num_agents)]

    if run_with_graphics:
        iterable = range(n_runs)
    else:
        iterable = tqdm.tqdm(range(n_runs))

    for _ in iterable:
        if run_with_graphics:
            drones, n_steps, terminal, all_drones_dead, percentage_of_planted_squares, \
            avg_distance_needed_to_fertile_land, avg_energy_used_per_planted_tree = \
                run_graphical(map, agents, log_level, max_number_of_seeds, max_battery_capacity)

        avg_drone_distance = np.mean([drone.total_distance for drone in drones])
        drones_distances.append(avg_drone_distance)
        all_n_steps.append(n_steps)
        number_of_dead_drones.append(len([drone for drone in drones if drone.is_dead]))
        percentage_of_planted_trees.append(percentage_of_planted_squares)
        avg_distance_needed_to_identify_fertile_land.append(avg_distance_needed_to_fertile_land)
        avg_energy_used.append(avg_energy_used_per_planted_tree)

        if all_drones_dead:
            all_drones_dead = False
            continue
        if terminal:
            break

    with open(f"metrics-{data['agent_type']}-agents-{num_agents}.csv", "w") as metrics:
        metrics.write(
            "Average distance to identify fertile land, Percentage of planted squares, Number of drones that died, Drones average distance traveled, Number of steps to complete the map\n")
        for a, b, c, d, e in zip(avg_distance_needed_to_identify_fertile_land, percentage_of_planted_trees,
                                 number_of_dead_drones, drones_distances, all_n_steps):
            metrics.write(f"{a}, {b}, {c}, {d}, {e}\n")


if __name__ == "__main__":
    main()

'''
def run_not_graphical(map: grid.Map, agents: List[agent.Base], log_level: str):
    environment = env.Environment(map=map, init_drones=len(agents), log_level=log_level)

    observations = environment.reset()
    running = True
    n_steps = 0
    while running:
        for observations, agent in zip(observations, agents):
            agent.see(observations)

        actions = [a.choose_action() for a in agents]
        observations, terminal = environment.step(*actions)
        n_steps += 1
        if terminal:
            break
    # TODO: metricas
    return environment.drones, n_steps, terminal
'''
