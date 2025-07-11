"""
Модуль для работы с базой данных SQLite.

Обеспечивает взаимодействие с базой данных пользователей,
инициализацию схемы и миграции.
"""

import os
import sqlite3
import logging
from pathlib import Path

# Каталог auth_project
BASE_DIR = Path(__file__).resolve().parent.parent
# Единый каталог для пользовательских данных
USER_DATA_DIR = BASE_DIR / "user_data"
USER_DATA_DIR.mkdir(exist_ok=True)
import bcrypt
from typing import Dict, List, Optional, Tuple, Any, Union

from src.config import config


class DatabaseManager:
    """
    Класс для управления базой данных пользователей и сессий.
    
    Предоставляет методы для инициализации БД, выполнения запросов,
    работы с пользователями и сессиями.
    """
    
    def __init__(self, db_path: str = None):
        """
        Инициализирует DatabaseManager. Создаёт директорию и инициализирует базу данных.

        Args:
            db_path: Путь к базе данных (по умолчанию user_data/users.db)
        """
        if db_path is None:
            self.db_path = str(USER_DATA_DIR / "users.db")
        else:
            self.db_path = db_path
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self._init_db()
    
    def _init_db(self) -> None:
        """
        Инициализирует базу данных и выполняет миграции.
        
        Создаёт таблицу users, если она не существует.
        Добавляет новые столбцы, если они отсутствуют.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Создаем таблицу пользователей, если она не существует
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            subscription INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cookie TEXT,
            cookie_expiration TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()

    def execute_query(
        self, query: str, params: Tuple = (), fetch: bool = False
    ) -> Union[List[Tuple[Any, ...]], None]:
        """
        Выполняет SQL запрос к базе данных.

        Args:
            query: SQL запрос
            params: Параметры запроса
            fetch: Нужно ли возвращать результат

        Returns:
            Результат запроса или None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        result = None
        if fetch:
            result = cursor.fetchall()
        
        conn.commit()
        conn.close()
        return result
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о пользователе по имени пользователя.

        Args:
            username: Имя пользователя

        Returns:
            Словарь с данными пользователя или None, если пользователь не найден
        """
        query = "SELECT id, username, password_hash, role, subscription, cookie, cookie_expiration FROM users WHERE username = ?"
        result = self.execute_query(query, (username,), fetch=True)
        
        if not result:
            return None
        
        user = {
            "id": result[0][0],
            "username": result[0][1],
            "password_hash": result[0][2],
            "role": result[0][3],
            "subscription": result[0][4],
            "cookie": result[0][5],
            "cookie_expiration": result[0][6]
        }
        
        return user
    
    def verify_password(self, username: str, password: str) -> bool:
        """
        Проверяет корректность пароля пользователя.

        Args:
            username: Имя пользователя
            password: Пароль для проверки

        Returns:
            True, если пароль верный, иначе False
        """
        user = self.get_user_by_username(username)
        if not user:
            return False
        
        hashed = user["password_hash"]
        if isinstance(hashed, str):
            hashed = hashed.encode('utf-8')
        
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def save_user_cookies(self, username: str, cookies: str, expiration: str = None) -> bool:
        """
        Сохраняет куки пользователя в базе данных.

        Args:
            username: Имя пользователя
            cookies: Куки для сохранения (в JSON формате)
            expiration: Время истечения кук

        Returns:
            True, если сохранение успешно, иначе False
        """
        try:
            query = "UPDATE users SET cookie = ?, cookie_expiration = ? WHERE username = ?"
            self.execute_query(query, (cookies, expiration, username))
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении кук для пользователя {username}: {e}")
            return False
            
    def get_user_cookies(self, username: str) -> Optional[str]:
        """
        Получает сохранённые куки пользователя.

        Args:
            username: Имя пользователя

        Returns:
            Сохранённые куки пользователя или None, если они не найдены
        """
        user = self.get_user_by_username(username)
        if user and user.get("cookie"):
            return user["cookie"]
        return None
        
    def delete_user(self, username: str) -> bool:
        """
        Удаляет пользователя из базы данных.
        
        Args:
            username: Имя пользователя для удаления
            
        Returns:
            True при успешном удалении, False если пользователь не найден или при ошибке
        """
        try:
            # Проверяем существует ли пользователь
            if not self.get_user_by_username(username):
                self.logger.warning(f"Пользователь {username} не найден в базе данных")
                return False
                
            # Удаляем пользователя
            self.execute_query("DELETE FROM users WHERE username = ?", (username,))
            self.logger.info(f"Пользователь {username} успешно удален")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при удалении пользователя {username}: {e}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """
        Хеширует пароль пользователя.

        Args:
            password: Пароль для хеширования

        Returns:
            Хешированный пароль
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def create_user(self, username: str, password: str, role: str = "user", subscription: int = None) -> bool:
        """
        Создает нового пользователя в базе данных или обновляет существующего.

        Args:
            username: Имя пользователя
            password: Пароль пользователя
            role: Роль пользователя (по умолчанию "user")
            subscription: Тип подписки: 1 - малое, 2 - среднее, 3 - крупное предприятие

        Returns:
            True при успешном создании/обновлении, иначе False
        """
        password_hash = self._hash_password(password)
        
        # Автоматически устанавливаем максимальную подписку для admin и moderator
        if role in ("admin", "moderator"):
            subscription = 3
        # Если подписка не указана, ставим минимальную
        if subscription is None:
            subscription = 1
        
        # Проверяем, существует ли пользователь
        existing_user = self.get_user_by_username(username)
        
        try:
            if existing_user:
                # Обновляем существующего пользователя
                self.logger.info(f"Обновление данных пользователя {username} (роль: {role}, подписка: {subscription})")
                self.execute_query(
                    "UPDATE users SET password_hash = ?, role = ?, subscription = ? WHERE username = ?",
                    (password_hash, role, subscription, username)
                )
            else:
                # Создаем нового пользователя
                self.logger.info(f"Создание нового пользователя {username} (роль: {role}, подписка: {subscription})")
                self.execute_query(
                    "INSERT INTO users (username, password_hash, role, subscription) VALUES (?, ?, ?, ?)",
                    (username, password_hash, role, subscription)
                )
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка при работе с пользователем {username}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при создании пользователя: {e}")
            return False

def init_db(db_path: str = None) -> DatabaseManager:
    """
    Инициализирует базу данных и возвращает менеджер.
    
    Args:
        db_path: Путь к базе данных (необязательно)
        
    Returns:
        Экземпляр DatabaseManager
    """
    return DatabaseManager(db_path)


# Создаём глобальный экземпляр для удобства использования
try:
    db_manager = DatabaseManager(str(config.DB_PATH) if hasattr(config, 'DB_PATH') else None)
except Exception as e:
    # Fallback если есть проблемы с конфигурацией
    db_manager = DatabaseManager()
