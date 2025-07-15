import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

def setup_logger(name: str) -> logging.Logger:
    """
    Настраивает и возвращает логгер с ротацией файлов.

    Конфигурация логгера теперь определяется переменными окружения
    с разумными значениями по умолчанию, что делает модуль независимым.
    """
    # Определяем корневую директорию проекта для корректного сохранения логов
    project_root = Path(__file__).parent.parent.parent
    
    # Получаем конфигурацию из переменных окружения или используем defaults
    log_dir_str = os.getenv("LOG_DIR", "logs")
    log_file_name = os.getenv("LOG_FILE", f"{name.replace('__', '')}.log")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Создаем директорию для логов
    log_dir = project_root / log_dir_str
    log_dir.mkdir(exist_ok=True)
    
    log_file_path = log_dir / log_file_name

    # Настраиваем логгер
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Очищаем существующие обработчики, чтобы избежать дублирования
    if logger.hasHandlers():
        logger.handlers.clear()

    # Форматтер для сообщений
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Обработчик для вывода в консоль
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)
    
    # Обработчик для записи в файл с ротацией
    file_handler = TimedRotatingFileHandler(
        log_file_path, when="midnight", backupCount=7, encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Добавляем обработчики к логгеру
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    
    return logger

# Создаем и экспортируем экземпляр логгера для использования в других модулях
logger = setup_logger(__name__)
