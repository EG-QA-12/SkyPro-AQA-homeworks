"""
Глобальные фикстуры для Integration тестов.

Этот модуль содержит общие фикстуры для всех типов интеграционных тестов:
- HTTP клиенты для API тестирования
- Подключения к базе данных
- Конфигурация окружений
"""
from __future__ import annotations

from typing import Generator

import pytest
import requests


@pytest.fixture(scope="session")
def http_session() -> Generator[requests.Session, None, None]:
    """
    HTTP клиент для интеграционных тестов.
    
    Создает сессию requests без аутентификации для тестирования
    публичных API и инфраструктуры.
    
    Yields:
        requests.Session: Настроенная HTTP сессия.
    """
    session = requests.Session()
    
    # Настройки по умолчанию
    session.headers.update({
        "User-Agent": "Integration-Tests/1.0 (BLL Test Suite)"
    })
    
    # Таймауты по умолчанию
    session.timeout = 10
    
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="session")
def test_environment() -> str:
    """
    Определяет текущее окружение для тестирования.
    
    Returns:
        str: Название окружения (production, staging, development).
    """
    # TODO: Реализовать определение окружения через переменные среды
    return "production"


@pytest.fixture(scope="function")
def api_base_url(test_environment: str) -> str:
    """
    Базовый URL для API тестов в зависимости от окружения.
    
    Args:
        test_environment: Название окружения.
        
    Returns:
        str: Базовый URL для API.
    """
    urls = {
        "production": "https://ca.bll.by/api",
        "staging": "https://staging.bll.by/api", 
        "development": "http://localhost:8000/api"
    }
    return urls.get(test_environment, urls["production"])


# Маркеры для категоризации тестов
pytest.mark.infrastructure = pytest.mark.infrastructure
pytest.mark.api = pytest.mark.api
pytest.mark.database = pytest.mark.database
pytest.mark.slow = pytest.mark.slow
pytest.mark.smoke = pytest.mark.smoke
