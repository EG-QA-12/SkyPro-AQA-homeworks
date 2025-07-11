import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

# Add project root to sys.path for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.config import config as Config


def setup_logger(name):
    """Настраивает и возвращает логгер."""
    log_file = Config.LOG_FILE
    log_level = Config.LOG_LEVEL
    log_dir = Config.LOG_DIR
    
    # Создаём директорию логов если её нет
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Также создаём директорию для файла логов если она отличается
    log_file_dir = os.path.dirname(log_file)
    if log_file_dir and log_file_dir != str(log_dir):
        os.makedirs(log_file_dir, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(log_level.upper())
    if logger.hasHandlers():
        logger.handlers.clear()
    ch = logging.StreamHandler()
    ch.setLevel(log_level.upper())
    fh = TimedRotatingFileHandler(log_file, when="midnight", backupCount=7, encoding='utf-8')
    fh.setLevel(log_level.upper())
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


# Создаем и экспортируем экземпляр логгера
logger = setup_logger(__name__)
