import json
import os
from config import config

def denormalize_journey_data(structured_data, world):
    denormalized = {}

    for npc_name, actions in structured_data.items():
        raw_actions = []

        for action in actions:
            if isinstance(action, dict):
                activity_type = action.get("activity")

                if activity_type == "wait":
                    steps = action.get("steps")
                    raw_actions.append(f"Wait for {steps} steps")

                elif activity_type == "move":
                    path = action.get("path", [])
                    description = action.get("description", "")
                    if len(path) == 2 and all(isinstance(p, (list, tuple)) for p in path):
                        p1 = path[0]
                        p2 = path[1]
                        if isinstance(p1, list) and len(p1) == 2:
                            p1 = tuple(p1)
                        else:
                            p1 = world.town_map.get_address_tiles(p1)

                        if isinstance(p2, list) and len(p2) == 2:
                            p2 = tuple(p2)
                        else:
                            p2 = world.town_map.get_address_tiles(p2)
                        raw_actions.append([p1, p2, description])
                    else:
                        raw_actions.append(action)  # fallback

                else:
                    # Leave other structured types (think, chat, etc.) as-is
                    raw_actions.append(action)

            else:
                raw_actions.append(action)  # Unstructured or already raw

        denormalized[npc_name] = raw_actions

    return denormalized

def get_journey(world):  
    """
    Get the journey of the player from a snapshot JSON file.
    """
    path = config.get_npc_storage_base_path()
    file_path = os.path.join(path, "snapshot.json")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return denormalize_journey_data(data, world)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Invalid JSON format in file: {file_path}")
        return None
