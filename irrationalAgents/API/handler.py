from typing import Dict, Any, List, Tuple, Union
from config.logger_config import setup_logger
from config.common_method import *
from API.request import UnityRequest
from API.journey import get_journey
from unity_modules.tools import *
from unity_modules.world import WorldState
import re

logger = setup_logger('API-unity-handler')


class UnityHandlers:
    def __init__(self):
        self.unity_request: UnityRequest = None
        self.map_data = None
        self.clock = 0
        self.npc_status = None
        self.player_status = None
        self.world = None
        self.character_schedule: Dict[str, Dict[int, Dict[str, Any]]] = {}
        self.meta = None

    def init(self, data: Dict[str, Any]):
        """Handle initial data from the client."""
        logger.info("Initializing server...")
        logger.debug(f"Received init data: {data}")
        
        sim_type = data.get('sim_type')

        if sim_type == "replay":
            self.meta = load_replay_meta_data(data['replay_id'])
            self.meta['sim_type'] = sim_type
        elif sim_type == "play":
            sim_id = create_sim_id()
            self.meta = create_meta_data(sim_id, data)
        
        self.unity_request.send_init(self.meta)

    def plan_journeys(self, plan: Dict[str, List[Union[Tuple[int, int, str], Dict[str, Any], str]]]):
        """
        Plan journeys, activities, and waits for each character.
        """
        for character, steps in plan.items():
            current_clock = 2  # Planning starts at clock 2
            self.character_schedule[character] = {}

            for step in steps:
                if isinstance(step, tuple) or (isinstance(step, list) and len(step) == 3):
                    start, end, description = step
                    path = self.world.path_planner.create_path(start, end)

                    # First tick: send full path
                    self.character_schedule[character][current_clock] = {
                        "state": {
                            "activity": "move",
                            "description": description,
                            "path": path
                        }
                    }
                    current_clock += 1

                    # Follow-up ticks: moving step-by-step
                    for _ in range(len(path)):
                        self.character_schedule[character][current_clock] = {
                            "state": {
                                "activity": "move",
                                "description": description
                            }
                        }
                        current_clock += 1

                elif isinstance(step, dict):
                    # Other states (e.g., interact, chat)
                    self.character_schedule[character][current_clock] = {
                        "state": step
                    }
                    current_clock += 1

                elif isinstance(step, str) and step.startswith("Wait for"):
                    match = re.match(r"Wait for (\d+) steps", step)
                    if match:
                        steps_to_wait = int(match.group(1))
                        for _ in range(steps_to_wait):
                            # For wait, put empty dict for each wait tick
                            self.character_schedule[character][current_clock] = {}
                            current_clock += 1

    def get_update(self, clock: int) -> Dict[str, Any]:
        updates = {}

        for character, schedule in self.character_schedule.items():
            if clock in schedule:
                updates_for_char = schedule[clock]
                # Only add if non-empty update (no update for empty dict during wait)
                if updates_for_char:
                    updates[character] = updates_for_char

        return updates
    def update(self, data: Dict[str, Any]):
        """Handle updates from the client."""
        logger.info(f"ui-tick: {data}")
        
        try:
            self.clock = int(data['clock'])
            self.npc_status = data['npc_status']
            self.player_status = data['player_status']

            if self.clock == 0:  # initialize
                logger.debug("initialize")
                self.map_data = data['map_data']
                self.world = WorldState(self.map_data)
                self.clock += 1
                self.unity_request.send_server_tick(1, None)

                if self.meta['sim_type'] == "replay":
                    self.plan_journeys(get_journey())

                return
            
            updates = {}
            logger.info(self.meta['sim_type'])
            if self.meta['sim_type'] == "replay":
                updates = self.get_update(self.clock)
            else:
                updates = self.world.tick_world(self.npc_status)

            
            self.unity_request.send_server_tick(self.clock, updates)

        except ValueError as e:
            logger.error(
                f"Invalid data received for update: {data}. Error: {e}")
