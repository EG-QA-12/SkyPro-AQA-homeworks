"""
Модуль централизованного логирования для всего проекта.

Этот модуль предоставляет единый интерфейс для логирования,
который должен использоваться всеми компонентами проекта.
Цель - обеспечить единообразный формат логов и централизованное
управление настройками логирования.

Основные функции:
- setup_logger() - настройка корневого логгера
- get_logger() - получение логгера с именем модуля
- clear_handlers() - очистка существующих обработчиков
"""

import logging
import sys
from pathlib import Path

# Константы
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_LOG_LEVEL = logging.INFO


def setup_logger(
    log_level: int = DEFAULT_LOG_LEVEL,
    log_file: str = None,
    clear_existing: bool = True
) -> logging.Logger:
    """
    Настраивает корневой логгер проекта.
    
    Args:
        log_level: Уровень логирования (по умолчанию INFO)
        log_file: Путь к файлу логов (если None - только консоль)
        clear_existing: Очистить существующие обработчики
        
    Returns:
        Корневой логгер проекта
    """
    # Получаем корневой логгер
    logger = logging.getLogger()
    
    # Очищаем существующие обработчики если нужно
    if clear_existing:
        clear_handlers(logger)
    
    # Устанавливаем уровень логирования
    logger.setLevel(log_level)
    
    # Создаем форматтер
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Добавляем консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Добавляем файловый обработчик если указан путь
    if log_file:
        # Создаем директорию если не существует
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Добавляем информацию о настройке
    logger.info(
        f"Логирование настроено на уровне: {logging.getLevelName(log_level)}"
    )
    if log_file:
        logger.info(f"Логи сохраняются в: {log_file}")
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Возвращает логгер с указанным именем.
    
    Args:
        name: Имя логгера (обычно __name__ модуля)
        
    Returns:
        Настроенный логгер
    """
    return logging.getLogger(name)


def clear_handlers(logger: logging.Logger) -> None:
    """
    Очищает все обработчики у логгера.
    
    Args:
        logger: Логгер для очистки
    """
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()


# Инициализация при импорте
if not logging.getLogger().handlers:
    setup_logger()
