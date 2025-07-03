"""Конфигурация базы данных.

Содержит настройки подключения и пути к файлам БД.
"""
import os
from pathlib import Path

# Путь к папке secrets в корне проекта
SECRETS_DIR = Path(__file__).resolve().parent.parent.parent / "secrets"
SECRETS_DIR.mkdir(exist_ok=True, parents=True)  # Создаем директорию при необходимости

# Путь к файлу БД по умолчанию
DEFAULT_DB_PATH = SECRETS_DIR / "users.db"

# Путь к тестовой базе данных SQLite
TEST_DB_PATH: str = "./test_db.sqlite3"
