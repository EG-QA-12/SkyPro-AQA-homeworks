"""
Глобальные фикстуры для End-to-End тестов.

Этот модуль содержит фикстуры для E2E тестирования:
- Настройка браузеров
- Аутентификация пользователей
- Подготовка тестовых данных
- Page Objects
"""
from __future__ import annotations

from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page


@pytest.fixture(scope="session")
def browser_context_args() -> dict:
    """
    Аргументы для настройки браузерного контекста.
    
    Returns:
        dict: Параметры конфигурации браузера.
    """
    return {
        "viewport": {"width": 1920, "height": 1080},
        "locale": "ru-RU",
        "timezone_id": "Europe/Minsk",
        "permissions": ["geolocation"],
        "record_video_dir": "test-results/videos/",
        "record_har_path": "test-results/network.har"
    }


@pytest.fixture(scope="function")
def authenticated_context_admin(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Браузерный контекст с авторизацией под администратором.
    
    Args:
        browser: Экземпляр браузера Playwright.
        
    Yields:
        BrowserContext: Авторизованный контекст администратора.
    """
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="ru-RU"
    )
    
    # TODO: Реализовать загрузку сохраненных куки администратора
    # context.add_cookies(admin_cookies)
    
    try:
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function") 
def authenticated_context_moderator(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Браузерный контекст с авторизацией под модератором.
    
    Args:
        browser: Экземпляр браузера Playwright.
        
    Yields:
        BrowserContext: Авторизованный контекст модератора.
    """
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="ru-RU"
    )
    
    # TODO: Реализовать загрузку сохраненных куки модератора
    # context.add_cookies(moderator_cookies)
    
    try:
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function")
def authenticated_page_admin(authenticated_context_admin: BrowserContext) -> Generator[Page, None, None]:
    """
    Страница с авторизацией под администратором.
    
    Args:
        authenticated_context_admin: Авторизованный контекст администратора.
        
    Yields:
        Page: Страница с правами администратора.
    """
    page = authenticated_context_admin.new_page()
    
    try:
        yield page
    finally:
        page.close()


@pytest.fixture(scope="function")
def authenticated_page_moderator(authenticated_context_moderator: BrowserContext) -> Generator[Page, None, None]:
    """
    Страница с авторизацией под модератором.
    
    Args:
        authenticated_context_moderator: Авторизованный контекст модератора.
        
    Yields:
        Page: Страница с правами модератора.
    """
    page = authenticated_context_moderator.new_page()
    
    try:
        yield page
    finally:
        page.close()


# Фикстура base_url временно отключена из-за конфликта с pytest-base-url плагином
# @pytest.fixture(scope="function")
# def base_url() -> str:
#     """
#     Базовый URL для E2E тестов.
#     
#     Returns:
#         str: Базовый URL приложения.
#     """
#     # TODO: Сделать конфигурируемым через переменные среды
#     return "https://bll.by"


# Маркеры для категоризации тестов
pytest.mark.smoke = pytest.mark.smoke
pytest.mark.regression = pytest.mark.regression
pytest.mark.user_journey = pytest.mark.user_journey
pytest.mark.admin_workflow = pytest.mark.admin_workflow
pytest.mark.cross_browser = pytest.mark.cross_browser
pytest.mark.mobile = pytest.mark.mobile
pytest.mark.slow = pytest.mark.slow
pytest.mark.critical = pytest.mark.critical
