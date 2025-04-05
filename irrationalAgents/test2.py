from agents_modules.agent import Agent
import json
import os
from config.config import *
from datetime import datetime, timedelta

def main():
    # basic_info.jsonを読み込む
    with open(META_FILE_PATH, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    
    sakura = create_agent(input("name: "))
    
    curr_time = datetime.strptime(f"{meta['start_date']} {meta['curr_time']}", "%Y-%m-%d %H:%M")
    
    # 動作確認
    print(f"test agent: {sakura.basic_info['name']}")
    while(True):
        
        event = input("Shota(User):  ") # should type wake up when new day
        sakura.move(curr_time, event)
        print(sakura.short_memory.short_memory[-1])
        curr_time = curr_time + timedelta(minutes=15)


def create_agent(name):
# プロジェクトのルートディレクトリを取得
    root_dir = NPC_STORAGE_BASE_PATH
    # basic_info.jsonを読み込む
    with open(os.path.join(root_dir, f"agents/{name}/basic_info.json"), 'r', encoding='utf-8') as f:
        basic_info = json.load(f)

    # memoryフォルダのパスを設定
    memory_folder_path = os.path.join(root_dir, f"agents/{name}/memory")

    # Agentインスタンスを作成
    sakura_agent = Agent(basic_info, memory_folder_path)

    return sakura_agent

if __name__ == "__main__":
    main()