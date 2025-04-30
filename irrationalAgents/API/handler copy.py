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
                self.unity_request.send_server_tick(self.clock, None)
                return
            
            # MAIN LOOP - Using actual map locations and items
            updates = {
                "Zhang San": {
                    "state": {
                        "activity": "move",
                        "description": "Going to the cafe to work",
                        "path": self.world.path_planner.create_path((26, 18), (77, 19))
                    }
                },
                "Kenta Takahashi": {
                    "state": {
                        "activity": "interact",
                        "description": "Playing guitar in apartment A",
                        "location": "apartment A:main room:items:guitar"
                    }
                },
                "Sakura Sato": {
                    "state": {
                        "activity": "move",
                        "description": "Returning from college to apartment",
                        "path": self.world.path_planner.create_path(
                            (126, 46),
                            (122, 25)
                        )
                    }
                }
            }
            
            # Minimal continuation updates with actual locations
            updates_c = {
                "Kenta Takahashi": {
                    "state": {
                        "activity": "think",
                        "description": "Composing new music",
                        "location": "apartment A:main room:items:desk"
                    }
                },
                "Sakura Sato": {
                    "state": {
                        "activity": "move",
                        "description": "Walking to next location"
                    }
                }
            }

            
            if self.clock == 2:
                self.unity_request.send_server_tick(self.clock, updates)
            # else:
            #     self.unity_request.send_server_tick(self.clock, updates_c)

        except ValueError as e:
            logger.error(
                f"Invalid data received for update: {data}. Error: {e}")