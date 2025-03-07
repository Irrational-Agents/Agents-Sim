import os
import json
from typing import List
from fastapi import HTTPException
from API.server_draft.models import NPCModel, NPCInfoModel
from functools import wraps
from agent import gen_agent_by_name
from typing import Callable, Union, List
from logger_config import setup_logger

logger = setup_logger('API-server-handler')

NPC_STORAGE_BASE_PATH = "storage/sample_data/agents"

def npc_path_handler(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        npc_names = kwargs.get('names') or args[0]
        
        if isinstance(npc_names, str):
            npc_names = [npc_names]
            is_single = True
        else:
            is_single = False
            
        file_paths = []
        for name in npc_names:
            npc_dir = os.path.join(NPC_STORAGE_BASE_PATH, name)
            os.makedirs(npc_dir, exist_ok=True)
            
            file_paths.append(os.path.join(npc_dir, "basic_info.json"))
        
        kwargs['file_path'] = file_paths[0] if is_single else file_paths
        
        return func(*args, **kwargs)
    return wrapper

@npc_path_handler
def save_npc(npc: NPCModel, file_path: str):
    try:
        npc_dir = os.path.dirname(file_path)
        memory_structure = {
            'memory': {
                'long_term': ['embeddings.json', 'kw_strength.json', 'nodes.json'],
                'short_term.json': None
            }
        }

        def create_structure(base_path: str, structure: dict) -> None:
            for key, value in structure.items():
                path = os.path.join(base_path, key)
                if isinstance(value, dict):
                    os.makedirs(path, exist_ok=True)
                    create_structure(path, value)
                elif isinstance(value, list):
                    os.makedirs(path, exist_ok=True)
                    for file_name in value:
                        file_path = os.path.join(path, file_name)
                        if not os.path.exists(file_path):
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump({}, f)
                elif value is None:
                    if not os.path.exists(path):
                        with open(path, 'w', encoding='utf-8') as f:
                            json.dump({}, f)

        create_structure(npc_dir, memory_structure)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(npc.model_dump(), f, ensure_ascii=False, indent=2)
            
        logger.info(f"Successfully saved NPC data: {npc.name}")
        return gen_agent_by_name(npc.name)
        
    except Exception as e:
        logger.error(f"Error saving NPC data: {npc.name}, {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving NPC data for '{npc.name}'")
@npc_path_handler   
def get_npcs(names, is_details) -> List[Union[NPCModel, NPCInfoModel]]:

    #todo: this could be load from basic_info.json
    agents = [gen_agent_by_name(name) for name in names]
    
    if is_details:
        return agents
    else:
        return [
            NPCInfoModel(**agent.model_dump())
            for agent in agents
        ]
