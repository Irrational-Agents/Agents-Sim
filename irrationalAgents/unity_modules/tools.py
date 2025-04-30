import os
import json
from typing import Dict
from config.logger_config import setup_logger
from config.common_method import *
from config.config import NPC_STORAGE_BASE_PATH, META_FILE_PATH, SIM_FILE_PATH, NPC_STORAGE_BASE_PATH_MAIN

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

def create_sim_id() -> int:
    # Load existing meta data
    with open(META_FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get current sim_id, default to 0 if not present
    sim_id = data.get('sim_id', 0)

    # Increment sim_id
    sim_id += 1
    data['sim_id'] = sim_id

    # Save back to file
    with open(SIM_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    # Create directory
    new_dir_path = os.path.join(NPC_STORAGE_BASE_PATH_MAIN, str(sim_id))
    os.makedirs(new_dir_path, exist_ok=True)

    return sim_id

def create_meta_data(sim_id: int, data: Dict) -> Dict:
    # Convert npcList (a list) into a name-indexed dictionary
    npcs = {npc["name"]: npc for npc in data.get("npcList", [])}

    sim_config = {
        "sim_id": sim_id,
        "sim_type": data.get("sim_type"),
        "map_name": data.get("map_name"),
        "steps_per_min": data.get("steps_per_min"),
        "start_date": data.get("start_date"),
        "start_time": data.get("start_time"),
        "total_steps": data.get("total_steps"),
        "end_time": data.get("end_time"),
        "end_date": data.get("end_date"),
        "npcs": npcs,
        "player_enabled": data.get("player_enabled", False),
        "player_name": data.get("player_name", ""),
        "npc_names": [npc["name"] for npc in data.get("npcList", [])]
    }

    return sim_config

def load_replay_meta_data(replay_id: int) -> Dict:
    replay_path = os.path.join(NPC_STORAGE_BASE_PATH)
    if not os.path.exists(replay_path):
        logger.error(f"Replay {replay_id} not found!")
        return None

    with open(os.path.join(replay_path, "meta.json"), 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data