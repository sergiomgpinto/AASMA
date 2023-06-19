import abc
from typing import Any


class Strategy(abc.ABC):
    """Strategy class for the agents"""

    @abc.abstractmethod
    def run(agent, env_timestep) -> Any:
        """Runs the strategy."""
        pass


class CooperativeCharging(Strategy):
    """Cooperative charging strategy."""
    def run(agent, env_timestep) -> int:
        """Runs the cooperative charging strategy."""
        resources_dict = agent.get_energy_level_and_seed_status()
        resources_dict[agent.get_id()] = {'battery_available': agent.get_drone().get_battery_available(), 'nr_seeds': agent.get_drone().get_nr_seeds()}
        intention_dict = agent.get_charging_status()
        intention_dict[agent.get_id()] = env_timestep
        filtered_intention_dict = {agent_id: timestep for agent_id, timestep in intention_dict.items() if
                                   timestep == env_timestep}
        min_battery_level = min(
            resources_dict[agent_id]['battery_available'] for agent_id in filtered_intention_dict.keys() if
            agent_id in resources_dict and 'battery_available' in resources_dict[agent_id])

        min_battery_agents = [agent_id for agent_id in filtered_intention_dict if
                              resources_dict.get(agent_id, {}).get('battery_available',
                                                                   float('inf')) == min_battery_level]

        return min(min_battery_agents)
