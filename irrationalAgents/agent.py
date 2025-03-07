import json


from memory_modules.long_term_memory import *
from memory_modules.short_term_memory import *
from common_method import *
from stimulus import *
from agents_modules.behavior.plan import *
from agents_modules.behavior.plan_evaluation import *
from agents_modules.behavior.action import *
from agents_modules.personality.cognition import *
from agents_modules.personality.emotion import *
from agents_modules.personality.personality import *
from typing import Dict, Any, List
from datetime import datetime, timedelta
from logger_config import setup_logger
from config.meta_manager import MetaManager

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
            self.action(best_plan)

class AgentManager:
    def __init__(self, spawn_config_path: str):
        """
        初始化Agent管理器
        
        Args:
            spawn_config_path: spawn.json的路径
        """
        self.agents: Dict[str, Agent] = {}
        self.curr_time: datetime = None
        self.spawn_config_path = spawn_config_path
        self.meta_manager = MetaManager()
        self.curr_time = self.meta_manager.get_datetime()
        self.load_agents()
        
    def load_agents(self):
        """从spawn配置文件加载所有agent"""
        try:
            with open(self.spawn_config_path, 'r', encoding='utf-8') as f:
                spawn_data = json.load(f)
                
            # 获取开始时间
            self.curr_time = datetime.strptime(
                f"{spawn_data.get('start_date')} {spawn_data.get('curr_time')}", 
                "%Y-%m-%d %H:%M"
            )
            
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
        root_dir = os.path.join(WORK_DIR, f'../storage/sample_data/agents/{name}')
        if not os.path.exists(root_dir):
            logger.error(f"agent {name} not exists!")
            return None, None

        with open(os.path.join(root_dir, "basic_info.json"), 'r', encoding='utf-8') as f:
            basic_info = json.load(f)
        
        memory_folder_path = os.path.join(root_dir, "memory")
        return basic_info, memory_folder_path

    def update_all(self, events: List[str]):
        """
        用于处理外部整体事件，比如当前世界的促销活动, 天气环境等
        @todo: 这里可以考虑由前端触发
        
        Args:
            events: 需要处理的事件列表
        """
        for agent_name, agent in self.agents.items():
            try:
                logger.info(f"更新 {agent_name} 状态")
                agent.move(list(self.agents.keys()), self.curr_time, events)
            except Exception as e:
                logger.error(f"更新 {agent_name} 时出错: {str(e)}")

    def get_all_agents_positions(self):
        positions = {}
        for agent_name, agent in self.agents.items():
            position = self._get_agent_position(agent_name, agent)
            if position:
                positions[agent_name] = position

        return positions
    
    def _get_agent_position(self, agent_name, agent):
        return agent.basic_info.get('spawn_point', None)
    
    def advance_time_by_15_minutes(curr_time, curr_date):
        current_datetime = datetime.strptime(f"{curr_date} {curr_time}", "%Y-%m-%d %H:%M")
        
        advanced_datetime = current_datetime + timedelta(minutes=15)

        advanced_time = advanced_datetime.strftime("%H:%M")
        advanced_date = advanced_datetime.strftime("%Y-%m-%d")
        
        return advanced_time, advanced_date
    
    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """
        获取指定agent的状态
        
        Args:
            agent_name: agent的名称
            
        Returns:
            包含agent状态信息的字典
        """
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            return {
                "current_time": self.curr_time,
                "memory": agent.short_memory.short_memory[-1] if agent.short_memory.short_memory else None,
                "emotion": agent.short_memory.emotion,
                "basic_info": agent.basic_info
            }
        return None
