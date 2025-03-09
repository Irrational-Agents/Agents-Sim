import unittest
import json
import os
import shutil
from unittest.mock import patch, mock_open
from agents_modules.agent import AgentManager, Agent
from config.meta_manager import MetaManager

class TestAgentManager(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        # 创建测试用的临时目录和文件
        self.test_base_path = "tests/"
        self.test_spawn_path = os.path.join(self.test_base_path, "spawn.json")
        
        # 创建测试用的spawn数据
        self.test_spawn_data = {
            "sakura_sato": {
                "spawn": {"x": 1, "y": 1},
                "next_spawn": {"x": 1, "y": 1}
            },
            "zhang_san": {
                "spawn": {"x": 2, "y": 2},
                "next_spawn": {"x": 2, "y": 2}
            }
        }
        
        # 创建测试用的basic_info数据
        self.test_basic_info = {
            "name": "sakura_sato",
            "age": 25,
            "personality": {
                "openness": 0.7,
                "conscientiousness": 0.8,
                "extraversion": 0.6,
                "agreeableness": 0.75,
                "neuroticism": 0.4
            }
        }
        
        # 创建测试目录结构

        
        # 写入测试数据
        with open(self.test_spawn_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_spawn_data, f, ensure_ascii=False, indent=4)
            
     
            
        # 创建测试用的short_term.json
        self.test_short_term = {
            "current_status": {
                "spawn": { "x": 73, "y": 14 },
                "action": 'move',
                "description": 'move to library',
                "location": 'library',
                "room": None
            },
            "short_term_goal_capacity": 3,
            "short_term_goal": [
            ],
            "short_memory_capacity": 30,
            "short_memory_for_plan": [],
            "short_memory": [],
            "basic_needs": {
                "fullness": 7,
                "social": 6,
                "fun": 5,
                "health": 8,
                "energy": 6
            },
            "temporary_personality_changes": {
                "openness": 0.2,
                "conscientiousness": 0.3,
                "extraversion": 0.1,
                "agreeableness": 0,
                "neuroticism": -0.1
            },
            "emotion": [0, 0, 1, 7, 0, 2, 0]
            }



        with open(os.path.join(self.test_base_path, "agents/sakura_sato/memory/short_term.json"), 'w', encoding='utf-8') as f:
            json.dump(self.test_short_term, f, ensure_ascii=False, indent=4)

        # 使用测试路径初始化AgentManager
        with patch('agents_modules.agent.SPAWN_FILE_PATH', self.test_spawn_path):
            with patch('agents_modules.agent.NPC_STORAGE_BASE_PATH', self.test_base_path):
                self.agent_manager = AgentManager()

    def tearDown(self):
        """测试后清理"""
        # 删除测试目录
        if os.path.exists(self.test_base_path):
            return
            shutil.rmtree(self.test_base_path)

    def test_load_agents(self):
        """测试加载agents"""
        # 验证agents是否正确加载
        self.assertIn("sakura_sato", self.agent_manager.agents)
        self.assertIn("zhang_san", self.agent_manager.agents)
        self.assertEqual(len(self.agent_manager.agents), 2)

    def test_create_agent(self):
        """测试创建agent"""
        # 测试创建已存在的agent
        agent = self.agent_manager.create_agent("sakura_sato")
        self.assertIsInstance(agent, Agent)
        self.assertEqual(agent.basic_info["name"], "Sakura Sato")
        
        # 测试创建不存在的agent
        agent = self.agent_manager.create_agent("Non Existent")
        self.assertIsNone(agent)

    def test_get_all_agents_positions(self):
        """测试获取所有agent位置"""
        positions = self.agent_manager.get_all_agents_positions()
        self.assertIn("sakura_sato", positions)
        self.assertEqual(positions["sakura_sato"], {"x": 73, "y": 14})

    def test_write_and_get_agent_status(self):
        """测试写入和获取agent状态"""
        new_status = {
            "spawn": {"x": 3, "y": 3},
            "action": "walking",
            "description": "walking to library"
        }
        
        # 写入新状态
        with patch('builtins.open', mock_open(read_data=json.dumps(self.test_short_term))):
            self.agent_manager.write_agent_status("sakura_sato", new_status)
        
        # 获取状态
        with patch('builtins.open', mock_open(read_data=json.dumps({"current_status": new_status}))):
            status = self.agent_manager.get_agent_current_status("sakura_sato")
            self.assertEqual(status, new_status)

    def test_get_agent_psychological_status(self):
        """测试获取agent心理状态"""
        status = self.agent_manager.get_agent_psychological_status("sakura_sato")
        self.assertIn("emotion", status)
        self.assertIn("basic_info", status)
        self.assertIn("memory", status)

    def test_erase_agent(self):
        """测试删除agent"""
        # 删除单个agent
        with patch('builtins.open', mock_open(read_data=json.dumps(self.test_spawn_data))):
            self.agent_manager.erase_agent("sakura_sato")
        
        self.assertNotIn("sakura_sato", self.agent_manager.agents)

    def test_erase_all_agents(self):
        """测试删除所有agent"""
        with patch('builtins.open', mock_open(read_data=json.dumps(self.test_spawn_data))):
            self.agent_manager.erase_all_agents()
        
        self.assertEqual(len(self.agent_manager.agents), 0)

if __name__ == '__main__':
    unittest.main() 