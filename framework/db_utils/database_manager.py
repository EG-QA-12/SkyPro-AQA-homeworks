"""Менеджер базы данных SQLite.

Обеспечивает работу с пользователями и сессиями.
"""
import sqlite3
from typing import Dict, Optional, Any
from pathlib import Path
# Используем единый конфигурационный модуль для пути к базе данных
from config.db_settings import DEFAULT_DB_PATH

class DatabaseManager:
    """
    Класс для управления базой данных пользователей.

    Позволяет создавать таблицы, добавлять пользователей, получать их данные и управлять сессией БД.
    Использует SQLite для хранения информации о пользователях.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        """
        Инициализирует подключение к БД.
        
        Args:
            db_path (Optional[str]): Путь к файлу базы данных. Если не указан, используется путь по умолчанию.
        """
        self.db_path: Path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: sqlite3.Connection = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self) -> None:
        """
        Создает необходимые таблицы в БД, если их ещё нет.

        Returns:
            None
        """
        cursor = self.conn.cursor()
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
        """
        Добавляет нового пользователя в БД.
        
        Args:
            login (str): Логин пользователя (email).
            password (str): Пароль в открытом виде.
            role (str): Роль пользователя (по умолчанию 'user').
            subscription (str): Тип подписки (по умолчанию 'basic').
        
        Returns:
            int: ID созданного пользователя.
        
        Raises:
            sqlite3.IntegrityError: Если пользователь с таким логином уже существует.
        
        Example:
            >>> db = DatabaseManager()
            >>> user_id = db.add_user('test@example.com', 'password123')
        """
        from .security import hash_password
        hashed_pw: str = hash_password(password)
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

    def get_user(self, login: str) -> Optional[Dict[str, Any]]:
        """
        Возвращает данные пользователя по логину.
        
        Args:
            login (str): Логин пользователя.
        
        Returns:
            Optional[Dict[str, Any]]: Словарь с данными пользователя или None, если не найден.
        
        Example:
            >>> db = DatabaseManager()
            >>> user = db.get_user('test@example.com')
            >>> print(user['role'])
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

    def close(self) -> None:
        """
        Закрывает соединение с БД.

        Returns:
            None
        """
        self.conn.close()

    def __enter__(self) -> 'DatabaseManager':
        """
        Позволяет использовать DatabaseManager в контексте with.

        Returns:
            DatabaseManager: Сам экземпляр класса.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Гарантирует закрытие соединения при выходе из контекста.

        Args:
            exc_type: Тип исключения.
            exc_val: Значение исключения.
            exc_tb: Трассировка стека.
        """
        self.close()
