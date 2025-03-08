# handlers.py
import os
from typing import Dict, Any
from logger_config import setup_logger
from unity_modules.models import *
from common_method import *
from API.request import UnityRequest
from unity_modules.tools import *
from unity_modules.world import WorldState
logger = setup_logger('API-unity-handler')


class UnityHandlers:
    def __init__(self):
        self.unity_request: UnityRequest = None
        self.map_data = None
        self.clock = 0
        self.npc_pos = None
        self.player_pos = None
        self.world = None
        
    def handle_map_data(self, data: Dict[str, Any]):
        self.map_data = data

    async def update(self, data: Dict[str, Any]):
        """Handle updates from the client."""
        try:

            self.clock = int(data['clock'])
            self.npc_pos = data['npc_pos']
            self.player_pos = data['player_pos']

            if self.clock == 0:# initialize
                if self.map_data is not None:
                    self.world = WorldState(self.map_data)
                    #self.unity_request.send_server_tick(1)
                else:
                    self.unity_request.get_map_data()
                    # if return is 0 frame will not be updated
                    self.unity_request.send_server_tick(0)
            
            # MAIN LOOP
            # update agent positions
            # update world state
            # process events to npc
            # update tile according to agent information
            
            self.world.update_agent_positions(self.npc_pos)
            results = await self.world.tick_world()

            self.unity_request.send_server_tick(1)

        except ValueError as e:
            logger.error(
                f"Invalid data received for update: {data}. Error: {e}")

    def handle_get_npcs(self, params: Dict) -> Dict:
        """Handle request to get all NPCs"""
        try:
            npcs = get_npcs(params)
            self.unity_request.emit('npc.getList.response', {
                                    'npcs': npcs})
        except Exception as e:
            logger.error(f"Error getting NPCs: {str(e)}")
            return {'error': str(e)}

    def handle_get_npc_info(self, params: Dict) -> Dict:
        """Handle request to get specific NPC info"""
        try:
            npc_data = get_npc_info(params)
            self.unity_request.emit('npc.getInfo.response', {
                                    'npc': npc_data})

        except Exception as e:
            logger.error(f"Error getting NPC info: {str(e)}")
            return {'error': str(e)}

    def handle_npc_navigate(self, params: Dict) -> Dict:
        pass

    def handle_chat(self, params: Dict) -> Dict:
        pass
