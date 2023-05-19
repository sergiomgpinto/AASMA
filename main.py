from agents import agent
from environment import env, grid
from visualize import default, graphical

import numpy as np
import pygame
import yaml
import tqdm


from typing import List


def run_graphical(map: grid.Map, agents: List[agent.Base], log_level: str):
    with graphical.EnvironmentPrinter(map.grid) as printer:
        environment = env.Environment(
            map=map, init_drones=len(agents), printer=printer, log_level=log_level,
        )
        # Initial render to see initial environment.
        observations = environment.reset()
        environment.render()
        running = True
        n_steps = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            for observations, agent in zip(observations, agents):
                agent.see(observations)

            actions = [a.act() for a in agents]
            observations, terminal = environment.step(*actions)
            n_steps += 1
            environment.render()
            if terminal:
                break

            #time.sleep(1)
    # TODO: util para as metricas 
    #squares_planted = len(environment.final_passengers) - len(environment.passengers)
    return environment.drones, n_steps #, environment.final_passengers, squares_planted, n_steps


def run_not_graphical(map: grid.Map, agents: List[agent.Base], log_level: str):
    environment = env.Environment(
        map=map, init_drones=len(agents), log_level=log_level)

    observations = environment.reset()
    running = True
    n_steps = 0
    while running:
        
        for observations, agent in zip(observations, agents):
            agent.see(observations)
        
        actions = [a.act() for a in agents]
        observations, terminal = environment.step(*actions)
        n_steps += 1
        if terminal:
            break
        #time.sleep(1)
    #TODO: metricas
    #n_delivered = len(environment.map.) - len(environment.passengers)
    return environment.drones, n_steps #,n_delivered

def main():


    with open("./config.yml", "r") as fp:
        data = yaml.safe_load(fp)

    num_agents = data[data["agent_type"]]["nr_agents"]
    #init_passengers = data[data["agent_type"]]["nr_passengers"]
    
    if data["agent_type"] == "Random":
        agents = [agent.Random() for i in range(num_agents)]
    elif data["agent_type"] == "PathPlanner":
        agents = [agent.PathPlanner(agent_id=i) for i in range(num_agents)]
    elif data["agent_type"] == "Debug":
        agents = [agent.Debug(agent_id=i) for i in range(num_agents)]
    '''
    elif data["agent_type"] == "QuadrantsSocialConventions":
        agents = [agent.QuadrantsSocialConventions(agent_id=i) for i in range(num_agents)]
    elif data["agent_type"] == "IDsSocialConventions":
        agents = [agent.IDsSocialConventions(agent_id=i) for i in range(num_agents)]
    elif data["agent_type"] == "Roles":
        agents = [agent.Roles(agent_id=i) for i in range(num_agents)]
    '''


    map = grid.Map(default.MAP)

    run_with_graphics = data["graphical"]
    log_level = data["log_level"]
    n_runs = data["n_runs"]

    drones_distances = []
    all_n_steps = []

    if run_with_graphics:
        iterable = range(n_runs)
    else:
        iterable = tqdm.tqdm(range(n_runs))
    
    for _ in iterable:
        if run_with_graphics:
            drones, n_steps = run_graphical(map, agents, log_level)
            #drones, n_delivered, n_steps = run_graphical(map, agents, log_level)
        else:
            #taxis, passengers, n_delivered, n_steps = run_not_graphical(map, agents, log_level)
            drones, n_steps = run_not_graphical(map, agents, log_level)

        # media da distancia percorrida pelos drones
        avg_drone_distance = np.mean([drone.total_distance for drone in drones])

        drones_distances.append(avg_drone_distance)
        all_n_steps.append(n_steps)

    # Stores each run in the following format
    # n_agents, n_passengers, avg_taxi_distance, avg_pick_up_time, avg_drop_off_time, avg_n_steps
    with open(f"metrics-{data['agent_type']}-agents-{num_agents}.csv", "w") as metrics:
        metrics.write("drone_distance,n_steps\n")
        for d, n in zip(drones_distances, all_n_steps):
            metrics.write(f"{d},{n}\n")



if __name__ == "__main__":
    main()