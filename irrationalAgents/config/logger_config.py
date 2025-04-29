import logging
import os
import json
from pprint import pformat
from logging.handlers import RotatingFileHandler
from config.config import LOG_LEVEL
import colorama 

colorama.init()
class Colors:
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'

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

class ColoredFormatter(logging.Formatter):
    """自定义带颜色的日志格式化器"""
    
    COLORS = {
        'DEBUG': Colors.BLUE,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.MAGENTA,
    }
    
    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            levelname_color = f"{self.COLORS[levelname]}{levelname}{Colors.RESET}"
            record.levelname = levelname_color
        return super().format(record)

class TruncateMessageFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'original_msg'):
            record.original_msg = record.msg  # 保存原始信息
            if isinstance(record.msg, str) and len(record.msg) > 500:
                record.msg = record.msg[:500] + '...'
        return True

class RestoreMessageFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'original_msg'):
            record.msg = record.original_msg  # 还原信息
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
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(convert_log_level(LOG_LEVEL))
    
    if logger.handlers:
        return logger
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    colored_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    dict_formatter = DictFormatterFilter()
    truncate_filter = TruncateMessageFilter()
    restore_filter = RestoreMessageFilter()
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(convert_log_level(LOG_LEVEL))
    console_handler.setFormatter(colored_formatter)
    console_handler.addFilter(dict_formatter)
    console_handler.addFilter(truncate_filter)  # 只在 console 截断
    logger.addHandler(console_handler)
    
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
        file_handler.setFormatter(file_formatter)  # 使用普通格式器
        file_handler.addFilter(dict_formatter)
        file_handler.addFilter(restore_filter)  # 在 file 恢复
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Error setting up file handler: {e}")
    return logger