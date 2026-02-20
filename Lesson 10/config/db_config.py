"""Конфигурация базы данных."""

import os
from typing import Optional

# Загрузка переменных окружения из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_env_var(key: str, default: Optional[str] = None) -> str:
    """
    Получить значение переменной окружения.
    
    Args:
        key (str): Имя переменной окружения
        default (Optional[str]): Значение по умолчанию
        
    Returns:
        str: Значение переменной окружения или default
        
    Raises:
        ValueError: Если переменная не найдена и нет значения по умолчанию
    """
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Переменная окружения {key} не установлена")
    return value


# Параметры подключения к PostgreSQL из переменных окружения
DB_HOST = get_env_var("DB_HOST", "localhost")
DB_PORT = int(get_env_var("DB_PORT", "5432"))
DB_NAME = get_env_var("DB_NAME", "postgres")
DB_USER = get_env_var("DB_USER", "postgres")
DB_PASSWORD = get_env_var("DB_PASSWORD", "")
