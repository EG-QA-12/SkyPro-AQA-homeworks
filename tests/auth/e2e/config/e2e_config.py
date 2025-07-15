"""
Конфигурация для запуска e2e тестов с правильными путями к данным пользователей
"""
import os
import sys
from pathlib import Path

# Определяем пути к директориям
E2E_CONFIG_ROOT = Path(__file__).resolve().parent
E2E_TESTS_ROOT = E2E_CONFIG_ROOT.parent
AUTH_PROJECT_ROOT = E2E_TESTS_ROOT.parent.parent

# Добавляем auth_project в sys.path, если его там нет
if str(AUTH_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(AUTH_PROJECT_ROOT))

# Импортируем конфигурацию из auth_project
from projects.auth_management.config import AppConfig

# Переопределяем пути к данным пользователей
os.environ["LOG_PATH"] = str(AUTH_PROJECT_ROOT / "user_data" / "app.log")
os.environ["COOKIES_PATH"] = str(AUTH_PROJECT_ROOT / "user_data" / "cookies.json")

# Создаем экземпляр конфигурации
config = AppConfig()
