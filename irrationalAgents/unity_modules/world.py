from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Tuple
from datetime import datetime
from config.config import DEFAULT_SPEED
from unity_modules.map import Map
from unity_modules.path_planner import PathPlanner
from unity_modules.tools import advance_time_by_15_minutes
from config.logger_config import setup_logger
from config.meta_manager import meta_manager
from agents_modules.agent import init_agent_manager, get_agent_manager

logger = setup_logger('World')


"""
 {
            "position" :{
                'x': status['position']['x'],
                'y': status['position']['y'],
                'direction': status['position']['direction']
            },
            "location": status['location'],
            "action": "move",
            "description": "Dorm for College:A room:spaces:sp-A",
            "move_extra": {
            }
        }
"""


class WorldState:
    def __init__(self, map_data: Dict[str, Any]):
        """Initialize the world state with map data and core components."""
        self.town_map = Map(map_data)
        self.meta_manager = meta_manager
        self.path_planner = PathPlanner(self.town_map)
        self.global_time = self.meta_manager.get_start_datetime()
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        init_agent_manager()
        self.agent_manager = get_agent_manager()
        self._validate_initial_state()

    def _validate_initial_state(self) -> None:
        """Validate the initial state of the world."""
        if not isinstance(self.global_time, datetime):
            raise ValueError("Global time must be a datetime object")
        if len(self.agent_manager.agents) == 0:
            logger.warning("No agents initialized in the world")

    def refresh_status(self, npc_status: Dict[str, Dict[str, int]]) -> None:
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

        if npc_name in self.agent_manager.agents:
            agent = self.agent_manager.agents[npc_name]

            if not tile_position:
                tile_position = self.town_map.get_address_tiles(
                    agent.short_memory.current_location)

            self.town_map.add_npc_to_tile(npc_name, tile_position)
            tile = self.town_map.get_tile_details(tile_position)
            agent.short_memory.current_location = f"{tile['location']}:{tile['room']}:{tile['space']}"

            status = self.agent_manager.generate_agent_snapshot(
                agent,
                **status,
                action=status['state'].get('activity'),
                description=status['state'].get('description'),
                step=self.meta_manager.get('step'),
                time=self.global_time.isoformat()
            )
            if self.meta_manager.get('step') == 1:
                self.agent_manager.write_agent_status(npc_name, self.global_time, status)

    def _clear_npc_positions(self) -> None:
        """Clear all NPC position markers from the map."""
        for i in range(self.town_map.maze_height):
            for j in range(self.town_map.maze_width):
                if self.town_map.tiles[i][j]['npc'] != '_':
                    self.town_map.tiles[i][j]['npc'] = '_'

    def tick_world(self, npc_status: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
        """
        Update the world state concurrently for all agents.
            # update agent positions
            # update world state
            # process events to npc
            # update tile according to agent information

        Returns:
            Dictionary containing world updates after the tick

        Raises:
            Exception: If any error occurs during world update
        """
        try:
            self.refresh_status(npc_status)

            # 1. Collect environment information
            environment_info = self._collect_env_info(npc_status)
            if not environment_info:
                logger.warning("No environment info collected for tick")

            # 2. Update all agents concurrently
            results = self._update_all_agents(environment_info)

            # 3. Refresh world time
            self._advance_world_time()
            snapshots = self._generate_npc_snapshot(results, npc_status)

            self._add_world_info(snapshots)
            logger.info(
                f"World tick completed for step {self.meta_manager.get('step')}, time {self.global_time}, snapshots: {snapshots}")

            return snapshots
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

    def _add_world_info(self, infos) -> None:
        world_info = set()
        self.town_map.remove_all_event_from_tiles()
        for npc, info in infos.items():
            if info.get('activity', None) in ['chat', 'interact']:
                world_info.add(
                    (info['position']['x'], info['position']['y'], info['description']))
                self.town_map.add_event_to_tile(
                    (info['position']['x'], info['position']['y']). info['description'])
        return world_info

    def _generate_npc_snapshot(self, results: List[Tuple[str, str, str]], npc_status) -> Dict[str, Any]:
        """
        Generate world updates after all agents have been updated.

        Args:
            results: List of agent update results (name, action, description)

        Returns:
            Dictionary containing world state updates
        """
        updates = {}
        for agent_name, action, description in results:
            updates[agent_name] = self.agent_manager.generate_agent_snapshot(
                self.agent_manager.agents[agent_name],
                **npc_status[agent_name],
                action=action,
                description=description,
                time=self.global_time.isoformat(),
                step=self.meta_manager.get('step'),
                location=self.agent_manager.agents[agent_name].short_memory.current_location
            )
            if action == "move":
                try:
                    x = npc_status[agent_name]['position']['x']
                    y = npc_status[agent_name]['position']['y']
                    co_destination = self.town_map.get_address_tiles(description.replace(":spaces:", ":"))
                    if co_destination:
                        destination = next(iter(co_destination))
                        move_extra = {
                            "path": self.path_planner.create_path((x, y), destination),
                            "speed": DEFAULT_SPEED
                        }
                        updates[agent_name]['state']['move_extra'] = move_extra
                    else:
                        logger.warning(f"No destination found for {description}")
                except Exception as e:
                    logger.error(f"Error creating path: {str(e)}")
                    raise e

            self.agent_manager.write_agent_status(
                agent_name,
                self.global_time, updates[agent_name])
            
        return updates

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
            # @TODO refien the expression
            stimuli.append(
                f"currently seeing events: {events}, currently seeing items: {set(items)}, currently seeing npcs: {npcs}")

        logger.debug(f"Generated stimuli: {stimuli}")
        return stimuli

    def _collect_env_info(self, npc_status) -> Dict[str, Dict[str, Any]]:
        """
        Collect environment information for all agents.

        Returns:
            Dictionary mapping agent names to their environment info
        """
        environment_info = {}
        positions = self.agent_manager.get_all_agents_positions(self.global_time)

        if len(positions) != len(self.agent_manager.agents):
            logger.warning(
                f"Position count mismatch. Agents: {len(self.agent_manager.agents)}, "
                f"Positions: {len(positions)}"
            )

        for agent_name, agent in self.agent_manager.agents.items():
            pos = positions.get(agent_name)
            if not pos:
                logger.warning(f"No position found for agent {agent_name}")
            

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
