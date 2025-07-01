"""Менеджер базы данных SQLite.

Обеспечивает работу с пользователями и сессиями.
"""
import sqlite3
from typing import Dict, Optional
from pathlib import Path
from . import db_config  # Импортируем модуль конфигурации

class DatabaseManager:
    """Класс для управления базой данных пользователей."""

    def __init__(self, db_path: str = None):
        """Инициализирует подключение к БД.
        
        Args:
            db_path: Путь к файлу базы данных. Если не указан, используется путь по умолчанию.
        """
        # Если путь не передан, используем путь по умолчанию из конфигурации
        self.db_path = Path(db_path) if db_path else db_config.DEFAULT_DB_PATH
        # Убедимся, что родительская директория существует
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        """Создает необходимые таблицы в БД."""
        cursor = self.conn.cursor()
        # Основная таблица пользователей
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            subscription TEXT NOT NULL DEFAULT 'basic',
            cookie_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
        """)
        self.conn.commit()

    def add_user(self, login: str, password: str, role: str = "user", 
                subscription: str = "basic") -> int:
        """Добавляет нового пользователя в БД.
        
        Args:
            login: Логин пользователя (email).
            password: Пароль в открытом виде.
            role: Роль пользователя.
            subscription: Тип подписки.
            
        Returns:
            ID созданного пользователя.
        """
        from .security import hash_password
        hashed_pw = hash_password(password)
        
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (login, password, password_hash, role, subscription)
            VALUES (?, ?, ?, ?, ?)
            """,
            (login, password, hashed_pw, role, subscription)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_user(self, login: str) -> Optional[Dict]:
        """Возвращает данные пользователя по логину.
        
        Args:
            login: Логин пользователя.
            
        Returns:
            Словарь с данными пользователя или None, если не найден.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, login, password, password_hash, role, subscription, cookie_file
            FROM users 
            WHERE login = ?
        """, (login,))
        
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "login": row[1],
                "password": row[2],
                "password_hash": row[3],
                "role": row[4],
                "subscription": row[5],
                "cookie_file": row[6]
            }
        return None

    def close(self):
        """Закрывает соединение с БД."""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
