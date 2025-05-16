import os
import json
from typing import Dict
from config.logger_config import setup_logger
from config.common_method import *
from config.config import NPC_STORAGE_BASE_PATH, META_FILE_PATH, SIM_FILE_PATH, NPC_STORAGE_BASE_PATH_MAIN, set_meta_file_path, set_npc_storage_base_path, get_npc_storage_base_path

logger = setup_logger('tools')


def mess_agent_by_name(name):
    if ' ' in name:
        name = convert_name2id(name)

    root_dir = os.path.join(get_npc_storage_base_path(), f'agents/{name}')
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
    with open(SIM_FILE_PATH, 'r', encoding='utf-8') as f:
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

    short_term_memory = {
        "age": 21,
        "current_location": data.get("spawn"),
        "short_term_goal_capacity": 3,
        "short_term_goal": [
        ],
        "short_memory_capacity": 50,
        "short_memory_for_plan": [
        ],
        "daily_plan_req": [
        ],
        "short_memory": [
        ],
        "basic_needs": {
            "fullness": 6.7,
            "social": 6.1,
            "fun": 6.3,
            "health": 7.2,
            "energy": 6.5
        },
        "temporary_personality_changes": {
            "openness": 0,
            "conscientiousness": 0,
            "extraversion": 0, 
            "agreeableness": 0,
            "neuroticism": 0
        },
        "emotion": [
            0,
            0,
            1,
            7,
            0,
            2,
            0
        ]
    }

    status = {
        "00:00:00": {
            "state": {
            "activity": "free",
            "description": None
            },
        "time": "2024-04-01T00:00:00",
        "step": 1,
        "location": "apartment A:main room:sp-A",
        "position": {
            "x": 53,
            "y": 14,
            "direction": "down"
        }
    }
    }

    # Path where the file will be saved
    save_path = os.path.join(NPC_STORAGE_BASE_PATH_MAIN, str(sim_id))

    # Ensure the directory exists; create it if it does not
    os.makedirs(save_path, exist_ok=True)
    os.makedirs(os.path.join(save_path, "agents"), exist_ok=True)

    for npc_name in sim_config["npc_names"]:
        npc_path = os.path.join(save_path, "agents", convert_name2id(npc_name))
        os.makedirs(npc_path, exist_ok=True)
        os.makedirs(os.path.join(npc_path,"memory"), exist_ok=True)
        os.makedirs(os.path.join(npc_path,"memory","long_term"), exist_ok=True)
        os.makedirs(os.path.join(npc_path,"snapshots"), exist_ok=True)
        os.makedirs(os.path.join(npc_path,"logs"), exist_ok=True)

        # Save the basic info and short-term memory for each NPC
        with open(os.path.join(npc_path, "basic_info.json"), 'w', encoding='utf-8') as f:
            json.dump(sim_config["npcs"][npc_name], f, ensure_ascii=False, indent=4)
        with open(os.path.join(npc_path, "memory/short_term.json"), 'w', encoding='utf-8') as f:
            short_term_memory["current_location"] = sim_config["npcs"][npc_name]["spawn"]
            short_term_memory["temporary_personality_changes"]["openness"] = sim_config["npcs"][npc_name]["personality_traits"]["openness"]
            short_term_memory["temporary_personality_changes"]["conscientiousness"] = sim_config["npcs"][npc_name]["personality_traits"]["conscientiousness"]
            short_term_memory["temporary_personality_changes"]['extraversion'] = sim_config["npcs"][npc_name]["personality_traits"]["extraversion"]
            short_term_memory["temporary_personality_changes"]["agreeableness"] = sim_config["npcs"][npc_name]["personality_traits"]["agreeableness"]
            short_term_memory["temporary_personality_changes"]["neuroticism"] = sim_config["npcs"][npc_name]["personality_traits"]["neuroticism"]

            json.dump(short_term_memory, f, ensure_ascii=False, indent=4)
        with open(os.path.join(npc_path, f"logs/2025-04-30.json"), 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)

        with open(os.path.join(npc_path, f"snapshots/2025-04-30.json"), 'w', encoding='utf-8') as f:
            status['00:00:00']['location'] = sim_config["npcs"][npc_name]["spawn"]
            json.dump(status, f, ensure_ascii=False, indent=4)

    # Define the path to the meta.json file
    meta_file_path = os.path.join(save_path, "meta.json")
    set_meta_file_path(meta_file_path)
    set_npc_storage_base_path(save_path)
    
    # Check if the file exists; if not, initialize with an empty dictionary
    if not os.path.exists(meta_file_path):
        # If file doesn't exist, create and initialize it
        with open(meta_file_path, 'w', encoding='utf-8') as f:
            json.dump(sim_config, f, ensure_ascii=False, indent=4)
    

    return sim_config

def load_replay_meta_data(replay_id: int) -> Dict:
    replay_path = os.path.join(NPC_STORAGE_BASE_PATH_MAIN, str(replay_id))
    set_npc_storage_base_path(replay_path)
    logger.debug(f"Loading replay meta data from {replay_path}")
    if not os.path.exists(replay_path):
        logger.error(f"Replay {replay_id} not found!")
        return None

    with open(os.path.join(replay_path, "meta.json"), 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data