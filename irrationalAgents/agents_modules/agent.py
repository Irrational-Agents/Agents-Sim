import json

from memory_modules.long_term_memory import *
from memory_modules.short_term_memory import *
from config.common_method import *
from agents_modules.stimulus import *
from agents_modules.behavior.plan import *
from agents_modules.behavior.plan_evaluation import *
from agents_modules.behavior.action import *
from agents_modules.personality.cognition import *
from agents_modules.personality.emotion import *
from agents_modules.personality.personality import *
from typing import Dict, Any
from config.logger_config import setup_logger
from config.meta_manager import MetaManager
from config.config import *
logger = setup_logger('Agent')


class Agent:
    def __init__(self, basic_info, memory_folder_path=False):
        
        self.basic_info = basic_info

        self.name = basic_info['name']


        long_memory_path = f"{memory_folder_path}/long_term"
        self.long_memory = LongTermMemory(long_memory_path)

        short_memory_path = f"{memory_folder_path}/short_term.json"
        self.short_memory = ShortTermMemory(short_memory_path)

        if basic_info.get('personality'):
            self.short_memory.personality_text = basic_info.get('personality')
        else:
            self.short_memory.personality_text = generate_personality(basic_info['personality_traits'])

        self.basic_profile = profile_to_narrative(basic_info) 
        self.formed_profile = self.basic_profile + self.short_memory.personality_text
        self.relationships = basic_info['social_relationships']
        self.short_memory.emotion_memory.append(self.short_memory.emotion)


    def stimulus(self, event):
        return stimulus(self, event)
    
    def plan(self, new_day):
        return plan(self, new_day)
    
    def plan_evaluation(self, plan_list):
        return plan_evaluation(self, plan_list)
    
    def action(self, best_plan):
        return action(self, best_plan)

    def emotion(self):
        return emotion(self)
    
    def cognition(self):
        return cognition(self)

    def growth(self):
        growth(self)


    def move(self, curr_time, event):

        #核心逻辑
        #用于处理agent的事件

        if isinstance(event, list):
            events = event
        else:
            events = []
            events.append(event)

        new_day = False
        if not self.short_memory.curr_datetime: 
            new_day = "First day"
            self.short_memory.short_memory = []
        elif (self.short_memory.curr_datetime.strftime('%A %B %d')
            != self.short_memory.curr_datetime.strftime('%A %B %d')):
            new_day = "New day"
        self.short_memory.curr_datetime = curr_time
        self.short_memory.curr_time = self.short_memory.curr_datetime.strftime('%H:%M')
        self.short_memory.curr_date = self.short_memory.curr_datetime.strftime('%Y-%m-%d')
            
        stimulus = self.stimulus(events)

        if stimulus == "sys2":
            return
        elif stimulus == "sys1":
            plan_list = self.plan(new_day)
            best_plan = self.plan_evaluation(plan_list)
            self.short_memory.save(self.short_memory)
            description = self.action(best_plan)
            return best_plan.get('action', None), description

class AgentManager:
    def __init__(self):
        """
        初始化Agent管理器
        
        Args:
            meta_config_path: meta.json的路径
        """
        self.agents: Dict[str, Agent] = {}
        
        self.meta_manager = MetaManager()

        self.load_agents()
        
    def load_agents(self):
        """spawn配置文件加载所有agent"""
        try:
            with open(SPAWN_FILE_PATH, 'r', encoding='utf-8') as f:
                spawn_data = json.load(f)

            for agent_name, agent_data in spawn_data.items():
                if isinstance(agent_data, dict):  # 跳过非agent的配置项
                    self.agents[agent_name] = self.create_agent(agent_name)
                    logger.info(f"Agent {agent_name} 已创建")
                    
        except Exception as e:
            logger.error(f"加载agents时出错: {str(e)}")
            raise
    
    def create_agent(self, name):
        basic_info, memory_folder_path = self._get_agent_info_by_name(name)
        if basic_info is None:
            return None
        return Agent(basic_info, memory_folder_path)
    
            
    def _get_agent_info_by_name(self, name):
        
        root_dir = os.path.join(NPC_STORAGE_BASE_PATH, f'agents/{name}')
        
        if not os.path.exists(root_dir):
            logger.error(f"agent {name} not exists!")
            return None, None

        with open(os.path.join(root_dir, "basic_info.json"), 'r', encoding='utf-8') as f:
            basic_info = json.load(f)
        
        memory_folder_path = os.path.join(root_dir, "memory")
        return basic_info, memory_folder_path

    def get_all_agents_positions(self):
        positions = {}
        for agent_name, agent in self.agents.items():
            position = agent.short_memory.current_status.get('spawn', None)
            if position:
                positions[agent_name] = position

        return positions
    
    def write_agent_status(self, agent_name: str, status: Dict[str, Any]):
        """
        写入agent的status
        """
        with open(NPC_STORAGE_BASE_PATH + f'agents/{agent_name}/memory/short_term.json', 'w', encoding='utf-8') as f:
            data = json.load(f)
            data['current_status'] = status
            json.dump(data, f, ensure_ascii=False, indent=4)
        return status
    
    def get_agent_current_status(self, agent_name: str) -> Dict[str, Any]:
        """
        获取指定agent的当前状态
        """
        with open(NPC_STORAGE_BASE_PATH + f'agents/{agent_name}/memory/short_term.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['current_status']
    
    def get_agent_psychological_status(self, agent_name: str) -> Dict[str, Any]:
        """
        获取指定agent的情感状态
        
        Args:
            agent_name: agent的名称
            
        Returns:
            包含agent状态信息的字典
        """
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            return {
                "memory": agent.short_memory.short_memory[-1] if agent.short_memory.short_memory else None,
                "emotion": agent.short_memory.emotion,
                "basic_info": agent.basic_info
            }
        return None

    def erase_all_agents(self, storage: bool = True):
        """
        删除所有agent
        """
        agent_names = list(self.agents.keys())
        for agent_name in agent_names:
            self.erase_agent(agent_name, storage)
    
    def erase_agent(self, agent_name: str, storage: bool = True):
        """
        删除指定agent, 包括basic_info.json, short_term.json, long_term.json
        """
        # 删除spawn.json中的agent
         # 删除spawn.json中的agent
        with open(SPAWN_FILE_PATH, 'r', encoding='utf-8') as f:
            spawn_data = json.load(f)
        
        # 从数据中移除agent
        if agent_name in spawn_data:
            spawn_data.pop(agent_name)
        
        # 将修改后的数据写回文件
        with open(SPAWN_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(spawn_data, f, ensure_ascii=False, indent=4)
        
        # 从内存中移除agent
        if agent_name in self.agents:
            self.agents.pop(agent_name)

        if storage:
            # 删除 short_term.json, long_term.json
            #@todo
            pass
