import os
from typing import Dict, Any, List
from unity_modules.map import Map
from unity_modules.tools import *
from agents_modules.agent import AgentManager
from config.logger_config import setup_logger
from config.meta_manager import MetaManager
from config.common_method import advance_time_by_15_minutes
from unity_modules.path_planner import PathPlanner
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = setup_logger('World')

class WorldState:
    def __init__(self, map_data: Dict):
        self.map = Map(map_data)
        self.agent_manager = AgentManager()
        self.meta_manager = MetaManager()
       # self.path_planner = PathPlanner(self.map)
        self.global_time = self.meta_manager.get_start_datetime()
        self.map_translator = None
        # 创建线程池
        self.thread_pool = ThreadPoolExecutor(max_workers=10)

    def update_agent_positions(self, npc_positions: Dict[str, Dict[str, int]]):
        """
        更新Agent在地图上的位置
        """
        # 清除旧的NPC位置
        self._clear_npc_positions()
        # 更新新的位置
        for npc_name, pos in npc_positions.items():
            # 更新地图上的位置
            self.map.add_npc_to_tile(npc_name, (pos['x'], pos['y']))
            
            # 更新Agent管理器中的位置，考虑需要将当前spawn信息和地图信息同步 保留一处维护
            # 暂时预留这个逻辑，
            # 1， 地图信息需要同步到agent的spawn信息 ✅ or
            # 2， agent的spawn信息需要同步到地图信息
            if npc_name in self.agent_manager.agents:
                logger.info(f"update_agent_positions: {npc_name} {pos}")

                self.agent_manager.agents[npc_name].short_memory.current_status['spawn'] = pos
                self.agent_manager.agents[npc_name].short_memory.current_status['next_spawn'] = pos
                self.agent_manager.write_agent_status(npc_name, self.agent_manager.agents[npc_name].short_memory.current_status)

    def _clear_npc_positions(self):
        """清除地图上所有NPC的位置标记"""
        for i in range(self.map.maze_height):
            for j in range(self.map.maze_width):
                if self.map.tiles[i][j]['npc'] != '_':
                    self.map.tiles[i][j]['npc'] = '_'

    def tick_world(self):
        """
        并发更新世界状态
        """
        try:
            # 1. 收集环境信息
            environment_info = self._collect_env_info()
            
            # 2. 创建所有agent更新任务
            update_tasks = []
            update_tasks = [
                self.thread_pool.submit(self._update_agent, agent_name, env_info)
                for agent_name, env_info in environment_info.items()
            ]
            
            # 3. 并发执行所有更新任务
            for future in as_completed(update_tasks):
                try:
                    result = future.result()
                    logger.debug(f"Agent update result: {result}")
                except Exception as e:
                    logger.error(f"更新Agent时出错: {str(e)}")
                    raise e
            # 4. 更新世界时间
            advanced_time, advanced_date = advance_time_by_15_minutes(self.global_time.strftime("%H:%M"), self.global_time.strftime("%Y-%m-%d"))            
            # 更新MetaManager中的时间, 用于后续断点恢复
            self.meta_manager.set_curr_datetime(advanced_date, advanced_time)
            self.meta_manager.set_step(self.meta_manager.get('step') + 1)
            self.meta_manager.write_meta()
            self.global_time = self.meta_manager.get_datetime()
            
            logger.info("所有Agent更新完成")
            
        except Exception as e:
            logger.error(f"更新世界状态时出错: {str(e)}")
            raise

    def _update_agent(self, agent_name: str, env_info: Dict[str, Any]):
        """        
        Args:
            agent_name: agent的名称
            env_info: 环境信息
        """
        agent = self.agent_manager.agents[agent_name]
        
        # 构建环境刺激
        stimuli =  self._build_stimuli(env_info)
        
        action, move_description = agent.move(self.global_time, stimuli)
        logger.info(f"{agent_name} action: {action}, move_description: {move_description}")

        status = self.gen_npc_current_status(agent_name, action, move_description)
        logger.debug(f"{agent_name} status: {status}")
        self.agent_manager.write_agent_status(agent_name, status)

        logger.debug(f"Agent {agent_name} 更新完成")
        return agent_name, action, move_description

    def _build_stimuli(self, env_info: Dict[str, Any]) -> List[str]:
        """
        处理环境信息，生成刺激列表
        """
        stimuli = []
        items = []
        npcs = []
        events = []
        
        # 处理周围的tile信息
        for tile in env_info['nearby_tiles']:
            if tile.get('events'):
                for event in tile['events']:
                    events.append(event)
            if tile.get('item'):
                items.append(tile['item'])
            if tile.get('npc'):
                npcs.append(tile['npc'])
        
        # 处理当前位置的tile信息
        #todo: 需要处理当前位置的tile信息，包括地址，房间，楼层，事件等

        stimuli.append(f"seeing items: {items}")
        stimuli.append(f"seeing npcs: {npcs}")
        #stimuli.append(f"seeing events: {events}") temporary commented for parsing
        logger.debug(f"stimuli: {stimuli}")
            
        return stimuli

        
    def _collect_env_info(self) -> Dict[str, Dict]:
        """
        收集每个NPC周围的环境信息
        """
        environment_info = {}
        positions = self.agent_manager.get_all_agents_positions()
        if len(positions) != len(self.agent_manager.agents):
            logger.error(f"NPC位置信息与Agent管理器中的数量不匹配, positions: {positions}, agents: {self.agent_manager.agents.keys()}")
            
        for agent_name, _ in self.agent_manager.agents.items():
            try:
                # 获取NPC当前位置
                pos = positions.get(agent_name)
                if not pos:
                    continue
                
                # 收集周围环境信息
                nearby_info = {
                    "nearby_tiles": self.map.generate_visible_tiles(
                        (pos['x'], pos['y'])
                    )
                }
                environment_info[agent_name] = nearby_info
                logger.debug(f"已收集 {agent_name} 的环境信息")
                
            except Exception as e:
                logger.error(f"收集 {agent_name} 的环境信息时出错: {str(e)}")
                continue
                
        return environment_info
    
    def gen_npc_current_status(self, agent_name: str, action: str, move_description: str) -> Dict[str, Any]:
        """
        生成NPC的当前状态
        """
        # todo: map_translator: translate from pos to location, room etc
        pos = self.agent_manager.agents[agent_name].short_memory.current_status['spawn']
        status = {
            'action': action,
            'description': move_description,
            'spawn': pos
        }
        # if action == 'move':
        #     path = self.path_planner.plan_path_from_memory(move_description, pos)
        #     if path:
        #         status = {**path, **status}
        return status