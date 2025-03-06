# handlers.py
import os
from typing import Dict, Any
from logger_config import setup_logger
from API.unity.models import *
from common_method import *
from API.unity.request import UnityRequest
from API.unity.map import Map
from config import WORK_DIR
from API.unity.tools import *

logger = setup_logger('API-unity-handler')


class UnityHandlers:
    def __init__(self):
        self.NPC_STORAGE_BASE_PATH = os.path.join(
            WORK_DIR, "../storage/sample_data")
        self.unity_request: UnityRequest = None
        self.map_data = None
        self.clock = 0
        self.npc_pos = None
        self.player_pos = None
        self.map_translator = None

    def handle_map_data(self, data: Dict[str, Any]):
        self.map_data = data

    def update(self, data: Dict[str, Any]):
        """Handle updates from the client."""
        # @todo need to restructure in the future
        try:

            self.clock = int(data['clock'])
            self.npc_pos = data['npc_pos']
            self.player_pos = data['player_pos']

            if self.clock == 0:
                if self.map_data is not None:
                    self.map = Map(self.map_data)
                    self.unity_request.send_server_tick(1)
                else:
                    self.unity_request.get_map_data()
                    # if return is 0 frame will not be updated
                    self.unity_request.send_server_tick(0)
            else:
                for npc in self.npc_pos:
                    x = self.npc_pos[npc]['x']
                    y = self.npc_pos[npc]['y']

                    self.map.add_npc_to_tile(npc, (x, y))

                    # get nearby tiles
                    logger.info(self.map.get_nearby_tiles((x, y), 1))

                    # get details on tiles
                    logger.info(self.map.get_tile_details((x, y)))

                # comment to stop
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
