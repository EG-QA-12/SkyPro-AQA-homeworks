"""
Глобальные фикстуры для End-to-End тестов.

ОБНОВЛЕНО: Полностью адаптировано для новой архитектуры фреймворка.
Использует централизованные fixtures из framework.fixtures и новые утилиты.

Этот модуль содержит:
- Настройки браузеров для E2E тестирования
- Интеграцию с framework.fixtures для авторизации
- Специфичные для E2E тестов конфигурации
- Маркеры для категоризации тестов

Преимущества новой архитектуры для Junior QA:
1. Меньше дублирования кода - используем готовые fixtures из framework
2. Централизованное управление авторизацией через cookies/
3. Автоматическое сохранение и восстановление сессий
4. Легкое переключение между пользователями в тестах
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Импортируем fixtures из framework - это избавляет от дублирования
from framework.fixtures.auth_fixtures import (
    browser_context, clean_context, authenticated_admin, 
    authenticated_user, auth_page, quick_auth
)
from framework.utils.auth_utils import load_user_cookie, save_user_cookie


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

# ---------------------------------------------------------------------------
# Автоматическое добавление параметра ``allow-session=1`` для NOTGUI/headless
# ---------------------------------------------------------------------------

import os
from framework.utils.url_utils import ensure_allow_session_param
import requests  # noqa: E402  # уже импортирован выше, но чтобы mypy не ругался
from playwright.sync_api import Page  # noqa: E402


@pytest.fixture(autouse=True, scope="session")
def _inject_allow_session_param(monkeypatch):
    """Патчит Playwright и requests, чтобы в каждом URL был ``allow-session=1``.

    Делается один раз на сессию и прозрачно для всех тестов.  Если сайт уже
    содержит этот параметр – ничего не меняем.

    Условие «NOTGUI» трактуем так: если установлен любой из env-переменных
    ``NOTGUI=1`` или ``HEADLESS=1`` (можно расширить при необходимости).
    Если переменная не выставлена – ничего не патчим, чтобы не влиять на
    тесты в ручном/GUI режиме.
    """
    if os.getenv("NOTGUI") != "1" and os.getenv("HEADLESS") != "1":
        return  # работаем только в headless/NOTGUI сборках

    # --- Patch Page.goto ----------------------------------------------------
    original_goto = Page.goto

    def patched_goto(self: Page, url: str, *args, **kwargs):  # type: ignore[override]
        url = ensure_allow_session_param(url)
        return original_goto(self, url, *args, **kwargs)

    monkeypatch.setattr(Page, "goto", patched_goto, raising=True)

    # --- Patch requests.Session.request ------------------------------------
    original_request = requests.Session.request

    def patched_request(self: requests.Session, method: str, url: str, *args, **kwargs):  # type: ignore[override]
        url = ensure_allow_session_param(url)
        return original_request(self, method, url, *args, **kwargs)

    monkeypatch.setattr(requests.Session, "request", patched_request, raising=True)

