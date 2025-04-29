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
                return
                
            # MAIN LOOP
            updates = self.world.tick_world(self.npc_status)
            
            self.clock += 1
            self.unity_request.send_server_tick(1, updates)

        except ValueError as e:
            logger.error(
                f"Invalid data received for update: {data}. Error: {e}")
