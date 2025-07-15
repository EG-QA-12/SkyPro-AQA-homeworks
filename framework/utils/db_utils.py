"""
Модуль для работы с базой данных пользователей.
Объединяет функционал database_manager.py и db_config.py.
"""
from __future__ import annotations

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from config.secrets_manager import SecretsManager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Менеджер для работы с базой данных пользователей."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Инициализация менеджера БД.
        
        Args:
            db_path: Путь к БД. Если не указан, используется users.db из secrets.
        """
        if db_path is None:
            # Используем стандартный путь к БД в secrets
            project_root = Path(__file__).resolve().parents[2]
            self.db_path = project_root / "secrets" / "users.db"
        else:
            self.db_path = Path(db_path)
        
        # Создаем директорию если не существует
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
    
    def _init_database(self) -> None:
        """Инициализация структуры БД."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    login TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    subscription TEXT DEFAULT 'basic',
                    cookie_file TEXT,
                    last_cookie_update TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass
    
    def execute_query(self, query: str, params: tuple = (), fetch: bool = False) -> Any:
        """Выполнение SQL-запроса.
        
        Args:
            query: SQL-запрос
            params: Параметры запроса
            fetch: Нужно ли возвращать результат
            
        Returns:
            Результат запроса если fetch=True
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch:
                return cursor.fetchall()
            
            conn.commit()
            return cursor.rowcount
    
    def get_user(self, login: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по логину."""
        result = self.execute_query(
            "SELECT id, login, role, subscription, cookie_file, last_cookie_update, is_active "
            "FROM users WHERE login = ?",
            (login,),
            fetch=True
        )
        
        if result:
            row = result[0]
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
        """Получение пользователей по роли."""
        query = """
            SELECT id, login, role, subscription, cookie_file, last_cookie_update, is_active 
            FROM users 
        """
        params = ()
        
        if role != "%":
            query += "WHERE role LIKE ?"
            params = (f"%{role}%",)
            
        results = self.execute_query(query, params, fetch=True)
        
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
            for row in results
        ]
    
    def add_or_update_user(self, login: str, role: str = "user", 
                          subscription: str = "basic", cookie_file: str = None,
                          password_hash: str = "placeholder") -> None:
        """Добавляет или обновляет пользователя в БД.
        
        Args:
            login: Логин пользователя
            role: Роль пользователя
            subscription: Подписка пользователя  
            cookie_file: Путь к файлу куки
            password_hash: Хеш пароля (placeholder для совместимости)
        """
        # Проверяем, существует ли пользователь
        existing_user = self.get_user(login)
        
        if existing_user:
            # Обновляем существующего пользователя
            self.execute_query(
                """UPDATE users 
                   SET role = ?, subscription = ?, cookie_file = ?, 
                       last_cookie_update = CURRENT_TIMESTAMP
                   WHERE login = ?""",
                (role, subscription, cookie_file, login)
            )
        else:
            # Добавляем нового пользователя
            self.execute_query(
                """INSERT INTO users (login, password_hash, role, subscription, cookie_file, last_cookie_update)
                   VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (login, password_hash, role, subscription, cookie_file)
            ) 