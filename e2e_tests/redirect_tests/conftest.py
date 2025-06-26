"""Common fixtures for redirect tests using HTTP requests.

This module defines reusable pytest fixtures for testing redirect behaviour
for unauthenticated users using direct HTTP requests.
"""
from __future__ import annotations

from typing import Generator

import pytest
import requests


@pytest.fixture(scope="function")
def http_session() -> Generator[requests.Session, None, None]:
    """Session-scoped HTTP клиент для проверки статус-кодов.
    
    Создаёт requests.Session без кук и с настройками для проверки редиректов.
    Используется для быстрой проверки HTTP статус-кодов без запуска браузера.
    """
    session = requests.Session()
    # Очищаем куки для имитации неавторизованного пользователя
    session.cookies.clear()
    # Устанавливаем разумный таймаут
    session.timeout = 10
    # Добавляем User-Agent для корректной обработки запросов
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    yield session
    session.close()
