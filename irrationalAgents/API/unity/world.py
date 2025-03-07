import os
from typing import Dict, Any
from API.unity.models import *
from common_method import *
from API.unity.map import Map
from API.unity.tools import *
from agent import AgentManager
from config.config import PERCEPTION_RANGE
from logger_config import setup_logger

logger = setup_logger('unity-world')

class WorldState:
    def __init__(self, map_data: Dict, spawn_config_path: str):
        self.map = Map(map_data)
        self.agent_manager = AgentManager(spawn_config_path)
        self.global_time = self.agent_manager.curr_time
        self.map_translator = None

        
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
                self.agent_manager.agents[npc_name].basic_info['spawn_point'] = pos

    def _clear_npc_positions(self):
        """清除地图上所有NPC的位置标记"""
        for i in range(self.map.maze_height):
            for j in range(self.map.maze_width):
                if self.map.tiles[i][j]['npc'] != '_':
                    self.map.tiles[i][j]['npc'] = '_'

    def update_world(self):
        """
        更新世界状态，包括环境信息和Agent状态
        """
        # 1. 收集环境信息
        environment_info = self._collect_env_info()
        
        # 2. 更新每个Agent的状态
        for agent_name, env_info in environment_info.items():
            agent = self.agent_manager.agents[agent_name]
            
            # 构建环境刺激
            stimuli = self._build_stimuli(env_info)
            
            # 更新Agent状态
            agent.move(
                env_info['nearby_agents'],
                self.global_time,
                stimuli
            )
            
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
                    "nearby_tiles": self.map.get_visible_tiles(
                        (pos['x'], pos['y'])
                    )
                }
                environment_info[agent_name] = nearby_info
                logger.debug(f"已收集 {agent_name} 的环境信息")
                
            except Exception as e:
                logger.error(f"收集 {agent_name} 的环境信息时出错: {str(e)}")
                continue
                
        return environment_info


    def _build_stimuli(self, env_info: Dict) -> List[str]:
        """构建环境刺激列表"""
        stimuli = []
        
        # 添加来自tile的刺激
        for tile in env_info['nearby_tiles']:
            if tile['events']:
                stimuli.extend([str(event) for event in tile['events']])
            if tile['item']:
                stimuli.append(f"看到物品: {tile['item']}")
            if tile['npc'] != '_':
                stimuli.append(f"看到NPC: {tile['npc']}")
        
        return stimuli

    def get_agent_actions(self) -> Dict[str, Any]:
        """
        获取所有Agent的行动决策
        
        Returns:
            Dict[str, Any]: 包含所有Agent行动的字典
            {
                "agent_name": {
                    "action": "action_type",
                    "target": target_info,
                    ...
                }
            }
        """
        actions = {}
        for agent_name, agent in self.agent_manager.agents.items():
            actions[agent_name] = {
                "action": agent.short_memory.short_memory[-1] if agent.short_memory.short_memory else None,
                "position": agent.basic_info.get('spawn_point', {})
            }
        return actions