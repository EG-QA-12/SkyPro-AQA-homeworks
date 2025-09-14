"""
Глобальные фикстуры для End-to-End тестов.

Этот модуль содержит специфичные для E2E тестирования фикстуры:
- Настройки браузеров Playwright
- Фикстуры для браузерного контекста
- Маркеры для категоризации E2E тестов

Базовая конфигурация (sys.path, переменные окружения) наследуется
из корневого conftest.py.
"""

from typing import Generator

import pytest
from playwright.sync_api import Browser, Page

# Импорт фикстур из фреймворка
from framework.fixtures import isolated_context
from framework.utils.reporting.allure_utils import allure_step


# Экспорт фикстур для использования в тестах
__all__ = [
    'isolated_context',
    'allure_step',
]


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """
    Фикстура для передачи кастомных аргументов в контекст браузера.
    Добавляет User-Agent для headless режима.
    """
    args = {
        **browser_context_args,
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ),
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "java_script_enabled": True,
    }
    return args


@pytest.fixture(scope="function")
def browser_page(browser: Browser) -> Generator[Page, None, None]:
    """
    Создает новую страницу браузера для каждого теста.
    
    Автоматически закрывает страницу после завершения теста.
    
    Yields:
        Page: Страница Playwright для взаимодействия с браузером
    """
    context = browser.new_context()
    page = context.new_page()
    
    try:
        yield page
    finally:
        page.close()
        context.close()


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
# Патчинг URL для `allow-session=1` теперь в корневом tests/conftest.py
# и применяется глобально. Удалено из этого файла во избежание дублирования.
# ---------------------------------------------------------------------------
