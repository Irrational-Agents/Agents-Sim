from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Tuple
from datetime import datetime

from unity_modules.map import Map
from unity_modules.path_planner import PathPlanner
from unity_modules.tools import advance_time_by_15_minutes
from config.logger_config import setup_logger
from config.meta_manager import MetaManager
from agents_modules.agent import AgentManager

logger = setup_logger('World')


class WorldState:
    def __init__(self, map_data: Dict[str, Any]):
        """Initialize the world state with map data and core components."""
        self.town_map = Map(map_data)
        self.meta_manager = MetaManager()
        self.path_planner = PathPlanner(self.town_map)
        self.global_time = self.meta_manager.get_start_datetime()
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.agent_manager = AgentManager()
        self._validate_initial_state()

    def _validate_initial_state(self) -> None:
        """Validate the initial state of the world."""
        if not isinstance(self.global_time, datetime):
            raise ValueError("Global time must be a datetime object")
        if len(self.agent_manager.agents) == 0:
            logger.warning("No agents initialized in the world")

    def update_status(self, npc_status: Dict[str, Dict[str, int]]) -> None:
        """
        Update agent positions on the map and in the agent manager.

        Args:
            npc_positions: Dictionary mapping NPC names to their positions (x, y)

        Raises:
            ValueError: If npc_positions is empty or invalid
        """
        if not npc_status:
            logger.warning("Received empty npc_positions in update_status")
            return

        self._clear_npc_positions()

        for npc_name, status in npc_status.items():
            self._update_agent_position(npc_name, status)

    def _update_agent_position(self, npc_name: str, status: Dict[str, int]) -> None:
        """Update position for a single agent."""
        tile_position = (status['position']['x'], status['position']['y'])
        self.town_map.add_npc_to_tile(npc_name, tile_position)

        if npc_name in self.agent_manager.agents:
            agent = self.agent_manager.agents[npc_name]
            logger.info(agent.short_memory.current_status)
            agent.short_memory.current_status.append(status)
            self.agent_manager.write_agent_status(
                npc_name, agent.short_memory.current_status)

    def _clear_npc_positions(self) -> None:
        """Clear all NPC position markers from the map."""
        for i in range(self.town_map.maze_height):
            for j in range(self.town_map.maze_width):
                if self.town_map.tiles[i][j]['npc'] != '_':
                    self.town_map.tiles[i][j]['npc'] = '_'

    def tick_world(self) -> Dict[str, Any]:
        """
        Update the world state concurrently for all agents.

        Returns:
            Dictionary containing world updates after the tick

        Raises:
            Exception: If any error occurs during world update
        """
        try:
            # 1. Collect environment information
            environment_info = self._collect_env_info()
            if not environment_info:
                logger.warning("No environment info collected for tick")

            # 2. Update all agents concurrently
            results = self._update_all_agents(environment_info)

            # 3. Advance world time
            self._advance_world_time()

            logger.info("World tick completed successfully")
            return self._generate_world_updates(results)

        except Exception as e:
            logger.error(f"World tick failed: {str(e)}", exc_info=True)
            raise

    def _update_all_agents(self, environment_info: Dict[str, Any]) -> List[Tuple[str, str, str]]:
        """Update all agents concurrently and return results."""
        update_tasks = [
            self.thread_pool.submit(
                self._update_agent,
                agent_name,
                env_info
            )
            for agent_name, env_info in environment_info.items()
        ]

        results = []
        for future in as_completed(update_tasks):
            try:
                result = future.result()
                results.append(result)
                logger.debug(f"Agent update result: {result}")
            except Exception as e:
                logger.error(f"Agent update failed: {str(e)}")
                raise

        return results

    def _advance_world_time(self) -> None:
        """Advance the world time by 15 minutes."""
        advanced_time, advanced_date = advance_time_by_15_minutes(
            self.global_time.strftime("%H:%M"),
            self.global_time.strftime("%Y-%m-%d")
        )

        self.meta_manager.set_curr_datetime(advanced_date, advanced_time)
        self.meta_manager.set_step(self.meta_manager.get('step') + 1)
        self.meta_manager.write_meta()
        self.global_time = self.meta_manager.get_datetime()
        logger.debug(f"World time advanced to {self.global_time}")

    def _generate_world_updates(self, results: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        """
        Generate world updates after all agents have been updated.

        Args:
            results: List of agent update results (name, action, description)

        Returns:
            Dictionary containing world state updates
        """
        updates = {}
        for agent_name, action, desc in results:
            if action == "move":
                x, y = self.town_map.get_address_tiles(
                    'house F:second bedroom:sp-B')
                updates[agent_name] = {
                    "activity": action,
                    "path": self.path_planner.create_path((53, 14), [94, 74])
                }

        return {
            "clock": 1,
            "updates": updates
        }

    def _update_agent(self, agent_name: str, env_info: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Update a single agent's state.

        Args:
            agent_name: Name of the agent to update
            env_info: Environment information for the agent

        Returns:
            Tuple containing (agent_name, action, description)
        """
        agent = self.agent_manager.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent {agent_name} not found")

        stimuli = self._build_stimuli(env_info)
        action, move_description = agent.move(self.global_time, stimuli)

        logger.info(
            f"{agent_name} action: {action}, description: {move_description}")

        status = self._generate_agent_status(
            agent_name, action, move_description)
        self.agent_manager.write_agent_status(agent_name, status)

        return agent_name, action, move_description

    def _build_stimuli(self, env_info: Dict[str, Any]) -> List[str]:
        """
        Process environment information to generate stimuli list.

        Args:
            env_info: Dictionary containing environment information

        Returns:
            List of stimulus strings
        """
        stimuli = []
        items = []
        npcs = []
        events = []

        for tile in env_info.get('nearby_tiles', []):
            if tile.get('events'):
                events.extend(tile['events'])
            if tile.get('item'):
                items.append(tile['item'])
            if tile.get('npc'):
                npcs.append(tile['npc'])

        if events or items or npcs:
            stimuli.append(
                f"seeing events: {events}, items: {items}, npcs: {npcs}")

        logger.debug(f"Generated stimuli: {stimuli}")
        return stimuli

    def _collect_env_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Collect environment information for all agents.

        Returns:
            Dictionary mapping agent names to their environment info
        """
        environment_info = {}
        positions = self.agent_manager.get_all_agents_positions()

        if len(positions) != len(self.agent_manager.agents):
            logger.warning(
                f"Position count mismatch. Agents: {len(self.agent_manager.agents)}, "
                f"Positions: {len(positions)}"
            )

        for agent_name, agent in self.agent_manager.agents.items():
            pos = positions.get(agent_name)
            if not pos:
                logger.warning(f"No position found for agent {agent_name}")
                continue

            try:
                nearby_tiles = self.town_map.generate_visible_tiles(
                    (pos['x'], pos['y']))
                environment_info[agent_name] = {
                    "nearby_tiles": nearby_tiles,
                    "current_position": pos
                }
                logger.debug(f"Collected environment for {agent_name}")
            except Exception as e:
                logger.error(
                    f"Failed to collect environment for {agent_name}: {str(e)}")
                continue

        return environment_info

    def _generate_agent_status(self, agent_name: str, action: str, description: str) -> Dict[str, Any]:
        """
        Generate status dictionary for an agent.

        Args:
            agent_name: Name of the agent
            action: Current action of the agent
            description: Description of the action

        Returns:
            Dictionary containing agent status
        """
        agent = self.agent_manager.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent {agent_name} not found")

        pos = agent.short_memory.current_status.get('spawn', {})

        return {
            'action': action,
            'description': description,
            'spawn': pos,
            'timestamp': self.global_time.isoformat()
        }
