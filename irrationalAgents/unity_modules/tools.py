import os
import json
from logger_config import setup_logger
from unity_modules.models import *
from common_method import *
from config.config import NPC_STORAGE_BASE_PATH, SPAWN_FILE_PATH

logger = setup_logger('tools')


def mess_agent_by_name(name):
    root_dir = os.path.join(NPC_STORAGE_BASE_PATH, f'agents/{name}')
    if not os.path.exists(root_dir):
        logger.error(f"agent {name} not exists!")
        return None, None

    with open(os.path.join(root_dir, "basic_info.json"), 'r', encoding='utf-8') as f:
        basic_info = json.load(f)
    with open(os.path.join(root_dir, "memory/short_term.json"), 'r', encoding='utf-8') as f:
        short_mem = json.load(f)
    return basic_info, short_mem



def get_npcs(params: Dict) -> Dict:
    """Handle request to get all NPCs"""
    try:
        request = NPCGetRequest(**params)

        with open(SPAWN_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)


        if request.names:
            logger.info(f"Received get request for NPCs: {request.names}")
            # 检查NPCs是否存在
            valid_npcs = []
            invalid_npcs = []
            for name in request.names:
                if convert_id2name(name) in list(data.keys()):
                    valid_npcs.append(name)
                else:
                    invalid_npcs.append(name)

            if not valid_npcs:
                return {'error': f"No valid NPCs found. Invalid NPCs: {invalid_npcs}"}

            if invalid_npcs:
                logger.warning(f"Skipping invalid NPCs: {invalid_npcs}")
        else:
            valid_npcs = [convert_name2id(name)
                            for name in list(data.keys())]
        # 获取NPC信息
        npcs = []
        for npc_id in valid_npcs:
            agent, status = mess_agent_by_name(npc_id)
            if not agent:
                continue
            if request.isDetails:
                npc_data = NPCModel(**agent)
                npc_data.status = status
            else:
                npc_data = NPCInfoModel(**(agent | status))
            npcs.append(npc_data)
        return [npc.model_dump() for npc in npcs] or None
    except Exception as e:
        logger.error(f"Error getting NPCs: {str(e)}")
        return {'error': str(e)}

def get_npc_info(params: Dict) -> Dict:
    """Handle request to get specific NPC info"""
    npc_id = params.get('NPCID')

    with open(SPAWN_FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if convert_id2name(npc_id) not in list(data.keys()):
        logger.warning(f'NPC {npc_id} not found')
        return {'error': f"NPC '{npc_id}' not found"}

    agent, status = mess_agent_by_name(npc_id)
    logger.debug(f"get agent {agent}")
    npc_data = NPCModel(**agent)
    npc_data.status = status
    return npc_data.model_dump()


def get_spawns() -> Dict:
    with open(SPAWN_FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


