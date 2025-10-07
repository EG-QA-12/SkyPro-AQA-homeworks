"""
Конфигурация для интеграционных тестов бургер-меню.

Содержит специфичные фикстуры и настройки для тестирования навигации бургер-меню.
"""

import pytest
from playwright.sync_api import BrowserContext

from framework.utils.auth_cookie_provider import get_auth_cookies
from framework.utils.smart_auth_manager import SmartAuthManager


@pytest.fixture(scope="class")
def authenticated_burger_context(browser):
    """
    Фикстура для создания аутентифицированного контекста браузера.

    Используется для всех тестов бургер-меню, требующих авторизации.

    Args:
        browser: Браузерный экземпляр от Playwright

    Yields:
        BrowserContext: Аутентифицированный контекст браузера
    """
    # Настраиваем контекст для обхода антибот защиты
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        locale="ru-RU",
        timezone_id="Europe/Minsk",
        ignore_https_errors=True
    )

    # Добавляем заголовки для обхода антибот защиты
    context.set_extra_http_headers({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    })

    # Добавляем куки авторизации
    context.add_cookies(get_auth_cookies(role="admin"))

    yield context

    # Очистка после тестов
    context.close()


@pytest.fixture(scope="class")
def smart_authenticated_context(browser):
    """
    Умная фикстура для создания аутентифицированного контекста браузера.
    
    Использует SmartAuthManager для проверки валидности куки и автоматического обновления
    устаревших кук через API авторизацию.

    Args:
        browser: Браузерный экземпляр от Playwright

    Yields:
        BrowserContext: Аутентифицированный контекст браузера с проверенной кукой
    """
    # Настраиваем контекст для обхода антибот защиты
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        locale="ru-RU",
        timezone_id="Europe/Minsk",
        ignore_https_errors=True
    )

    # Добавляем заголовки для обхода антибот защиты
    context.set_extra_http_headers({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    })

    # Используем SmartAuthManager для получения валидной куки
    auth_manager = SmartAuthManager()
    session_cookie = auth_manager.get_valid_session_cookie(role="admin")
    
    if session_cookie:
        # Добавляем валидную куку в контекст
        context.add_cookies([session_cookie])
        print(f"✅ Используется валидная кука для роли 'admin'")
    else:
        print("⚠️ Не удалось получить валидную куку, используется стандартная авторизация")
        # Fallback на стандартную авторизацию
        context.add_cookies(get_auth_cookies(role="admin"))

    yield context

    # Очистка после тестов
    context.close()


@pytest.fixture(scope="function")
def burger_menu_page(authenticated_burger_context):
    """
    Фикстура для создания страницы с открытым бургер-меню.

    Args:
        authenticated_burger_context: Аутентифицированный контекст браузера

    Yields:
        Page: Страница с открытым бургер-меню
    """
    page = authenticated_burger_context.new_page()

    # Переход на главную страницу
    page.goto("https://bll.by/", wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")

    yield page

    # Очистка после теста
    page.close()


# Маркеры для группировки тестов
def pytest_configure(config):
    """Регистрация кастомных маркеров для тестов бургер-меню."""
    config.addinivalue_line(
        "markers", "burger_menu: тесты навигации бургер-меню"
    )
    config.addinivalue_line(
        "markers", "navigation: тесты навигации"
    )
    config.addinivalue_line(
        "markers", "left_column: тесты левой колонки меню"
    )
    config.addinivalue_line(
        "markers", "right_column: тесты правой колонки меню"
    )
    config.addinivalue_line(
        "markers", "stable: стабильные тесты (проходят в CI)"
    )
    config.addinivalue_line(
        "markers", "flaky: нестабильные тесты (требуют доработки)"
    )
    config.addinivalue_line(
        "markers", "critical: критически важные тесты"
    )
    config.addinivalue_line(
        "markers", "refactored: рефакторированные тесты"
    )