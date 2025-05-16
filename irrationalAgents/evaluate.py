'''
Author: Yifei Wang
Github: ephiewangyf@gmail.com
Date: 2025-04-29 15:45:22
LastEditors: ephie && ephiewangyf@gmail.com
LastEditTime: 2025-05-06 21:14:54
FilePath: /Agents-Sim/irrationalAgents/evaluate.py
Description: 
'''
from agents_modules.agent import Agent
import json
import os
from config.config import *
from datetime import datetime, timedelta

def build_prompt(question_text, options_dict):
    options_str = "\n".join([f"{k}: {v}" for k, v in options_dict.items()])
    prompt = f"""I will ask you a question, here is the question: {question_text}
            Options:
            {options_str}
            Please respond with the letter of your choice (A, B, C, or D) only."""
    return prompt


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
    
    with open(os.path.join(EVALUATION_BASE_PATH, f"ques.json"), 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    res_j = list()

    print(f"test agent: {agent.basic_info['name']}")
    try:
        for q in questions:
            question_id = q["id"]
            question_text = q["question"]
            options = q["options"]

            print(f"⏳ Asking agent: {question_id}")
            a, d = agent.move(curr_time, ["seeing npc: Ephie", build_prompt(question_text, options)])
            print(f"🤖 Agent's answer:{a}, {d}")
            curr_time = curr_time + timedelta(minutes=15)
            meta['step'] += 1
            res_j.append(      {
                'id': question_id,
                'response': d
            })
    except Exception as e:
        print('Attention pls Error:', e)
        agent.short_memory.save(agent.short_memory)
        meta['curr_time'] = curr_time.strftime('%H:%M')
        meta['curr_date'] = curr_time.strftime('%Y-%m-%d')
        raise e

    with open(os.path.join(EVALUATION_BASE_PATH, "res.json"), 'w', encoding='utf-8') as f:
        json.dump(res_j, f, ensure_ascii=False, indent=2)
            
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