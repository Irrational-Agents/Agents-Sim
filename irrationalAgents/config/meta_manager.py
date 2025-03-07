import os
import json
from datetime import datetime
from typing import Any, Optional
from dotenv import load_dotenv
from logger_config import setup_logger

logger = setup_logger('MetaManager')

class MetaManager:
    """
    元数据管理器，支持从环境变量和配置文件加载配置
    使用单例模式确保全局只有一个实例
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetaManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # 加载环境变量
        load_dotenv()
        
        self._meta_data = {}
        self._meta_file_path = os.getenv('META_FILE_PATH', 'storage/sample_data/meta.json')
        self._initialized = True
        self.reload()
        
    def reload(self) -> None:
        """重新加载元数据"""
        try:
            # 首先从文件加载基础配置
            self._load_from_file()
            
            # 然后用环境变量覆盖
            self._override_from_env()
            
            # 验证必要的字段
            self._validate_meta()
            
            logger.info("元数据重新加载成功")
            
        except Exception as e:
            logger.error(f"加载元数据时出错: {str(e)}")
            raise
            
    def _load_from_file(self) -> None:
        """从文件加载配置"""
        try:
            with open(self._meta_file_path, 'r', encoding='utf-8') as f:
                self._meta_data = json.load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件不存在: {self._meta_file_path}，使用默认值")
            self._meta_data = self._get_default_meta()
        except json.JSONDecodeError:
            logger.error(f"配置文件格式错误: {self._meta_file_path}")
            raise
            
    def _override_from_env(self) -> None:
        """从环境变量覆盖配置"""
        env_mappings = {
            'START_DATE': 'start_date',
            'CURR_TIME': 'curr_time',
            'TIME_STEP': 'time_step',
            'SIMULATION_SPEED': 'simulation_speed',
            'DEBUG_MODE': 'debug_mode'
        }
        
        for env_key, meta_key in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                # 特殊类型转换
                if meta_key in ['time_step', 'simulation_speed']:
                    env_value = int(env_value)
                elif meta_key == 'debug_mode':
                    env_value = env_value.lower() == 'true'
                    
                self._meta_data[meta_key] = env_value
                logger.info(f"从环境变量加载配置: {meta_key} = {env_value}")
                
    def _validate_meta(self) -> None:
        """验证元数据的必要字段"""
        required_fields = {
            'start_date': str,
            'curr_time': str,
            'time_step': int
        }
        
        for field, field_type in required_fields.items():
            if field not in self._meta_data:
                self._meta_data[field] = self._get_default_meta()[field]
                logger.warning(f"使用默认值: {field} = {self._meta_data[field]}")
            else:
                # 确保类型正确
                try:
                    self._meta_data[field] = field_type(self._meta_data[field])
                except ValueError:
                    logger.error(f"字段类型错误: {field}")
                    raise
                    
    def _get_default_meta(self) -> dict:
        """获取默认元数据"""
        return {
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'curr_time': '08:00',
            'time_step': 15,
            'simulation_speed': 1,
            'debug_mode': False
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._meta_data.get(key, default)
        
    def get_datetime(self) -> datetime:
        """获取当前日期时间"""
        try:
            return datetime.strptime(
                f"{self.get('start_date')} {self.get('curr_time')}", 
                "%Y-%m-%d %H:%M"
            )
        except ValueError as e:
            logger.error(f"日期时间格式错误: {e}")
            raise
            
    def get_time_step(self) -> int:
        """获取时间步长（分钟）"""
        return self.get('time_step', 15)
        
    def get_all(self) -> dict:
        """获取所有元数据"""
        return self._meta_data.copy() 