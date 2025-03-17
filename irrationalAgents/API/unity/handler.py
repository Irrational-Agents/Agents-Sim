# handlers.py
import os
import json
from typing import Dict, Any
from datetime import datetime
from logger_config import setup_logger
from API.unity.models import *
from API.unity.config import *
from common_method import *
from API.unity.request import UnityRequest
from API.unity.map import Map
from config import WORK_DIR

logger = setup_logger('API-unity-handler')


def gen_agent_by_name(name):
    root_dir = os.path.join(WORK_DIR, f'../storage/sample_data/agents/{name}')
    if not os.path.exists(root_dir):
        logger.error(f"agent {name} not exists!")
        return None

    with open(os.path.join(root_dir, "basic_info.json"), 'r', encoding='utf-8') as f:
        basic_info = json.load(f)
    with open(os.path.join(root_dir, "memory/short_term.json"), 'r', encoding='utf-8') as f:
        short_mem = json.load(f)
    return basic_info, short_mem


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
            request = NPCGetRequest(**params)

            with open(os.path.join(self.NPC_STORAGE_BASE_PATH, "meta.json"), 'r', encoding='utf-8') as f:
                data = json.load(f)

            if request.names:
                logger.info(f"Received get request for NPCs: {request.names}")
                # 检查NPCs是否存在
                valid_npcs = []
                invalid_npcs = []
                for name in request.names:
                    if convert_id2name(name) in data["agents_list"]:
                        valid_npcs.append(name)
                    else:
                        invalid_npcs.append(name)

                if not valid_npcs:
                    return {'error': f"No valid NPCs found. Invalid NPCs: {invalid_npcs}"}

                if invalid_npcs:
                    logger.warning(f"Skipping invalid NPCs: {invalid_npcs}")
            else:
                valid_npcs = [convert_name2id(name)
                              for name in data["agents_list"]]
            # 获取NPC信息
            npcs = []
            for npc_id in valid_npcs:
                agent, status = gen_agent_by_name(npc_id)
                if request.isDetails:
                    npc_data = NPCModel(**agent)
                    npc_data.status = status
                else:
                    npc_data = NPCInfoModel(**(agent | status))
                npcs.append(npc_data)
            self.unity_request.emit('npc.getList.response', {
                                    'npcs': [npc.model_dump() for npc in npcs] or None})
        except Exception as e:
            logger.error(f"Error getting NPCs: {str(e)}")
            return {'error': str(e)}

    def handle_get_npc_info(self, params: Dict) -> Dict:
        """Handle request to get specific NPC info"""
        try:
            npc_id = params.get('NPCID')

            with open(os.path.join(self.NPC_STORAGE_BASE_PATH, "meta.json"), 'r', encoding='utf-8') as f:
                data = json.load(f)

            if convert_id2name(npc_id) not in data["agents_list"]:
                logger.warning(f'NPC {npc_id} not found')
                return {'error': f"NPC '{npc_id}' not found"}

            agent, status = gen_agent_by_name(npc_id)
            logger.debug(f"get agent {agent}")
            npc_data = NPCModel(**agent)
            npc_data.status = status

            self.unity_request.emit('npc.getInfo.response', {
                                    'npc': npc_data.model_dump()})

        except Exception as e:
            logger.error(f"Error getting NPC info: {str(e)}")
            return {'error': str(e)}

    def handle_npc_navigate(self, params: Dict) -> Dict:
        pass

    def handle_chat(self, params: Dict) -> Dict:
        pass
