"""Менеджер базы данных SQLite.

Обеспечивает работу с пользователями, ролями и куками для автоматизации тестирования.
"""
import sqlite3
from typing import Dict, Optional, Any, List
from pathlib import Path
from datetime import datetime
# Единый путь к БД определён в config.db_settings
from config.db_settings import DEFAULT_DB_PATH

class DatabaseManager:
    """
    Класс для управления базой данных пользователей и их куками.

    Позволяет создавать таблицы, добавлять пользователей, получать их данные, обновлять куки и фильтровать по ролям/подпискам.
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
            role TEXT NOT NULL,
            subscription TEXT NOT NULL,
            cookie_file TEXT,
            last_cookie_update TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
        """)
        self.conn.commit()

    def add_or_update_user(self, login: str, role: str, subscription: str, cookie_file: str = None) -> int:
        """
        Добавляет нового пользователя или обновляет существующего по логину.
        Если пользователь уже есть — обновляет роль, подписку и путь к куке.

        Args:
            login (str): Логин пользователя.
            role (str): Роль пользователя.
            subscription (str): Тип подписки.
            cookie_file (str): Путь к cookie-файлу (опционально).

        Returns:
            int: ID пользователя.
        """
        cursor = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO users (login, role, subscription, cookie_file, last_cookie_update, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(login) DO UPDATE SET
                role=excluded.role,
                subscription=excluded.subscription,
                cookie_file=excluded.cookie_file,
                last_cookie_update=excluded.last_cookie_update,
                is_active=1
        """, (login, role, subscription, cookie_file, now))
        self.conn.commit()
        cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
        row = cursor.fetchone()
        return row[0] if row else -1

    def update_cookie_file(self, login: str, cookie_file: str) -> None:
        """
        Обновляет путь к cookie-файлу и дату обновления для пользователя.
        """
        cursor = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            UPDATE users SET cookie_file = ?, last_cookie_update = ? WHERE login = ?
        """, (cookie_file, now, login))
        self.conn.commit()

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
            SELECT id, login, role, subscription, cookie_file, last_cookie_update, is_active
            FROM users WHERE login = ?
        """, (login,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "login": row[1],
                "role": row[2],
                "subscription": row[3],
                "cookie_file": row[4],
                "last_cookie_update": row[5],
                "is_active": bool(row[6])
            }
        return None

    def get_users_by_role(self, role: str) -> List[Dict[str, Any]]:
        """
        Возвращает список пользователей по роли.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, login, role, subscription, cookie_file, last_cookie_update, is_active
            FROM users WHERE role = ? AND is_active = 1
        """, (role,))
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "login": row[1],
                "role": row[2],
                "subscription": row[3],
                "cookie_file": row[4],
                "last_cookie_update": row[5],
                "is_active": bool(row[6])
            }
            for row in rows
        ]

    def get_users_by_subscription(self, subscription: str) -> List[Dict[str, Any]]:
        """
        Возвращает список пользователей по уровню подписки.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, login, role, subscription, cookie_file, last_cookie_update, is_active
            FROM users WHERE subscription = ? AND is_active = 1
        """, (subscription,))
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "login": row[1],
                "role": row[2],
                "subscription": row[3],
                "cookie_file": row[4],
                "last_cookie_update": row[5],
                "is_active": bool(row[6])
            }
            for row in rows
        ]

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
