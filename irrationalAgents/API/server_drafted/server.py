import os
import json
from typing import List
from fastapi import FastAPI, HTTPException,Query
from API.server_draft.models import * 
from API.server_draft.handler import *
from logger_config import setup_logger

logger = setup_logger('API-server')

app = FastAPI(title="NPC CRUD API")

NPC_STORAGE_BASE_PATH = "storage/sample_data/agents"

@app.get("/npcs", response_model=List[Union[NPCModel, NPCInfoModel]])
def get_npcs(request: NPCGetRequest):
    logger.info(f"Received get request for NPCs: {request.names}")
    
    valid_npcs = []
    invalid_npcs = []
    
    for name in request.names:
        with open("storage/sample_data/agents/spawn.json", 'w', encoding='utf-8') as f:
            data = json.load(f)
        if name not in data["agents_list"]:    
            invalid_npcs.append(name)
        else:
            valid_npcs.append(name)
    
    if not valid_npcs:
        raise HTTPException(
            status_code=400,
            detail=f"No valid NPCs found. Invalid NPCs: {invalid_npcs}"
        )
    
    if invalid_npcs:
        logger.warning(f"Skipping invalid NPCs: {invalid_npcs}")
    
    try:
        npcs = get_npcs(valid_npcs, request.isDetails)
        
        response = {
            npc.name: details 
            for npc, details in zip(valid_npcs, npcs)
        }
        
        logger.info(f"Successfully get NPCs: {list(response.keys())}")
        return response
        
    except Exception as e:
        logger.error(f"Error during NPC get: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting NPCs: {str(e)}"
        )

@app.post("/npcs/", response_model=NPCModel)
def create_npc(npc: NPCModel):
    try:
        with open("storage/sample_data/agents/spawn.json", 'w', encoding='utf-8') as f:
            data = json.load(f)
        if npc.prefered_name in data["agents_list"]:
            logger.warning(f"Attempting to create existing NPC: {npc.name}")
            raise HTTPException(status_code=400, detail=f"NPC '{npc.name}' already exists")

        ret = save_npc(npc)
        
        logger.info(f"Successfully created NPC: {npc.name}")
        return ret
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating NPC: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating NPC: {npc.name}")

@app.put("/npcs/{npc_name}", response_model=NPCModel)
def update_npc(npc_name: str, updated_npc: NPCModel):
    """I will leave this function as is. But I dont think NPC should be updated except for short-term data."""
    try:
        if updated_npc.name != npc_name:
            logger.warning(f"NPC name mismatch: path {npc_name}, data {updated_npc.name}")
            raise HTTPException(status_code=400, detail="NPC name in path must match the name in data")
        
        with open("storage/sample_data/agents/spawn.json", 'w', encoding='utf-8') as f:
            data = json.load(f)
        if npc_name in data["agents_list"]:
            logger.warning(f"Attempting to update existing NPC: {npc_name}")
            raise HTTPException(status_code=400, detail=f"NPC '{npc_name}' already exists")

        
        # Save updated NPC data
        save_npc(updated_npc)
        
        logger.info(f"Successfully updated NPC: {npc_name}")
        return updated_npc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating NPC: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating NPC: {npc_name}")

@app.delete("/npcs/{npc_name}")
def delete_npc(npc_name: str):
    """Delete a specific NPC"""
    try:
        npc_dir = os.path.dirname(os.path.join(NPC_STORAGE_BASE_PATH, npc_name))
        import shutil
        shutil.rmtree(npc_dir)

        with open("storage/sample_data/agents/spawn.json", 'w', encoding='utf-8') as f:
            data = json.load(f)
            data["agents_list"].remove(npc_name)
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Successfully deleted NPC: {npc_name}")
        return {"message": f"NPC '{npc_name}' deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting NPC: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting NPC: {npc_name}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)