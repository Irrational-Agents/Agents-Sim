import logging
import os
import json
from pprint import pformat
from logging.handlers import RotatingFileHandler
from config.config import LOG_LEVEL

def convert_log_level(level: str, to_format: str = 'standard') -> str:
    # 标准日志级别映射
    level_mapping = {
        'DEBUG': 'debug',
        'INFO': 'info',
        'WARNING': 'warning',
        'ERROR': 'error',
        'CRITICAL': 'critical'
    }
    
    # 统一转换为大写以便查找
    level = level.upper()
    
    if to_format == 'uvicorn':
        return level_mapping.get(level, 'info')  # 默认返回 'info'
    else:  # standard format (大写)
        return level
class TruncateMessageFilter(logging.Filter):
    # TL, DR
    def filter(self, record):
        if len(record.msg) > 500:
            record.msg = record.msg[:500] + '...'
        return True
    
class DictFormatterFilter(logging.Filter):
    def filter(self, record):
        # 检查 args 中是否有字典或列表需要格式化
        if record.args:
            args = list(record.args)
            for i, arg in enumerate(args):
                if isinstance(arg, (dict, list)):
                    args[i] = f"\n{pformat(arg)}"
            record.args = tuple(args)
        return True

def setup_logger(name):
    # 创建logger
    logger = logging.getLogger(name)
    # 禁用继承
    logger.propagate = False
    logger.setLevel(convert_log_level(LOG_LEVEL))
    
    # 如果logger已经有handlers,不再添加，避免重复
    if logger.handlers:
        return logger
    
    # 修改formatter，添加文件名、函数名和行号
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # 添加我们的自定义过滤器
    dict_formatter = DictFormatterFilter()
    truncate_filter = TruncateMessageFilter()
    
    # 创建并配置 console handler
    console_handler = logging.StreamHandler()
    #console_handler.setLevel(logging.INFO)
    console_handler.setLevel(convert_log_level(LOG_LEVEL))
    console_handler.setFormatter(formatter)
    console_handler.addFilter(dict_formatter)  # 添加过滤器
    console_handler.addFilter(truncate_filter)
    logger.addHandler(console_handler)
    
    # 创建并配置 file handler
    try:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        file_handler = RotatingFileHandler(
            f'logs/{name}.log',
            maxBytes=1024*1024,  # 1MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(dict_formatter)  # 添加过滤器
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Error setting up file handler: {e}")
    
    return logger