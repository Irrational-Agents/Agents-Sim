import os
from typing import Any

LOG_LEVEL = 'DEBUG'

# Websocket Configuration
SOCKET_URL = "https://orange-cliff-0b3a9151e.5.azurestaticapps.net:8080"
WORK_DIR = '$PATH/irrationalAgents'

# langchain configuration
LANGCHAIN_TRACING_V2 = "true"
LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com"
LANGCHAIN_PROJECT = "IrationalAgents"
LANGCHAIN_API_KEY = "xxx"
OPENAI_API_KEY = "xxx"

# Action configuration
AVAILABLE_ACTIONS = ["moving", "interacting", "thinking", "sleeping"]
ACTION_COOLDOWN = 5

# Planning configuration
MAX_PLAN_STEPS = 10
PLAN_HORIZON = 24

# Personality traits
PERSONALITY_DIMENSIONS = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
TRAIT_RANGE_MIN = 0
TRAIT_RANGE_MAX = 100

# Emotion configuration
EMOTION_TYPES = ["happy", "sad", "angry", "afraid", "disgusted", "surprised", "neutral"]
EMOTION_INTENSITY_MIN = 0
EMOTION_INTENSITY_MAX = 10

# Growth configuration
GROWTH_RATE = 0.01
MAX_GROWTH_PER_CYCLE = 0.1

# Memory configuration
MEMORY_IMPORTANCE_THRESHOLD = 0.5
MEMORY_DECAY_RATE = 0.99

# Perception configuration
PERCEPTION_RANGE = 2


def load_config_to_env():
    """
    加载配置，优先使用环境变量中的值
    """
    # 获取所有配置项
    config_items = {
        name: value for name, value in globals().items()
        if not name.startswith('_') and name.isupper()
    }
    # 处理每个配置项
    for name, default_value in config_items.items():
        env_name = name.upper()
        
        # 如果环境变量存在，使用环境变量的值
        if env_name in os.environ:
            env_value = os.environ[env_name]
            globals()[name] = _convert_value(env_value, default_value)
        else:
            # 环境变量不存在，使用默认值
            os.environ[env_name] = _convert_to_env_value(default_value)
                

def _convert_value(env_value: str, default_value: Any) -> Any:
    """
    将环境变量值转换为适当的类型
    """
    try:
        if isinstance(default_value, bool):
            return env_value.lower() == 'true'
        elif isinstance(default_value, int):
            return int(env_value)
        elif isinstance(default_value, float):
            return float(env_value)
        elif isinstance(default_value, (list, tuple)):
            return env_value.split(',')
        else:
            return env_value
    except (ValueError, TypeError):
        return default_value

def _convert_to_env_value(value: Any) -> str:
    """
    将值转换为环境变量格式
    """
    if isinstance(value, (list, tuple)):
        return ','.join(map(str, value))
    elif isinstance(value, bool):
        return str(value).lower()
    else:
        return str(value)

def get_config(key: str, default: Any = None) -> Any:
    """
    获取配置值，优先使用环境变量
    """
    try:
        env_name = key.upper()
        # 如果环境变量存在，使用环境变量的值
        if env_name in os.environ:
            env_value = os.environ[env_name]
            return _convert_value(env_value, globals().get(key, default))
        
        # 如果环境变量不存在，返回配置文件中的值或默认值
        return globals().get(key, default)
            
    except Exception as e:
        return default

load_config_to_env()

META_FILE_PATH = os.path.join(WORK_DIR, "../storage/meta.data")
SPAWN_FILE_PATH = os.path.join(WORK_DIR, "../storage/sample_data/spawn.json")
NPC_STORAGE_BASE_PATH = os.path.join(WORK_DIR, "../storage/sample_data")