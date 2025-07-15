"""
Объединенные утилиты для работы с авторизацией в тестах.

Этот модуль объединяет функциональность auth_utils.py и secure_auth_utils.py,
предоставляя единый интерфейс для работы с авторизацией:

- Совместимость с существующим кодом через старые функции
- Современная архитектура с типизацией и валидацией
- Безопасная работа с авторизационными данными
- Централизованное логирование и обработка ошибок
- Поддержка различных сценариев авторизации

Рекомендуется использовать SecureAuthManager для нового кода,
старые функции save_cookie/load_cookie оставлены для совместимости.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass

from playwright.sync_api import BrowserContext, Page
from .cookie_constants import COOKIE_NAME, LOGIN_URL

# Конфигурация логирования
logger = logging.getLogger(__name__)


@dataclass
class CookieData:
    """Структура данных для работы с куками."""
    name: str
    value: str
    domain: str
    path: str = "/"
    secure: bool = True
    http_only: bool = True
    same_site: str = "Lax"
    
    def to_playwright_format(self) -> Dict[str, Any]:
        """Конвертация в формат Playwright."""
        return {
            "name": self.name,
            "value": self.value,
            "domain": self.domain,
            "path": self.path,
            "secure": self.secure,
            "httpOnly": self.http_only,
            "sameSite": self.same_site
        }


class UnifiedAuthManager:
    """
    Объединенный менеджер авторизации для автотестов.
    
    Особенности:
    - Совместимость с существующим кодом
    - Безопасное логирование без раскрытия секретов
    - Валидация входных данных
    - Типизированная работа с куками
    - Централизованная обработка ошибов
    """
    
    def __init__(self, cookie_name: str = COOKIE_NAME) -> None:
        """Инициализация менеджера авторизации."""
        self.cookie_name = cookie_name
        self.logger = self._setup_logger()
        self.logger.info(f"Инициализирован UnifiedAuthManager с кукой: {cookie_name}")
    
    def _setup_logger(self) -> logging.Logger:
        """Настройка логгера."""
        logger = logging.getLogger("UnifiedAuthManager")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _validate_context(self, context: BrowserContext) -> None:
        """Валидация браузерного контекста."""
        if not context:
            raise ValueError("BrowserContext не может быть None")
    
    def _validate_filename(self, filename: str) -> Path:
        """Валидация и подготовка пути к файлу."""
        if not filename:
            raise ValueError("Имя файла не может быть пустым")
        
        file_path = Path(filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        return file_path
    
    def save_auth_cookie(
        self, 
        context: BrowserContext, 
        filename: str,
        validate_cookie: bool = True
    ) -> bool:
        """
        Сохранение авторизационной куки в файл.
        
        Args:
            context: Браузерный контекст Playwright
            filename: Путь к файлу для сохранения
            validate_cookie: Валидировать наличие целевой куки
            
        Returns:
            True если кука успешно сохранена
        """
        try:
            self._validate_context(context)
            file_path = self._validate_filename(filename)
            
            # Получаем все куки из контекста
            all_cookies = context.cookies()
            
            # Фильтруем только нужную авторизационную куку
            target_cookies = [
                cookie for cookie in all_cookies 
                if cookie.get("name") == self.cookie_name
            ]
            
            if validate_cookie and not target_cookies:
                self.logger.warning(
                    f"Авторизационная кука '{self.cookie_name}' не найдена в контексте"
                )
                return False
            
            # Сохраняем куки в файл
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(target_cookies, file, indent=2, ensure_ascii=False)
            
            cookie_count = len(target_cookies)
            self.logger.info(
                f"Сохранено {cookie_count} куки в файл: {file_path.name}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения куки: {e}")
            raise
    
    def load_auth_cookie(
        self, 
        context: BrowserContext, 
        filename: str,
        validate_file: bool = True
    ) -> bool:
        """
        Загрузка авторизационной куки из файла.
        
        Args:
            context: Браузерный контекст Playwright
            filename: Путь к файлу с сохраненной кукой
            validate_file: Валидировать существование файла
            
        Returns:
            True если кука успешно загружена
        """
        try:
            self._validate_context(context)
            file_path = self._validate_filename(filename)
            
            if validate_file and not file_path.exists():
                self.logger.warning(f"Файл с кукой не найден: {file_path}")
                return False
            
            # Загружаем куки из файла
            with open(file_path, "r", encoding="utf-8") as file:
                cookies_data = json.load(file)
            
            if not isinstance(cookies_data, list):
                raise ValueError("Некорректный формат файла с куками")
            
            # Добавляем куки в контекст
            if cookies_data:
                context.add_cookies(cookies_data)
                self.logger.info(
                    f"Загружено {len(cookies_data)} куки из файла: {file_path.name}"
                )
                return True
            else:
                self.logger.warning("Файл с куками пуст")
                return False
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки куки: {e}")
            raise
    
    def get_cookie_path(self, username: str) -> Path:
        """
        Получает путь к файлу с cookies для указанного пользователя.
        
        Args:
            username: Имя пользователя для которого нужен файл cookies
            
        Returns:
            Полный путь к файлу с cookies пользователя
        """
        project_root = Path(__file__).parent.parent.parent
        cookies_dir = project_root / "cookies"
        cookies_dir.mkdir(exist_ok=True)
        cookie_filename = f"{username}_cookies.json"
        return cookies_dir / cookie_filename
    
    def save_user_cookie(self, context: BrowserContext, username: str) -> bool:
        """
        Сохраняет cookies пользователя с автоматическим определением пути.
        
        Args:
            context: Браузерный контекст Playwright
            username: Имя пользователя для сохранения cookies
            
        Returns:
            True если успешно сохранено
        """
        cookie_path = self.get_cookie_path(username)
        result = self.save_auth_cookie(context, str(cookie_path))
        if result:
            self.logger.info(f"Cookies для пользователя '{username}' сохранены в {cookie_path}")
        return result
    
    def load_user_cookie(self, context: BrowserContext, username: str) -> bool:
        """
        Загружает cookies пользователя с автоматическим определением пути.
        
        Args:
            context: Браузерный контекст Playwright
            username: Имя пользователя для загрузки cookies
            
        Returns:
            True если cookies успешно загружены
        """
        cookie_path = self.get_cookie_path(username)
        if not cookie_path.exists():
            self.logger.warning(f"Файл с cookies для пользователя '{username}' не найден")
            return False
        
        result = self.load_auth_cookie(context, str(cookie_path))
        if result:
            self.logger.info(f"Cookies для пользователя '{username}' успешно загружены")
        return result
    
    def check_auth_cookie_exists(self, context: BrowserContext) -> bool:
        """
        Проверка наличия авторизационной куки в контексте.
        
        Args:
            context: Браузерный контекст Playwright
            
        Returns:
            True если авторизационная кука присутствует
        """
        try:
            self._validate_context(context)
            cookies = context.cookies()
            auth_cookies = [
                cookie for cookie in cookies 
                if cookie.get("name") == self.cookie_name
            ]
            return len(auth_cookies) > 0
        except Exception as e:
            self.logger.error(f"Ошибка проверки куки: {e}")
            return False
    
    def clear_all_cookies(self, context: BrowserContext) -> None:
        """
        Очистка всех cookies в контексте.
        
        Args:
            context: Браузерный контекст Playwright
        """
        try:
            self._validate_context(context)
            context.clear_cookies()
            self.logger.info("Все cookies очищены из контекста")
        except Exception as e:
            self.logger.error(f"Ошибка очистки cookies: {e}")
            raise
    
    def list_available_cookies(self, cookies_dir: Optional[str] = None) -> List[str]:
        """
        Получение списка доступных файлов с cookies.
        
        Args:
            cookies_dir: Директория с файлами cookies (по умолчанию проектная)
            
        Returns:
            Список имен файлов с cookies
        """
        if cookies_dir is None:
            project_root = Path(__file__).parent.parent.parent
            cookies_dir = project_root / "cookies"
        else:
            cookies_dir = Path(cookies_dir)
        
        if not cookies_dir.exists():
            return []
        
        cookie_files = [
            f.stem.replace("_cookies", "") 
            for f in cookies_dir.glob("*_cookies.json")
        ]
        
        return sorted(cookie_files)


# Глобальный экземпляр менеджера
auth_manager = UnifiedAuthManager()


# === СОВМЕСТИМЫЕ ФУНКЦИИ ДЛЯ СТАРОГО КОДА ===

def save_cookie(context: BrowserContext, filename: str) -> None:
    """
    Совместимая функция для сохранения куки (заменяет auth_utils.save_cookie).
    
    Args:
        context: Браузерный контекст Playwright
        filename: Название файла для сохранения куков
    """
    auth_manager.save_auth_cookie(context, filename)


def load_cookie(context: BrowserContext, filename: str) -> None:
    """
    Совместимая функция для загрузки куки (заменяет auth_utils.load_cookie).
    
    Args:
        context: Браузерный контекст Playwright
        filename: Название файла с сохранённой кукой
    """
    auth_manager.load_auth_cookie(context, filename)


def get_cookie_path(username: str) -> Path:
    """
    Совместимая функция для получения пути к файлу cookies.
    
    Args:
        username: Имя пользователя
        
    Returns:
        Путь к файлу cookies
    """
    return auth_manager.get_cookie_path(username)


def save_user_cookie(context: BrowserContext, username: str) -> None:
    """
    Совместимая функция для сохранения cookies пользователя.
    
    Args:
        context: Браузерный контекст Playwright
        username: Имя пользователя
    """
    auth_manager.save_user_cookie(context, username)


def load_user_cookie(context: BrowserContext, username: str) -> bool:
    """
    Совместимая функция для загрузки cookies пользователя.
    
    Args:
        context: Браузерный контекст Playwright
        username: Имя пользователя
        
    Returns:
        True если успешно загружено
    """
    return auth_manager.load_user_cookie(context, username)


def clear_all_cookies(context: BrowserContext) -> None:
    """
    Совместимая функция для очистки всех cookies.
    
    Args:
        context: Браузерный контекст Playwright
    """
    auth_manager.clear_all_cookies(context)


def list_available_cookies(cookies_dir: Optional[str] = None) -> List[str]:
    """
    Совместимая функция для получения списка доступных cookies.
    
    Args:
        cookies_dir: Директория с cookies
        
    Returns:
        Список имен пользователей с сохраненными cookies
    """
    return auth_manager.list_available_cookies(cookies_dir)


def check_cookie_validity(context: BrowserContext) -> bool:
    """
    Совместимая функция для проверки валидности cookies.
    
    Args:
        context: Браузерный контекст Playwright
        
    Returns:
        True если cookies валидны
    """
    return auth_manager.check_auth_cookie_exists(context)


def get_auth_credentials() -> Dict[str, str]:
    """
    Получает учетные данные для авторизации из переменных окружения.
    
    Returns:
        Словарь с ключами 'username' и 'password'
    """
    try:
        from config.secrets_manager import get_secret
        username = get_secret("username")
        password = get_secret("password")
        return {"username": username, "password": password}
    except ImportError:
        # Fallback для случаев, когда secrets_manager недоступен
        username = os.getenv("AUTH_USERNAME", "")
        password = os.getenv("AUTH_PASSWORD", "")
        return {"username": username, "password": password}


# Алиасы для совместимости с secure_auth_utils
SecureAuthManager = UnifiedAuthManager 