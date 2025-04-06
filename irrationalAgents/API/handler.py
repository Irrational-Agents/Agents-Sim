from typing import Dict, Any
from config.logger_config import setup_logger
from config.common_method import *
from API.request import UnityRequest
from unity_modules.tools import *
from unity_modules.world import WorldState

logger = setup_logger('API-unity-handler')


class UnityHandlers:
    def __init__(self):
        self.unity_request: UnityRequest = None
        self.map_data = None
        self.clock = 0
        self.npc_status = None
        self.player_status = None
        self.world = None
        self.agent_manager = None

    def update(self, data: Dict[str, Any]):
        """Handle updates from the client."""
        try:
            self.clock = int(data['clock'])
            self.npc_status = data['npc_status']
            self.player_status = data['player_status']

            if self.clock == 0:  # initialize
                logger.debug("initialize")
                self.map_data = data['map_data']
                self.world = WorldState(self.map_data)
                self.unity_request.send_server_tick(1, None)
                return

            # MAIN LOOP
            # update agent positions
            # update world state
            # process events to npc
            # update tile according to agent information
            # self.world.update_status(self.npc_pos)

            updates = {
                "Kenta Takahashi": {
                    "activity": "move",
                    "path": self.world.path_planner.create_path(
                        (53, 14), (93, 74))
                }
            }

            updates_c = {
                "Kenta Takahashi": {
                    "activity": "move",
                }
            }

            if "Kenta Takahashi" in self.npc_status:
                if self.npc_status["Kenta Takahashi"]['activity'] == "move":
                    self.unity_request.send_server_tick(1, updates_c)
                    return

            self.unity_request.send_server_tick(1, updates)

        except ValueError as e:
            logger.error(
                f"Invalid data received for update: {data}. Error: {e}")

    def handle_get_npcs(self, params: Dict) -> Dict:
        """Handle request to get all NPCs"""
        try:
            logger.info(f"get_npcs: {params}")
            npcs = get_npcs(params)
            self.unity_request.emit('npc.getList.response', {
                                    'npcs': npcs})
        except Exception as e:
            logger.error(f"Error getting NPCs: {str(e)}")
            return {'error': str(e)}
