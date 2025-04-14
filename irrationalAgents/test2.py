from agents_modules.agent import Agent
import json
import os
from config.config import *
from memory_modules.short_term_memory import form_short_memory
from datetime import datetime, timedelta

def main():
    with open(META_FILE_PATH, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    #agent = create_agent(input("name: "))
    agent = create_agent('zhang_san')
    
    curr_time = datetime.strptime(f"{meta['curr_date']} {meta['curr_time']}", "%Y-%m-%d %H:%M")
    start_time = datetime.strptime(f"{meta['start_date']} {meta['start_time']}", "%Y-%m-%d %H:%M")
    if curr_time != start_time:
         # if not agent.short_memory.curr_datetime:
        agent.short_memory.curr_datetime = curr_time

    print(f"test agent: {agent.basic_info['name']}")
    count = 1
    try:
        while(count <= 1):
            print(f'loop {count}')
            #event = input("Shota(User):  ")
            agent.move(curr_time, "")
            # if count % 4 == 0:
            #     agent.short_memory.short_memory = form_short_memory(agent)
            curr_time = curr_time + timedelta(minutes=15)
            count += 1
            meta['step'] += 1
    except Exception as e:
        agent.short_memory.save(agent.short_memory)
        meta['curr_time'] = curr_time.strftime('%H:%M')
        meta['curr_date'] = curr_time.strftime('%Y-%m-%d')
        raise e
        
    agent.short_memory.save(agent.short_memory)
    meta['curr_time'] = curr_time.strftime('%H:%M')
    meta['curr_date'] = curr_time.strftime('%Y-%m-%d')

    with open(META_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=4)


def create_agent(name):
    root_dir = NPC_STORAGE_BASE_PATH
    with open(os.path.join(root_dir, f"agents/{name}/basic_info.json"), 'r', encoding='utf-8') as f:
        basic_info = json.load(f)
    memory_folder_path = os.path.join(root_dir, f"agents/{name}/memory")
    agent = Agent(basic_info, memory_folder_path)
    return agent

if __name__ == "__main__":
    main()