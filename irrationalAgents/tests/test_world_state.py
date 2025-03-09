import unittest
import asyncio
from datetime import datetime
from typing import Dict
from unittest.mock import Mock, patch

from unity_modules.world import WorldState
from unity_modules.map import Map
from agents_modules.agent import AgentManager
from config.meta_manager import MetaManager

class TestWorldState(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        # 创建测试用的地图数据
        self.map_data = {
            "mapMeta": {
                "maze_width": 10,
                "maze_height": 10,
                "sq_tile_size": 1
            },
            "mapData": {
                "collision_maze": [[0] * 10 for _ in range(10)],
                "sector_maze": [[0] * 10 for _ in range(10)],
                "arena_maze": [[0] * 10 for _ in range(10)],
                "game_object_maze": [[0] * 10 for _ in range(10)],
                "spawning_location_maze": [[0] * 10 for _ in range(10)]
            },
            "blockData": {}
        }
        
        # 创建WorldState实例
        self.world = WorldState(self.map_data)
        
        # 模拟NPC位置数据
        self.npc_positions = {
            "Sakura Sato": {"x": 1, "y": 1},
            "Zhang San": {"x": 2, "y": 2}
        }

    async def test_update_agent_positions(self):
        """测试更新Agent位置"""
        # 更新位置
        self.world.update_agent_positions(self.npc_positions)
        
        # 验证地图上的NPC位置
        self.assertEqual(self.world.map.tiles[1][1]['npc'], "Sakura Sato")
        self.assertEqual(self.world.map.tiles[2][2]['npc'], "Zhang San")
        
        # 验证Agent管理器中的位置
        for npc_name, pos in self.npc_positions.items():
            if npc_name in self.world.agent_manager.agents:
                agent_pos = self.world.agent_manager.agents[npc_name].short_memory.current_status['spawn']
                self.assertEqual(agent_pos, pos)

    async def test_collect_env_info(self):
        """测试收集环境信息"""
        # 先更新位置
        self.world.update_agent_positions(self.npc_positions)
        
        # 收集环境信息
        env_info = self.world._collect_env_info()
        
        # 验证环境信息
        self.assertIn("Sakura Sato", env_info)
        self.assertIn("Zhang San", env_info)
        self.assertIn("nearby_tiles", env_info["Sakura Sato"])
        self.assertIn("nearby_tiles", env_info["Zhang San"])

    async def test_build_stimuli(self):
        """测试构建刺激信息"""
        # 创建测试环境信息
        env_info = {
            "nearby_tiles": [
                {
                    "events": ["event1", "event2"],
                    "item": "book",
                    "npc": "Zhang San"
                }
            ]
        }
        
        # 构建刺激
        stimuli = self.world._build_stimuli(env_info)
        
        # 验证刺激信息
        self.assertIn("event1", stimuli[0])
        self.assertIn("event2", stimuli[1])
        self.assertIn("book", stimuli[2])
        self.assertIn("Zhang San", stimuli[3])

    async def test_tick_world(self):
        """测试世界更新"""
        # 更新位置
        self.world.update_agent_positions(self.npc_positions)
        
        # 执行世界更新
        await self.world.tick_world()
        
        # 验证时间更新
        self.assertIsNotNone(self.world.global_time)
        self.assertEqual(self.world.meta_manager.get('step'), 1)

    async def test_gen_npc_current_status(self):
        """测试生成NPC当前状态"""
        agent_name = "Sakura Sato"
        action = "move"
        move_description = "walking to library"
        
        # 确保agent存在
        if agent_name in self.world.agent_manager.agents:
            # 生成状态
            status = self.world.gen_npc_current_status(
                agent_name, 
                action, 
                move_description
            )
            
            # 验证状态
            self.assertEqual(status['action'], action)
            self.assertEqual(status['description'], move_description)
            self.assertIn('spawn', status)

    @patch('irrationalAgents.unity_modules.map.Map')
    @patch('irrationalAgents.agents_modules.agent.AgentManager')
    def test_with_mocks(self, mock_map, mock_agent_manager):
        # 使用mock对象进行测试
        pass

def run_async_test(test_case):
    """运行异步测试的辅助函数"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_case)

if __name__ == '__main__':
    # 运行所有测试
    unittest.main() 