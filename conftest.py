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

# Абсолютный путь до корня репозитория (папка, где расположен этот conftest)
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# Загружаем переменные окружения из secrets/
load_dotenv(PROJECT_ROOT / "secrets" / ".env", override=False)
load_dotenv(PROJECT_ROOT / "secrets" / "creds.env", override=True)

# Выводим информацию об авторизационных данных для отладки
print(f"AUTH_USERNAME: {os.getenv('AUTH_USERNAME')}")
print(f"AUTH_PASSWORD: {os.getenv('AUTH_PASSWORD')}")


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


def pytest_configure(config: pytest.Config) -> None:
    """
    Настройка pytest после парсинга конфигурации.
    
    Добавляет кастомные маркеры для категоризации тестов.
    """
    config.addinivalue_line("markers", "slow: Медленные тесты")
    config.addinivalue_line("markers", "integration: Интеграционные тесты") 
    config.addinivalue_line("markers", "e2e: End-to-end тесты")
    config.addinivalue_line("markers", "auth: Тесты авторизации")
    config.addinivalue_line("markers", "api: API тесты")
    config.addinivalue_line("markers", "ui: UI тесты")
