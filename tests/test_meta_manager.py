import unittest
import os
import json
from datetime import datetime
from irrationalAgents.config.meta_manager import MetaManager

class TestMetaManager(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        # 创建测试用的meta文件
        self.test_meta_path = 'test_meta.data'
        self.test_meta_data = {
            'start_date': '2024-03-06',
            'curr_date': '2024-03-06',
            'curr_time': '08:00',
            'start_time': '08:00',
            'time_step': 15,
            'simulation_speed': 1,
            'debug_mode': False,
            'step': 0
        }
        
        # 写入测试数据
        with open(self.test_meta_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_meta_data, f, ensure_ascii=False, indent=4)
            
        # 设置环境变量
        os.environ['META_FILE_PATH'] = self.test_meta_path
        os.environ['START_DATE'] = '2024-03-07'
        os.environ['CURR_TIME'] = '09:00'
        
        # 创建MetaManager实例
        self.meta_manager = MetaManager()

    def tearDown(self):
        """测试后清理"""
        # 删除测试文件
        if os.path.exists(self.test_meta_path):
            os.remove(self.test_meta_path)
        
        # 清除环境变量
        for key in ['META_FILE_PATH', 'START_DATE', 'CURR_TIME']:
            if key in os.environ:
                del os.environ[key]

    def test_singleton(self):
        """测试单例模式"""
        manager1 = MetaManager()
        manager2 = MetaManager()
        self.assertIs(manager1, manager2)

    def test_load_from_file(self):
        """测试从文件加载配置"""
        self.meta_manager.reload()
        self.assertEqual(self.meta_manager.get('curr_time'), '09:00')  # 应该被环境变量覆盖
        self.assertEqual(self.meta_manager.get('time_step'), 15)

    def test_override_from_env(self):
        """测试环境变量覆盖"""
        os.environ['TIME_STEP'] = '30'
        self.meta_manager.reload()
        self.assertEqual(self.meta_manager.get('time_step'), 30)

    def test_datetime_operations(self):
        """测试日期时间操作"""
        # 测试获取当前时间
        current_dt = self.meta_manager.get_datetime()
        self.assertIsInstance(current_dt, datetime)
        
        # 测试设置当前时间
        self.meta_manager.set_curr_datetime('2024-03-08', '10:00')
        self.assertEqual(self.meta_manager.get('curr_date'), '2024-03-08')
        self.assertEqual(self.meta_manager.get('curr_time'), '10:00')

    def test_step_operations(self):
        """测试步数操作"""
        # 测试设置步数
        self.meta_manager.set_step(5)
        self.assertEqual(self.meta_manager.get('step'), 5)

    def test_write_meta(self):
        """测试写入元数据"""
        # 修改一些值
        self.meta_manager.set_curr_datetime('2024-03-08', '10:00')
        self.meta_manager.set_step(5)
        
        # 写入文件
        self.meta_manager.write_meta()
        
        # 重新读取验证
        with open(self.test_meta_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data['curr_date'], '2024-03-08')
            self.assertEqual(data['curr_time'], '10:00')
            self.assertEqual(data['step'], 5)


if __name__ == '__main__':
    unittest.main() 