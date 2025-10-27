"""
Main Page Navigation Legacy Conftest

Обратная совместимость для старых тестов main_page_nav.
Содержит оригинальную логику с фикстурой domain_aware_authenticated_context_for_bll.

Используется для обеспечения совместимости со старыми тестами,
которые не готовы к переходу на новую архитектуру множественной авторизации.
"""

import pytest
from playwright.sync_api import BrowserContext
from framework.auth.unified_auth_manager import get_unified_auth_manager()


# Конфигурация для single-domain тестирования главной страницы (legacy)
DOMAIN_CONFIG = {
    'bll': 'https://bll.by'  # Только главный сайт для обратной совместимости
}


@pytest.fixture(scope="function")
def domain_aware_authenticated_context_for_bll(browser):
    """
    Фикстура авторизации конкретно для главной страницы bll.by (legacy версия).

    Предоставляет аутентифицированный контекст браузера только для bll.by домена,
    используя get_unified_auth_manager() для проверки и обновления кук.

    Это legacy версия для обратной совместимости со старыми тестами.

    Args:
        browser: Браузерный экземпляр от Playwright

    Yields:
        BrowserContext: Аутентифицированный контекст браузера для bll.by
    """
    base_url = DOMAIN_CONFIG['bll']

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

    # Авторизация для bll.by с умной проверкой кук (legacy версия)
    print("🎯 Домен bll: используем умную авторизацию с проверкой кук (legacy)")
    auth_manager = get_unified_auth_manager()()
    session_cookie = auth_manager.get_valid_session_cookie(role="admin")

    if session_cookie:
        # Правильное преобразование строки в формат Playwright
        cookies_list = [{
            "name": "test_joint_session",
            "value": session_cookie,
            "domain": ".bll.by",
            "path": "/"
        }]
        context.add_cookies(cookies_list)
        print("✅ Авторизация для домена bll выполнена (legacy)")
    else:
        print("⚠️ Не удалось получить куку для домена bll, используется fallback (legacy)")
        # Fallback на стандартную авторизацию
        from framework.auth.cookie_provider import get_auth_cookies
        context.add_cookies(get_auth_cookies(role="admin"))

    yield context

    # Очистка после тестов
    context.close()


# Маркеры для организации legacy тестов
pytest_plugins = []


def pytest_configure(config):
    """
    Конфигурация pytest для legacy main_page_nav тестов.
    """
    config.addinivalue_line(
        "markers", "main_page_nav_legacy: маркер для legacy тестов главной страницы навигации"
    )
    config.addinivalue_line(
        "markers", "legacy_auth: маркер для тестов с legacy авторизацией"
    )