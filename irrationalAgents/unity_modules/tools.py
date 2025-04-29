import os
import json
from typing import Dict
from config.logger_config import setup_logger
from config.common_method import *
from config.config import NPC_STORAGE_BASE_PATH, META_FILE_PATH

logger = setup_logger('tools')


def mess_agent_by_name(name):
    if ' ' in name:
        name = convert_name2id(name)

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
        if params.get('npc_names'):
            names = params.get('npc_names')
        else:
            with open(META_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                names = list(data.get('npc_names'))

                if data.get("player_name") != '':
                    names.append(data.get("player_name"))
      
        npcs = []
        for npc_name in names:
            basic_info, short_mem = mess_agent_by_name(npc_name)
            if not basic_info:
                continue
            else:
                npc_data = {**basic_info, **short_mem}
            npcs.append(npc_data)
        return npcs
    except Exception as e:
        logger.error(f"Error getting NPCs: {str(e)}")
        return {'error': str(e)}

def get_npc_info(params: Dict) -> Dict:
    """Handle request to get specific NPC info"""
    npc_name  = params.get('npc_name')

    agent, status = mess_agent_by_name(npc_name)
    logger.debug(f"get agent {agent}")
    npc_data = {**agent, **status}
    return npc_data

def get_meta() -> Dict:
    with open(META_FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data