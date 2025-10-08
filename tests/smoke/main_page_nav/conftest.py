"""
Main Page Navigation Conftest

Локальная конфигурация для тестов главной страницы специально адаптированная под нужды.
Использует только bll.by домен с авторизацией.
"""

import pytest
from playwright.sync_api import BrowserContext
from framework.utils.smart_auth_manager import SmartAuthManager


# Конфигурация для single-domain тестирования главной страницы
DOMAIN_CONFIG = {
    'bll': 'https://bll.by'  # Только главный сайт
}


@pytest.fixture(scope="function")
def domain_aware_authenticated_context_for_bll(browser):
    """
    Фикстура авторизации конкретно для главной страницы bll.by.

    Предоставляет аутентифицированный контекст браузера только для bll.by домена,
    используя SmartAuthManager для проверки и обновления кук.

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

    # Авторизация для bll.by с умной проверкой кук
    print("🎯 Домен bll: используем умную авторизацию с проверкой кук")
    auth_manager = SmartAuthManager()
    session_cookie = auth_manager.get_valid_session_cookie(role="admin")

    if session_cookie:
        # Добавляем куку в контекст - приводим к формату списка словарей
        cookies_list = [session_cookie] if isinstance(session_cookie, dict) else [session_cookie]
        context.add_cookies(cookies_list)
        print("✅ Авторизация для домена bll выполнена")
    else:
        print("⚠️ Не удалось получить куку для домена bll, используется fallback")
        # Fallback на стандартную авторизацию
        from framework.utils.auth_cookie_provider import get_auth_cookies
        context.add_cookies(get_auth_cookies(role="admin"))

    yield context

    # Очистка после тестов
    context.close()
