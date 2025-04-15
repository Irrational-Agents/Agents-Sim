import json
import os
from typing import Dict, Any, Optional, Tuple, List

from memory_modules.long_term_memory import LongTermMemory
from memory_modules.short_term_memory import ShortTermMemory, form_short_memory
from config.common_method import convert_name2id, profile_to_narrative
from agents_modules.stimulus import stimulus
from agents_modules.behavior.plan import plan
from agents_modules.behavior.plan_evaluation import plan_evaluation
from agents_modules.behavior.action import action
from agents_modules.personality.cognition import cognition, growth
from agents_modules.personality.emotion import emotion
from agents_modules.personality.personality import generate_personality
from config.logger_config import setup_logger
from config import config

logger = setup_logger('Agent')

agent_manager  = None

class Agent:
    def __init__(self, basic_info: Dict[str, Any], memory_folder_path: Optional[str] = None):
        """
        Initialize an Agent with basic information and memory paths.
        
        Args:
            basic_info: Dictionary containing agent's basic information
            memory_folder_path: Path to the agent's memory storage
        """
        self.basic_info = basic_info
        self.name = basic_info['name']

        # Initialize memory systems
        long_memory_path = os.path.join(memory_folder_path, "long_term") if memory_folder_path else None
        self.long_memory = LongTermMemory(long_memory_path)

        short_memory_path = os.path.join(memory_folder_path, "short_term.json") if memory_folder_path else None
        self.short_memory = ShortTermMemory(short_memory_path)

        # Initialize personality
        self.short_memory.personality_text = (
            basic_info.get('personality') or 
            generate_personality(basic_info['personality_traits'])
        )

        # Initialize profile and relationships
        self.basic_profile = profile_to_narrative(basic_info)
        self.formed_profile = self.basic_profile + self.short_memory.personality_text
        self.relationships = basic_info.get('social_relationships', {})
        
        # Initialize emotion memory
        self.short_memory.emotion_memory.append(self.short_memory.emotion)

    def stimulus(self, event: Any) -> str:
        """Process an event stimulus."""
        return stimulus(self, event)

    def plan(self, new_day: bool) -> List[Dict[str, Any]]:
        """Generate plans based on current state."""
        return plan(self, new_day)

    def plan_evaluation(self, plan_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate and select the best plan."""
        return plan_evaluation(self, plan_list)

    def action(self, best_plan: Dict[str, Any]) -> str:
        """Execute the best plan."""
        return action(self, best_plan)

    def emotion(self) -> Dict[str, Any]:
        """Update and return current emotion state."""
        return emotion(self)

    def cognition(self) -> Dict[str, Any]:
        """Perform cognitive processing."""
        return cognition(self)
    
    def growth(self) -> Dict[str, Any]:
        return growth(self)

    def move(self, curr_time: Any, event: Any) -> Optional[Tuple[Any, str]]:
        """
        Process agent movement and event handling.
        
        Args:
            curr_time: Current datetime object
            event: Event or list of events to process
            
        Returns:
            Tuple of (action, description) if action is taken, None otherwise
        """
        # Normalize events to list
        events = [event] if not isinstance(event, list) else event

        # Handle new day logic
        new_day = False
        if not self.short_memory.curr_datetime or (self.short_memory.curr_datetime.strftime('%A %B %d') != 
              curr_time.strftime('%A %B %d')):
            new_day = True

        # Update time tracking
        self.short_memory.curr_datetime = curr_time
        self.short_memory.curr_time = curr_time.strftime('%H:%M')
        self.short_memory.curr_date = curr_time.strftime('%Y-%m-%d')
        # Handle new day operations for cognitive growth
        if new_day:
            logger.debug(f"New day for Agent {self.name}")
            
            self.short_memory.add_short_memory(form_short_memory(self))
            self.short_memory.save(self.short_memory)
            self.short_memory.short_memory_for_plan = []

            self.long_memory.update_all_freshness(curr_time)
            self.short_memory.organize_memory(self.long_memory)
            self.short_memory.cleanup_short_memory()
            self.long_memory.save(self.long_memory)
            #self.growth(self.cognition())

        # Process stimulus
        stimulus_result = self.stimulus(events)
        logger.debug(f"{self.short_memory.curr_date}:{self.short_memory.curr_time} agent {self.name}")

        # Handle stimulus results
        if stimulus_result == "sys2":
            return None
        elif stimulus_result == "sys1":
            plan_list = self.plan(new_day)
            logger.info(f"{self.name} {self.short_memory.curr_date} plan: {plan_list}")

            best_plan = self.plan_evaluation(plan_list)
            logger.info(f"{self.name}'s best_plan: {best_plan}")

            description = self.action(best_plan)
            return best_plan.get('action', None), description
        
        #self.growth(self.cognition())
        return None


class AgentManager:
    def __init__(self):
        """Initialize Agent manager and load all agents."""
        self.agents: Dict[str, Agent] = {}
        self.load_agents()

    def load_agents(self) -> None:
        """Load all agents from meta configuration."""
        try:
            with open(config.META_FILE_PATH, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)

            for agent_name in meta_data['npc_names']:
                agent_data = self.create_agent(agent_name)
                if agent_data:
                    self.agents[agent_name] = agent_data
                    logger.info(f"Agent {agent_name} created successfully")

        except Exception as e:
            logger.error(f"Error loading agents: {str(e)}")
            raise

    def create_agent(self, name: str) -> Optional[Agent]:
        """Create an agent instance by name."""
        basic_info, memory_folder_path = self._get_agent_info_by_name(name)
        return Agent(basic_info, memory_folder_path) if basic_info else None

    def _get_agent_info_by_name(self, name: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Retrieve agent information by name."""
        root_dir = os.path.join(
            config.NPC_STORAGE_BASE_PATH, 
            f'agents/{convert_name2id(name)}'
        )

        if not os.path.exists(root_dir):
            logger.error(f"Agent {name} does not exist!")
            return None, None

        try:
            with open(os.path.join(root_dir, "basic_info.json"), 'r', encoding='utf-8') as f:
                basic_info = json.load(f)
            memory_folder_path = os.path.join(root_dir, "memory")
            return basic_info, memory_folder_path
        except Exception as e:
            logger.error(f"Error loading agent {name} info: {str(e)}")
            return None, None

    def save_agents(self, agent: Agent) -> None:
        for _, agent in self.agents.items():
            agent.short_memory.save(agent.short_memory)  
    
    def generate_agent_snapshot(self, agent, action=None, description=None, step=None, position=None, time=None, location=None, **kwargs):
        if time is None:
            time = agent.short_memory.curr_datetime
        if location is None:
            location = agent.short_memory.current_location

        ret =   {
            "state": {
                    "activity": action,
                    "description": description
                },
            "time": time,
            "step": step,
            "location": location,
            "position": position
        }

        logger.debug(f"Agent {agent.name} snapshot: {ret}")
        return ret

    def get_all_agents_positions(self, file_path, index_) -> Dict[str, Any]:
        """Get current positions of all agents."""
        status_dict = {}
        for agent_name, _ in self.agents.items():
            status = self.get_agent_current_status(agent_name, file_path, index_)
            if status:
                status_dict[agent_name] = status.get('position')

        return status_dict

    def write_agent_status(self, agent_name: str, file_path, index_, status: Dict[str, Any]) -> Dict[str, Any]:
        """Update agent's status in storage."""
        file_path = os.path.join(
            config.NPC_STORAGE_BASE_PATH,
            f'agents/{convert_name2id(agent_name)}/snapshots/{file_path}.json'
        )
        data = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}

        if not isinstance(data, dict):
            data = {}

        data[index_] = status

        # 写入更新后的数据
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_agent_current_status(self, agent_name: str, file_path, index_) -> Dict[str, Any]:
        """Get current status of specified agent."""
        file_path = os.path.join(
            config.NPC_STORAGE_BASE_PATH,
            f'agents/{convert_name2id(agent_name)}/snapshots/{file_path}.json'
        )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get(str(index_), {})
        except Exception as e:
            logger.error(f"Error getting status for agent {agent_name}: {str(e)}")

    def get_agent_psychological_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get psychological status of specified agent."""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            return {
                "memory": agent.short_memory.short_memory[-1] if agent.short_memory.short_memory else None,
                "emotion": agent.short_memory.emotion,
                "basic_info": agent.basic_info
            }
        return None

    def erase_all_agents(self, storage: bool = True) -> None:
        """Remove all agents from memory and optionally from storage."""
        agent_names = list(self.agents.keys())
        for agent_name in agent_names:
            self.erase_agent(agent_name, storage)

    def erase_agent(self, agent_name: str, storage: bool = True) -> None:
        """Remove specified agent from memory and optionally from storage."""
        # Remove from spawn data
        try:
            with open(config.SPAWN_FILE_PATH, 'r', encoding='utf-8') as f:
                spawn_data = json.load(f)

            if agent_name in spawn_data:
                spawn_data.pop(agent_name)

            with open(config.SPAWN_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(spawn_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error removing agent {agent_name} from spawn data: {str(e)}")

        # Remove from memory
        if agent_name in self.agents:
            del self.agents[agent_name]

        if storage:
            # TODO: Implement storage cleanup
            pass



def init_agent_manager():
    global agent_manager
    agent_manager = AgentManager()

def get_agent_manager():
    return agent_manager