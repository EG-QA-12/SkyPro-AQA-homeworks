"""Модуль для подключения к базе данных."""

from typing import Optional
from .teacher_table import TeacherTable
from config.db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def get_db_connection(connection_string: Optional[str] = None) -> TeacherTable:
    """
    Создать подключение к базе данных.
    
    Args:
        connection_string (Optional[str]): Строка подключения к БД.
            Если не указана, используется конфигурация по умолчанию.
            
    Returns:
        TeacherTable: Экземпляр класса для работы с таблицей учителей
    """
    if not connection_string:
        connection_string = (
            f"postgresql://{DB_USER}:{DB_PASSWORD}@"
            f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    return TeacherTable(connection_string)
