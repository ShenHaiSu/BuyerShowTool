"""日志工具模块"""
import logging
import os
from datetime import datetime


def setup_logger(target_dir: str = None) -> logging.Logger:
    """设置日志记录器"""
    logger = logging.getLogger('BuyerShowTool')
    logger.setLevel(logging.DEBUG)
    
    # 清除已有的处理器
    logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                        datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了目标目录）
    if target_dir:
        log_file = os.path.join(target_dir, 'error.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.ERROR)
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                         datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def log_error(logger: logging.Logger, message: str, error: Exception = None):
    """记录错误日志"""
    if error:
        logger.error(f"{message}: {str(error)}")
    else:
        logger.error(message)


def log_info(logger: logging.Logger, message: str):
    """记录信息日志"""
    logger.info(message)


def log_warning(logger: logging.Logger, message: str):
    """记录警告日志"""
    logger.warning(message)