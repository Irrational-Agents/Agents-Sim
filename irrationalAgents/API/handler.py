from typing import Dict, Any
from config.logger_config import setup_logger
from config.common_method import *
from API.request import UnityRequest
from unity_modules.tools import *
from unity_modules.world import WorldState
from agents_modules.agent import AgentManager
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

    def handle_map_data(self, data: Dict[str, Any]):
        logger.debug("map_data received")
        self.map_data = data

    def update(self, data: Dict[str, Any]):
        """Handle updates from the client."""
        try:
            self.clock = int(data['clock'])
            self.npc_status = data['npc_status']
            self.player_status = data['player_status']

            if self.clock == 0:  # initialize
                logger.debug("initialize")
                self.map_data = data['map_data']
                if self.map_data is not None:
                    self.world = WorldState(self.map_data, self.unity_request)

                    #self.agent_manager = AgentManager()
                    # for name,agent in self.agent_manager.agents.items():
                    #     logger.info(f"Generating plan for {name}")
                    #     agent.plan(new_day=True)

                    #x,y = self.world.town_map.get_address_tiles('house F:second bedroom:sp-B')
                    

                    res = {
                        "clock" : 1,
                        "updates": {
                            "Kenta Takahashi": {
                                "activity": "move",
                                "path": self.world.path_planner.create_path(
                                    (53,14),[94, 74])
                            }
                        }
                    }

                    self.unity_request.send_server_tick(res)
                else:
                    self.unity_request.get_map_data()
                    self.unity_request.send_server_tick(1)
                    return
            else:
               self.unity_request.send_server_tick({
                        "clock" : 0})

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
