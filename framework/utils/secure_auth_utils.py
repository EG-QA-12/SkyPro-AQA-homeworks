"""
Безопасные утилиты для работы с авторизацией в тестах.

Этот модуль заменяет auth_utils.py и обеспечивает:
- Безопасную работу с авторизационными данными через менеджер секретов
- Типизированные функции для работы с куками
- Логирование операций без раскрытия секретных данных
- Валидацию входных данных
- Обработку ошибок

Автор: Lead SDET Architect
Дата создания: 2025-06-27
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from playwright.sync_api import BrowserContext, Page
# Абсолютный импорт, чтобы избежать ошибок «relative import beyond top-level package»
from config.secrets_manager import get_config, AuthCredentials


@dataclass
class CookieData:
    """Структура данных для безопасной работы с куками."""
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


class SecureAuthManager:
    """
    Менеджер безопасной авторизации для автотестов.
    
    Особенности:
    - Автоматическая загрузка конфигурации из переменных окружения
    - Безопасное логирование без раскрытия секретов
    - Валидация входных данных
    - Типизированная работа с куками
    - Обработка ошибок авторизации
    """
    
    def __init__(self) -> None:
        """Инициализация менеджера авторизации."""
        self.logger = self._setup_logger()
        
        try:
            self.config = get_config()
            self.auth_credentials = self.config.auth
            self.logger.info(f"Инициализирован SecureAuthManager для домена: {self.auth_credentials.domain}")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации SecureAuthManager: {e}")
            raise
    
    def _setup_logger(self) -> logging.Logger:
        """Настройка безопасного логгера."""
        logger = logging.getLogger("SecureAuthManager")
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
        
        if not hasattr(context, 'cookies'):
            raise ValueError("BrowserContext не поддерживает работу с куками")
    
    def _validate_filename(self, filename: str) -> Path:
        """Валидация и подготовка пути к файлу."""
        if not filename:
            raise ValueError("Имя файла не может быть пустым")
        
        file_path = Path(filename)
        
        # Создаем директорию если её нет
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        return file_path
    
    def save_auth_cookie(
        self, 
        context: BrowserContext, 
        filename: str,
        validate_cookie: bool = True
    ) -> bool:
        """
        Безопасное сохранение авторизационной куки.
        
        Args:
            context: Браузерный контекст Playwright
            filename: Путь к файлу для сохранения
            validate_cookie: Валидировать наличие целевой куки
            
        Returns:
            True если кука успешно сохранена
            
        Raises:
            ValueError: При некорректных входных данных
            FileNotFoundError: При проблемах с файловой системой
        """
        try:
            self._validate_context(context)
            file_path = self._validate_filename(filename)
            
            # Получаем все куки из контекста
            all_cookies = context.cookies()
            
            # Фильтруем только нужную авторизационную куку
            target_cookies = [
                cookie for cookie in all_cookies 
                if cookie.get("name") == self.auth_credentials.cookie_name
            ]
            
            if validate_cookie and not target_cookies:
                self.logger.warning(
                    f"Авторизационная кука '{self.auth_credentials.cookie_name}' не найдена в контексте"
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
        validate_domain: bool = True
    ) -> bool:
        """
        Безопасная загрузка авторизационной куки.
        
        Args:
            context: Браузерный контекст Playwright
            filename: Путь к файлу с сохраненной кукой
            validate_domain: Валидировать соответствие домена
            
        Returns:
            True если кука успешно загружена
            
        Raises:
            ValueError: При некорректных входных данных
            FileNotFoundError: Если файл с кукой не найден
            json.JSONDecodeError: При некорректном формате файла
        """
        try:
            self._validate_context(context)
            file_path = self._validate_filename(filename)
            
            if not file_path.exists():
                raise FileNotFoundError(f"Файл с кукой не найден: {file_path}")
            
            # Загружаем куки из файла
            with open(file_path, "r", encoding="utf-8") as file:
                cookies_data = json.load(file)
            
            if not isinstance(cookies_data, list):
                raise ValueError("Некорректный формат файла с куками")
            
            # Фильтруем только целевые куки
            target_cookies = [
                cookie for cookie in cookies_data 
                if cookie.get("name") == self.auth_credentials.cookie_name
            ]
            
            if not target_cookies:
                self.logger.warning(
                    f"Целевая кука '{self.auth_credentials.cookie_name}' не найдена в файле"
                )
                return False
            
            # Валидируем домен если требуется
            if validate_domain:
                for cookie in target_cookies:
                    cookie_domain = cookie.get("domain", "")
                    if self.auth_credentials.domain not in cookie_domain:
                        self.logger.warning(
                            f"Домен куки '{cookie_domain}' не соответствует настроенному '{self.auth_credentials.domain}'"
                        )
            
            # Добавляем куки в контекст
            context.add_cookies(target_cookies)
            
            self.logger.info(
                f"Загружено {len(target_cookies)} куки из файла: {file_path.name}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки куки: {e}")
            raise
    
    def create_auth_cookie(
        self, 
        value: str, 
        custom_domain: Optional[str] = None,
        custom_path: str = "/",
        secure: bool = True
    ) -> CookieData:
        """
        Создание объекта авторизационной куки.
        
        Args:
            value: Значение куки
            custom_domain: Кастомный домен (по умолчанию из конфигурации)
            custom_path: Путь куки
            secure: Флаг secure для куки
            
        Returns:
            Объект CookieData с настроенной кукой
            
        Raises:
            ValueError: При некорректных входных данных
        """
        if not value:
            raise ValueError("Значение куки не может быть пустым")
        
        domain = custom_domain or self.auth_credentials.domain
        
        if not domain:
            raise ValueError("Домен куки не определен")
        
        cookie_data = CookieData(
            name=self.auth_credentials.cookie_name,
            value=value,
            domain=domain,
            path=custom_path,
            secure=secure
        )
        
        self.logger.info(f"Создан объект куки для домена: {domain}")
        
        return cookie_data
    
    def add_auth_cookie_to_context(
        self, 
        context: BrowserContext, 
        cookie_value: str,
        custom_domain: Optional[str] = None
    ) -> None:
        """
        Добавление авторизационной куки в браузерный контекст.
        
        Args:
            context: Браузерный контекст Playwright
            cookie_value: Значение авторизационной куки
            custom_domain: Кастомный домен (по умолчанию из конфигурации)
            
        Raises:
            ValueError: При некорректных входных данных
        """
        try:
            self._validate_context(context)
            
            cookie_data = self.create_auth_cookie(
                value=cookie_value,
                custom_domain=custom_domain
            )
            
            context.add_cookies([cookie_data.to_playwright_format()])
            
            self.logger.info("Авторизационная кука добавлена в контекст")
            
        except Exception as e:
            self.logger.error(f"Ошибка добавления куки в контекст: {e}")
            raise
    
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
                if cookie.get("name") == self.auth_credentials.cookie_name
            ]
            
            exists = len(auth_cookies) > 0
            
            self.logger.info(
                f"Проверка авторизационной куки: {'найдена' if exists else 'не найдена'}"
            )
            
            return exists
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки куки: {e}")
            return False
    
    def get_auth_cookie_value(self, context: BrowserContext) -> Optional[str]:
        """
        Получение значения авторизационной куки из контекста.
        
        Args:
            context: Браузерный контекст Playwright
            
        Returns:
            Значение куки или None если не найдена
        """
        try:
            self._validate_context(context)
            
            cookies = context.cookies()
            auth_cookies = [
                cookie for cookie in cookies 
                if cookie.get("name") == self.auth_credentials.cookie_name
            ]
            
            if auth_cookies:
                cookie_value = auth_cookies[0].get("value", "")
                self.logger.info("Значение авторизационной куки получено")
                return cookie_value
            
            self.logger.warning("Авторизационная кука не найдена в контексте")
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка получения значения куки: {e}")
            return None
    
    def clear_auth_cookies(self, context: BrowserContext) -> None:
        """
        Очистка всех авторизационных куки из контекста.
        
        Args:
            context: Браузерный контекст Playwright
        """
        try:
            self._validate_context(context)
            
            # Получаем все куки
            all_cookies = context.cookies()
            
            # Фильтруем куки, исключая авторизационные
            non_auth_cookies = [
                cookie for cookie in all_cookies 
                if cookie.get("name") != self.auth_credentials.cookie_name
            ]
            
            # Очищаем все куки и добавляем обратно только неавторизационные
            context.clear_cookies()
            
            if non_auth_cookies:
                context.add_cookies(non_auth_cookies)
            
            removed_count = len(all_cookies) - len(non_auth_cookies)
            
            self.logger.info(f"Удалено {removed_count} авторизационных куки")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки куки: {e}")
            raise


# Глобальный экземпляр менеджера авторизации
auth_manager = SecureAuthManager()


def save_cookie(context: BrowserContext, filename: str) -> None:
    """
    Совместимая функция для сохранения куки (заменяет оригинальную).
    
    Args:
        context: Браузерный контекст Playwright
        filename: Название файла для сохранения куков
    """
    auth_manager.save_auth_cookie(context, filename)


def load_cookie(context: BrowserContext, filename: str) -> None:
    """
    Совместимая функция для загрузки куки (заменяет оригинальную).
    
    Args:
        context: Браузерный контекст Playwright
        filename: Название файла с сохранённой кукой
    """
    auth_manager.load_auth_cookie(context, filename)


def create_joint_cookie(value: str, domain: str, path: str = "/") -> Dict[str, str]:
    """
    Совместимая функция для создания куки (обновлённая версия joint_cookie).
    
    Args:
        value: Значение куки
        domain: Домен сайта
        path: Путь куки
        
    Returns:
        Словарь, совместимый с BrowserContext.add_cookies
    """
    cookie_data = auth_manager.create_auth_cookie(
        value=value,
        custom_domain=domain,
        custom_path=path
    )
    
    return cookie_data.to_playwright_format()


if __name__ == "__main__":
    # Демонстрация работы безопасного менеджера авторизации
    try:
        manager = SecureAuthManager()
        print("✅ SecureAuthManager инициализирован успешно")
        print(f"Домен авторизации: {manager.auth_credentials.domain}")
        print(f"Имя куки: {manager.auth_credentials.cookie_name}")
        
        # Пример создания куки
        cookie = manager.create_auth_cookie("example_value")
        print(f"Создана кука: {cookie.name} для домена {cookie.domain}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n💡 Убедитесь, что созданы файлы конфигурации:")
        print("1. config/.env с авторизационными данными")
        print("2. Установлен модуль: pip install python-dotenv")
