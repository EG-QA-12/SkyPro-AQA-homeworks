"""
Менеджер секретов для проекта автоматизации тестирования.

Этот модуль обеспечивает безопасную работу с конфиденциальными данными:
- Загрузка переменных окружения из .env файлов
- Валидация обязательных секретов
- Типизированный доступ к конфигурации
- Автоматическое обнаружение окружения (dev/test/prod)

Автор: Lead SDET Architect
Дата создания: 2025-06-27
"""

from __future__ import annotations

import os
import logging
import csv
from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
# from dotenv import load_dotenv
# Импорт DatabaseManager перенесен внутрь методов для избежания циклических импортов

# try:
#     from dotenv import load_dotenv
# except ImportError:
#     load_dotenv = None
#     logging.warning("python-dotenv не установлен. Установите: pip install python-dotenv")


class Environment(Enum):
    """Типы окружений для тестирования."""
    DEVELOPMENT = "dev"
    TESTING = "test"
    STAGING = "staging"
    PRODUCTION = "prod"


@dataclass
class AuthCredentials:
    """Учетные данные для авторизации."""
    username: str
    password: str
    domain: str
    cookie_name: str = "test_joint_session"
    
    def __post_init__(self) -> None:
        """Валидация данных после инициализации."""
        if not all([self.username, self.password, self.domain]):
            raise ValueError("Все поля учетных данных обязательны для заполнения")


@dataclass
class ApiCredentials:
    """Учетные данные для API."""
    base_url: str
    api_key: Optional[str] = None
    timeout: int = 30
    
    def __post_init__(self) -> None:
        """Валидация API данных."""
        if not self.base_url:
            raise ValueError("base_url обязателен для API")


@dataclass
class DatabaseCredentials:
    """Учетные данные для базы данных."""
    host: str
    port: int
    database: str
    username: str
    password: str
    
    def connection_string(self) -> str:
        """Формирует строку подключения к БД."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class TestConfig:
    """Конфигурация для тестирования."""
    environment: Environment
    auth: AuthCredentials
    api: Optional[ApiCredentials] = None
    database: Optional[DatabaseCredentials] = None
    debug_mode: bool = False
    headless: bool = True
    browser_timeout: int = 30000
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class SecretsManager:
    """
    Менеджер секретов с поддержкой .env файлов и переменных окружения.
    
    Особенности:
    - Автоматическая загрузка .env файлов по приоритету
    - Валидация обязательных переменных
    - Типизированный доступ к конфигурации
    - Поддержка различных окружений
    - Безопасное логирование (без раскрытия секретов)
    """
    
    def __init__(self, project_root: Optional[Path] = None) -> None:
        """
        Инициализация менеджера секретов.
        
        Args:
            project_root: Корневая директория проекта. По умолчанию - текущая директория.
        """
        self.project_root = project_root or Path.cwd()
        self.config_dir = self.project_root / "config"
        self.logger = self._setup_logger()
        
        # Создаем директорию конфигурации если её нет
        self.config_dir.mkdir(exist_ok=True)
        
        # Загружаем переменные окружения
        self._load_environment_variables()
        
        # Определяем текущее окружение
        self.current_environment = self._detect_environment()
        
        self.logger.info(f"Инициализирован SecretsManager для окружения: {self.current_environment.value}")
    
    def _setup_logger(self) -> logging.Logger:
        """Настройка безопасного логгера."""
        logger = logging.getLogger("SecretsManager")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_environment_variables(self) -> None:
        """Загрузка переменных окружения из .env файлов по приоритету."""
        if True: # Temporarily disabled dotenv
            self.logger.warning("Модуль dotenv недоступен. Используются только системные переменные.")
            return
        
        # Порядок приоритета .env файлов (от высшего к низшему)
        env_files = [
            self.config_dir / ".env.local",      # Локальные настройки (высший приоритет)
            self.config_dir / ".env.test",       # Тестовое окружение
            self.config_dir / ".env.dev",        # Среда разработки
            self.config_dir / ".env",            # Основные настройки
            self.project_root / ".env.local",    # Локальные настройки в корне
            self.project_root / ".env"           # Основные настройки в корне
        ]
        
        loaded_files = []
        for env_file in env_files:
            if env_file.exists():
                # load_dotenv(env_file, override=False)  # override=False = не перезаписывать уже загруженные
                loaded_files.append(str(env_file))
        
        if loaded_files:
            self.logger.info(f"Загружены .env файлы: {', '.join(loaded_files)}")
        else:
            self.logger.info("Файлы .env не найдены. Используются системные переменные.")
    
    def _detect_environment(self) -> Environment:
        """Автоматическое определение текущего окружения."""
        env_value = os.getenv("TEST_ENVIRONMENT", "dev").lower()
        
        for env in Environment:
            if env.value == env_value:
                return env
        
        self.logger.warning(f"Неизвестное окружение '{env_value}'. Используется 'dev' по умолчанию.")
        return Environment.DEVELOPMENT
    
    def get_required_env(self, key: str) -> str:
        """
        Получение обязательной переменной окружения.
        
        Args:
            key: Имя переменной окружения
            
        Returns:
            Значение переменной
            
        Raises:
            ValueError: Если переменная не найдена или пустая
        """
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Обязательная переменная окружения '{key}' не найдена или пустая")
        return value
    
    def get_optional_env(self, key: str, default: str = "") -> str:
        """
        Получение необязательной переменной окружения.
        
        Args:
            key: Имя переменной окружения
            default: Значение по умолчанию
            
        Returns:
            Значение переменной или значение по умолчанию
        """
        return os.getenv(key, default)
    
    def get_bool_env(self, key: str, default: bool = False) -> bool:
        """
        Получение boolean переменной окружения.
        
        Args:
            key: Имя переменной окружения
            default: Значение по умолчанию
            
        Returns:
            Boolean значение
        """
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on", "enabled")
    
    def get_int_env(self, key: str, default: int = 0) -> int:
        """
        Получение integer переменной окружения.
        
        Args:
            key: Имя переменной окружения
            default: Значение по умолчанию
            
        Returns:
            Integer значение
        """
        value = os.getenv(key)
        if value is None:
            return default
        
        try:
            return int(value)
        except ValueError:
            self.logger.warning(f"Некорректное число в переменной '{key}': {value}. Используется {default}")
            return default
    
    def get_auth_credentials(self) -> AuthCredentials:
        """
        Получение учетных данных для авторизации.
        
        Returns:
            Объект с учетными данными
            
        Raises:
            ValueError: Если обязательные данные отсутствуют
        """
        return AuthCredentials(
            username=self.get_required_env("AUTH_USERNAME"),
            password=self.get_required_env("AUTH_PASSWORD"),
            domain=self.get_required_env("AUTH_DOMAIN"),
            cookie_name=self.get_optional_env("AUTH_COOKIE_NAME", "test_joint_session")
        )
    
    def get_api_credentials(self) -> Optional[ApiCredentials]:
        """
        Получение учетных данных для API.
        
        Returns:
            Объект с API данными или None если не настроено
        """
        base_url = self.get_optional_env("API_BASE_URL")
        if not base_url:
            return None
        
        return ApiCredentials(
            base_url=base_url,
            api_key=self.get_optional_env("API_KEY"),
            timeout=self.get_int_env("API_TIMEOUT", 30)
        )
    
    def get_database_credentials(self) -> Optional[DatabaseCredentials]:
        """
        Получение учетных данных для базы данных.
        
        Returns:
            Объект с данными БД или None если не настроено
        """
        host = self.get_optional_env("DB_HOST")
        if not host:
            return None
        
        return DatabaseCredentials(
            host=host,
            port=self.get_int_env("DB_PORT", 5432),
            database=self.get_required_env("DB_NAME"),
            username=self.get_required_env("DB_USER"),
            password=self.get_required_env("DB_PASSWORD")
        )
    
    def get_test_config(self) -> TestConfig:
        """
        Получение полной конфигурации для тестирования.
        
        Returns:
            Объект с полной конфигурацией
        """
        return TestConfig(
            environment=self.current_environment,
            auth=self.get_auth_credentials(),
            api=self.get_api_credentials(),
            database=self.get_database_credentials(),
            debug_mode=self.get_bool_env("DEBUG_MODE", False),
            headless=self.get_bool_env("HEADLESS", True),
            browser_timeout=self.get_int_env("BROWSER_TIMEOUT", 30000)
        )
    
    def validate_configuration(self, required_sections: List[str]) -> bool:
        """
        Валидация наличия обязательных секций конфигурации.
        
        Args:
            required_sections: Список обязательных секций ['auth', 'api', 'database']
            
        Returns:
            True если все секции настроены корректно
            
        Raises:
            ValueError: Если обязательные секции отсутствуют
        """
        missing_sections = []
        
        if "auth" in required_sections:
            try:
                self.get_auth_credentials()
            except ValueError as e:
                missing_sections.append(f"auth: {e}")
        
        if "api" in required_sections and not self.get_api_credentials():
            missing_sections.append("api: API_BASE_URL не настроен")
        
        if "database" in required_sections and not self.get_database_credentials():
            missing_sections.append("database: DB_HOST не настроен")
        
        if missing_sections:
            error_msg = "Отсутствуют обязательные конфигурации:\n" + "\n".join(missing_sections)
            raise ValueError(error_msg)
        
        self.logger.info("Валидация конфигурации пройдена успешно")
        return True
    
    def get_masked_config_summary(self) -> Dict[str, Any]:
        """
        Получение обзора конфигурации с замаскированными секретами для логирования.
        
        Returns:
            Словарь с безопасной информацией о конфигурации
        """
        def mask_value(value: str) -> str:
            """Маскирует секретные значения."""
            if len(value) <= 4:
                return "*" * len(value)
            return value[:2] + "*" * (len(value) - 4) + value[-2:]
        
        summary = {
            "environment": self.current_environment.value,
            "loaded_env_files": "проверено",
            "auth_configured": bool(self.get_optional_env("AUTH_USERNAME")),
            "api_configured": bool(self.get_optional_env("API_BASE_URL")),
            "database_configured": bool(self.get_optional_env("DB_HOST"))
        }
        
        # Добавляем замаскированные значения для диагностики
        if summary["auth_configured"]:
            summary["auth_username"] = mask_value(self.get_optional_env("AUTH_USERNAME", ""))
            summary["auth_domain"] = self.get_optional_env("AUTH_DOMAIN", "не указан")
        
        return summary
    
    @classmethod
    def load_users(cls) -> List[Dict]:
        """Загружает пользователей из источника, заданного в USER_DATA_SOURCE."""
        source = os.getenv("USER_DATA_SOURCE", "csv").lower()
        
        if source == "csv":
            return cls.load_users_from_csv()
        elif source == "sqlite":
            return cls.load_users_from_sqlite()
        else:
            raise ValueError(f"Unknown user data source: {source}")

    @classmethod
    def load_users_from_sqlite(cls) -> List[Dict]:
        """Загружает пользователей из SQLite БД."""
        # Импорт внутри метода для избежания циклических импортов
        from framework.db_utils.database_manager import DatabaseManager
        
        users = []
        with DatabaseManager() as db:
            # Получаем всех активных пользователей
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT login, password, role, subscription, cookie_file
                FROM users
                WHERE is_active = 1
            """)
            
            for row in cursor.fetchall():
                # Форматируем в тот же вид, что и из CSV
                users.append({
                    "login": row[0],
                    "password": row[1],
                    "role": row[2],
                    "subscription": row[3],
                    "cookie_file": row[4]
                })
        return users

    @classmethod
    def load_users_from_csv(cls) -> List[Dict]:
        """Загружает пользователей из CSV файла."""
        users = []
        # Определяем путь к файлу пользователей
        project_root = Path(__file__).resolve().parent.parent
        csv_path = project_root / "secrets" / "bulk_users.csv"
        
        # Если файл не найден, возвращаем тестовых пользователей
        if not csv_path.exists():
            return cls._get_default_test_users()
            
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Определяем директорию cookies внутри корня проекта
                project_root = Path(__file__).resolve().parent.parent
                cookies_dir = project_root / "cookies"
                cookies_dir.mkdir(exist_ok=True)

                cookie_filename = f"{row['username'].split('@')[0]}_cookies.json"
                cookie_path = cookies_dir / cookie_filename

                users.append({
                    "name": row["username"],
                    "login": row["username"],
                    "password": row["password"],
                    "role": row.get("role", "user"),
                    "cookie_file": str(cookie_path)
                })
        return users

    @classmethod
    def _get_default_test_users(cls) -> List[Dict]:
        """Возвращает тестовых пользователей по умолчанию если CSV файл не найден."""
        project_root = Path(__file__).resolve().parent.parent
        cookies_dir = project_root / "cookies"
        cookies_dir.mkdir(exist_ok=True)
        
        return [
            {
                "name": "test_user",
                "login": "test_user",
                "password": "test_password",
                "role": "user",
                "cookie_file": str(cookies_dir / "test_user_cookies.json")
            },
            {
                "name": "admin_user", 
                "login": "admin_user",
                "password": "admin_password",
                "role": "admin",
                "cookie_file": str(cookies_dir / "admin_user_cookies.json")
            }
        ]

    @classmethod
    def get_env(cls, key: str) -> str:
        """Получает значение переменной окружения"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Missing required environment variable: {key}")
        return value


# Явная загрузка .env файла временно отключена

# Глобальный экземпляр менеджера секретов
secrets_manager = SecretsManager()


def get_config() -> TestConfig:
    """
    Удобная функция для получения конфигурации тестов.
    
    Returns:
        Объект с полной конфигурацией тестирования
    """
    return secrets_manager.get_test_config()


def validate_required_config(sections: List[str]) -> None:
    """
    Удобная функция для валидации обязательных секций.
    
    Args:
        sections: Список обязательных секций
        
    Raises:
        ValueError: Если конфигурация неполная
    """
    secrets_manager.validate_configuration(sections)


if __name__ == "__main__":
    # Демонстрация работы менеджера секретов
    try:
        config = get_config()
        print("✅ Конфигурация загружена успешно")
        print(f"Окружение: {config.environment.value}")
        print(f"Домен авторизации: {config.auth.domain}")
        
        # Проверяем доступные компоненты
        components = []
        if config.api:
            components.append("API")
        if config.database:
            components.append("Database")
        
        if components:
            print(f"Доступные компоненты: {', '.join(components)}")
        
        print("\n📋 Обзор конфигурации:")
        summary = secrets_manager.get_masked_config_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
            
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        print("\n💡 Создайте файл .env с необходимыми переменными:")
        print("AUTH_USERNAME=your_username")
        print("AUTH_PASSWORD=your_password")
        print("AUTH_DOMAIN=your_domain.com")
