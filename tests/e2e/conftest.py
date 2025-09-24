"""
Глобальные фикстуры для End-to-End тестов бургер-меню.

Этот модуль содержит специфичные для E2E тестирования фикстуры:
- Настройки браузеров Playwright
- Фикстуры для браузерного контекста с авторизацией
- Маркеры для категоризации E2E тестов
- Вспомогательные фикстуры для работы с бургер-меню

Базовая конфигурация (sys.path, переменные окружения) наследуется
из корневого conftest.py.
"""
import logging
from typing import Generator, Tuple
import pytest
from playwright.sync_api import Browser, Page, BrowserContext
import allure

# Импорт фикстур и утилит из фреймворка
from framework.fixtures.auth_fixtures import authenticated_admin, authenticated_user
from framework.utils.auth_cookie_provider import get_auth_cookies
from framework.utils.url_utils import add_allow_session_param, is_headless
from framework.utils.reporting.allure_utils import allure_step

# Импорт Page Objects
from tests.e2e.pages.main_page import MainPage
from tests.e2e.pages.burger_menu_page import BurgerMenuPage


# Экспорт фикстур для использования в тестах
__all__ = [
    'authenticated_admin',
    'authenticated_user',
    'allure_step',
    'burger_menu_page',
    'main_page_with_burger',
    'authenticated_burger_context',
    'burger_menu_items',
    'isolated_context'
]


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """
    Фикстура для передачи кастомных аргументов в контекст браузера.
    Добавляет User-Agent для headless режима и другие параметры для обхода антибот защиты.
    
    Args:
        browser_context_args: Словарь с аргументами контекста браузера
        
    Returns:
        dict: Обновленный словарь с аргументами контекста браузера
    """
    args = {
        **browser_context_args,
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "viewport": {"width": 1920, "height": 1080},
        "locale": "ru-RU",
        "timezone_id": "Europe/Minsk",
        "ignore_https_errors": True,
        "java_script_enabled": True,
    }
    return args


@pytest.fixture(scope="function")
def authenticated_burger_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Создает браузерный контекст с авторизацией через куки (роль admin) для тестов бургер-меню.
    
    Args:
        browser: Экземпляр браузера Playwright
        
    Yields:
        BrowserContext: Авторизованный контекст браузера
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
    
    try:
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function")
def burger_menu_page(authenticated_burger_context: BrowserContext) -> Generator[BurgerMenuPage, None, None]:
    """
    Создает Page Object для работы с бургер-меню.
    
    Args:
        authenticated_burger_context: Авторизованный контекст браузера
        
    Yields:
        BurgerMenuPage: Page Object для бургер-меню
    """
    page = authenticated_burger_context.new_page()
    
    # Переходим на главную страницу с параметром allow-session
    main_url = add_allow_session_param("https://bll.by/", is_headless())
    page.goto(main_url, wait_until="domcontentloaded")
    
    burger_menu_page_obj = BurgerMenuPage(page)
    
    try:
        yield burger_menu_page_obj
    finally:
        page.close()


@pytest.fixture(scope="function")
def main_page_with_burger(authenticated_burger_context: BrowserContext) -> Generator[MainPage, None, None]:
    """
    Создает Page Object для работы с главной страницей и бургер-меню.
    
    Args:
        authenticated_burger_context: Авторизованный контекст браузера
        
    Yields:
        MainPage: Page Object для главной страницы
    """
    page = authenticated_burger_context.new_page()
    
    # Переходим на главную страницу с параметром allow-session
    main_url = add_allow_session_param("https://bll.by/", is_headless())
    page.goto(main_url, wait_until="domcontentloaded")
    
    main_page_obj = MainPage(page)
    
    try:
        yield main_page_obj
    finally:
        page.close()


@pytest.fixture(scope="function")
def burger_menu_items(burger_menu_page: BurgerMenuPage) -> list:
    """
    Получает все элементы бургер-меню для использования в параметризованных тестах.
    
    Args:
        burger_menu_page: Page Object для бургер-меню
        
    Returns:
        list: Список кортежей (текст, href) для всех элементов меню
    """
    # Открываем меню
    if burger_menu_page.open_menu():
        # Получаем все элементы меню
        items = burger_menu_page.get_all_menu_items()
        return items
    else:
        # Если не удалось открыть меню, возвращаем пустой список
        return []


@pytest.fixture(scope="function")
def isolated_context(browser: Browser) -> Generator[Tuple[BrowserContext, Page], None, None]:
    """
    Создает изолированный браузерный контекст и страницу для тестов.

    Эта фикстура предоставляет чистый контекст браузера без авторизации,
    подходящий для демонстрационных тестов и простых проверок.

    Args:
        browser: Экземпляр браузера Playwright

    Yields:
        Tuple[BrowserContext, Page]: Кортеж из контекста браузера и страницы
    """
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        locale="ru-RU",
        timezone_id="Europe/Minsk",
        ignore_https_errors=True
    )

    page = context.new_page()

    try:
        yield context, page
    finally:
        page.close()
        context.close()


# Маркеры для категоризации тестов
def pytest_configure(config):
    """Регистрация пользовательских маркеров для pytest."""
    config.addinivalue_line("markers", "burger_menu: Тесты бургер-меню")
    config.addinivalue_line("markers", "navigation: Тесты навигации")
    config.addinivalue_line("markers", "functionality: Тесты функциональности")
    config.addinivalue_line("markers", "performance: Тесты производительности")
    config.addinivalue_line("markers", "security: Тесты безопасности")
    config.addinivalue_line("markers", "smoke: Smoke тесты")
    config.addinivalue_line("markers", "regression: Регрессионные тесты")


# Хуки для Allure отчетов
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Хук для создания отчетов и прикрепления дополнительной информации в Allure.
    
    Args:
        item: Тестовый элемент pytest
        call: Вызов теста
    """
    outcome = yield
    rep = outcome.get_result()
    
    # Сохраняем результат в узле теста для доступа в fixture
    setattr(item, f"rep_{rep.when}", rep)
    
    # Добавляем дополнительную информацию в Allure
    if rep.when == "call":
        if rep.passed:
            allure.dynamic.tag("passed")
        elif rep.failed:
            allure.dynamic.tag("failed")
        elif rep.skipped:
            allure.dynamic.tag("skipped")


# Фикстура для автоматического прикрепления скриншотов при падении тестов
@pytest.fixture(autouse=True)
def auto_attach_screenshot_on_failure(request):
    """
    Автоматически прикрепляет скриншот страницы при падении теста.
    
    Args:
        request: Запрос pytest
    """
    yield
    
    # Проверяем, упал ли тест
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        # Пытаемся получить page из fixture
        page_fixture_names = ['burger_menu_page', 'main_page_with_burger']
        
        for fixture_name in page_fixture_names:
            if fixture_name in request.fixturenames:
                try:
                    page = request.getfixturevalue(fixture_name).page
                    # Делаем и прикрепляем скриншот
                    screenshot = page.screenshot()
                    allure.attach(
                        screenshot, 
                        name=f"Failed Test Screenshot - {request.node.name}",
                        attachment_type=allure.attachment_type.PNG
                    )
                    break
                except Exception:
                    # Если не удалось получить скриншот, продолжаем
                    continue
