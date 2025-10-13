"""Корневой conftest для Pytest - главная конфигурация для всего проекта.

Этот файл содержит:
- Настройку sys.path для импорта framework модулей
- Загрузку переменных окружения из secrets/
- Общие фикстуры для HTTP сессий и Playwright браузеров
- Базовые pytest hooks для всех тестов

Все тесты в проекте (e2e, integration, unit) наследуют эти настройки,
что обеспечивает единообразную конфигурацию без дублирования кода.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Generator

import pytest
import requests
from dotenv import load_dotenv

# Импорт Allure утилит для автоматической интеграции
from framework.utils.reporting.allure_utils import *

# Абсолютный путь до корня репозитория (папка, где расположен этот conftest)
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# Загружаем переменные окружения из secrets/
load_dotenv(PROJECT_ROOT / "secrets" / ".env", override=False)
load_dotenv(PROJECT_ROOT / "secrets" / "creds.env", override=True)

# Безопасная проверка конфигурации без раскрытия секретов
auth_username = os.getenv('AUTH_USERNAME')
auth_password = os.getenv('AUTH_PASSWORD')

if auth_username and auth_password:
    print(f"✅ Конфигурация авторизации загружена для пользователя: {auth_username[:2]}***")
else:
    print("⚠️ Отсутствуют данные авторизации в переменных окружения")


@pytest.fixture(scope="session")
def http_session() -> Generator[requests.Session, None, None]:
    """
    Создает HTTP сессию для API тестов.
    
    Автоматически добавляет параметр allow-session=1 к URL для обхода
    защиты от ботов в headless режиме.
    
    Yields:
        requests.Session: Настроенная HTTP сессия
    """
    with requests.Session() as session:
        # Базовые заголовки для всех запросов
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html,application/xhtml+xml',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        })
        yield session


@pytest.fixture(scope="session")
def browser_launch_args():
    """
    Аргументы запуска браузера с защитой от детекции автоматизации.

    ПО УМОЛЧАНИЮ: GUI режим (видимый браузер) для удобства разработки.
    Для headless режима (CI/CD): установите переменную окружения HEADLESS=true

    Возвращает набор флагов Chrome для максимального обхода антибот защиты.
    """
    # ДИАГНОСТИКА: Проверяем переменные окружения
    headless_env = os.getenv('HEADLESS', 'NOT_SET')
    print(f"🔍 DEBUG: HEADLESS env var: '{headless_env}'")

    # ДИАГНОСТИКА: Проверяем переменные окружения
    headless_env = os.getenv('HEADLESS', 'NOT_SET')
    print(f"🔍 DEBUG: HEADLESS env var: '{headless_env}'")

    # ПРИНУДИТЕЛЬНО GUI РЕЖИМ! Игнорируем все переменные окружения
    headless_mode = False  # ЖЕСТКАЯ ФИКСАЦИЯ GUI РЕЖИМА
    print(f"🔍 DEBUG: Calculated headless_mode: {headless_mode}")

    result_args = {
        "headless": headless_mode,  # ПРИНУДИТЕЛЬНО GUI РЕЖИМ!
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--disable-automation",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-field-trial-config",
            "--disable-ipc-flooding-protection",
            "--no-first-run",
            "--no-default-browser-check",
            "--no-pings",
            "--password-store=basic",
            "--use-mock-keychain",
            "--disable-web-security",
            "--allow-running-insecure-content"
        ]
    }

    print(f"🔍 DEBUG: Final browser_launch_args headless: {result_args['headless']}")
    return result_args


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    ГЛОБАЛЬНАЯ НАСТРОЙКА БРАУЗЕРНОГО КОНТЕКСТА - FULL HD VIEWPORT ДЛЯ ВСЕХ ТЕСТОВ!

    Расширяет стандартные аргументы контекста браузера.
    ГАРАНТИРУЕТ Full HD 1920x1080 разрешение для ВСЕХ тестов, включая headless режим.
    """
    # Обновляем viewport для всех browser контекстов
    browser_context_args["viewport"] = {"width": 1920, "height": 1080}
    return browser_context_args


@pytest.fixture(scope="session")
def anti_bot_browser_context_args():
    """
    Аргументы контекста браузера для обхода антибот защиты.

    Настраивает реалистичные заголовки и поведение браузера.
    Теперь включает Full HD viewport по умолчанию.
    """
    return {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "viewport": {"width": 1920, "height": 1080},  # Full HD гарантирован
        "locale": "ru-RU",
        "timezone_id": "Europe/Minsk",
        "ignore_https_errors": True,
        "java_script_enabled": True,
        "extra_http_headers": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }
    }


def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Добавляет кастомные опции командной строки для pytest.

    Доступные опции:
    --headless: Запуск браузерных тестов в headless режиме
    --slow-mo: Задержка между действиями в Playwright (мс)
    --test-browser: Выбор браузера (chromium, firefox, webkit)
    --cookie-file: Указание cookie файла для тестов
    --user-role: Роль пользователя для авторизации
    --user-login: Логин конкретного пользователя

    Примечание: pytest-playwright добавляет свою опцию --browser,
    поэтому мы используем --test-browser для избежания конфликтов.
    """
    # Браузерные опции
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Запустить браузерные тесты в headless режиме"
    )
    parser.addoption(
        "--slow-mo",
        action="store",
        default=0,
        type=int,
        help="Задержка между действиями в Playwright (мс)"
    )
    parser.addoption(
        "--test-browser",
        action="store",
        default="chromium",
        choices=["chromium", "firefox", "webkit"],
        help="Выбор браузера для тестов (альтернатива pytest-playwright --browser)"
    )

    # Опции для cookie тестов
    parser.addoption(
        "--cookie-file",
        action="store",
        default=None,
        help="Укажите имя cookie-файла или 'all' для всех файлов. Или список через запятую."
    )

    # Опции для авторизационных тестов
    parser.addoption(
        "--user-role",
        action="store",
        default="admin",
        help="Роль пользователя для авторизации (admin, moderator, expert, user, qa, tester)"
    )
    parser.addoption(
        "--user-login",
        action="store",
        default=None,
        help="Логин конкретного пользователя для авторизации (например: admin, DxYZ-Ab7, yR-SUV-t)"
    )

# Глобальная переменная для отслеживания headless режима
IS_HEADLESS_MODE = False


def pytest_configure(config: pytest.Config) -> None:
    """
    Настройка pytest после парсинга конфигурации.

    Добавляет кастомные маркеры для категоризации тестов и определяет headless режим.
    """
    global IS_HEADLESS_MODE

    # Определяем headless режим из командной строки
    IS_HEADLESS_MODE = config.getoption("--headless", False) or "--headless" in config.invocation_params.args

    config.addinivalue_line("markers", "slow: Медленные тесты")
    config.addinivalue_line("markers", "integration: Интеграционные тесты")
    config.addinivalue_line("markers", "e2e: End-to-end тесты")
    config.addinivalue_line("markers", "auth: Тесты авторизации")
    config.addinivalue_line("markers", "api: API тесты")
    config.addinivalue_line("markers", "ui: UI тесты")
