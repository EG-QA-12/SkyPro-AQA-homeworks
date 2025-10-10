"""
Burger Menu Params - Multi-Domain Parameterized Tests.

Конфигурация для тестирования burger menu на всех доменах системы.
Использует параметризацию для запуска тестов на 5 доменах одновременно.
Поддерживает headless режим с allow-session параметром для обхода защиты от ботов.
"""

import pytest
from playwright.sync_api import BrowserContext
from framework.utils.url_utils import add_allow_session_param
from framework.utils.smart_auth_manager import SmartAuthManager


# Импортируем глобальную переменную headless режима из корневого conftest.py
try:
    from conftest import IS_HEADLESS_MODE
except ImportError:
    IS_HEADLESS_MODE = False


# Конфигурация доменов для multi-domain тестирования
DOMAIN_CONFIG = {
    'bll': 'https://bll.by',              # Основной сайт
    'expert': 'https://expert.bll.by',    # Экспертная система
    'bonus': 'https://bonus.bll.by',      # Бонусная система
    'ca': 'https://ca.bll.by/',           # Контрагенты
    'cp': 'https://cp.bll.by'             # Инструменты
}


@pytest.fixture(params=['bll', 'expert', 'bonus', 'ca', 'cp'],
                ids=['Main Site (bll.by)', 'Expert System', 'Bonus System', 'CA System', 'CP System'])
def multi_domain_context(request):
    """
    Параметризованный fixture для multi-domain тестирования.

    Добавляет allow-session параметр для обхода защиты от ботов в headless режиме.

    Args:
        request: pytest fixture request object

    Returns:
        tuple: (domain_name, base_url) - имя домена и его базовый URL
    """
    domain = request.param
    base_url = DOMAIN_CONFIG[domain]

    # Добавляем параметр allow-session для headless режима
    if IS_HEADLESS_MODE:
        base_url = add_allow_session_param(base_url, headless=True)

    return domain, base_url


@pytest.fixture(params=['bll', 'expert', 'bonus', 'ca', 'cp'])
def domain_name(request):
    """Только имя домена для тестов."""
    return request.param


@pytest.fixture(params=list(DOMAIN_CONFIG.values()))
def domain_url(request):
    """Только URL домена для тестов."""
    base_url = request.param
    # Добавляем параметр allow-session для headless режима
    if IS_HEADLESS_MODE:
        base_url = add_allow_session_param(base_url, headless=True)
    return base_url


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
        from framework.utils.auth_cookie_provider import get_auth_cookies
        context.add_cookies(get_auth_cookies(role="admin"))

    yield context

    # Очистка после тестов
    context.close()


@pytest.fixture(scope="function")
def domain_aware_authenticated_context(browser, multi_domain_context):
    """
    Домен-зависимая фикстура авторизации для Playwright тестов.

    Адаптирует стратегию авторизации в зависимости от домена:
    - Для bll/expert: умная авторизация с проверкой валидности кук
    - Для bonus/ca/cp: простая авторизация без проверки (как в test_buy_navigation.py)

    Args:
        browser: Браузерный экземпляр от Playwright
        multi_domain_context: Кортеж (domain_name, base_url) из параметризации

    Yields:
        BrowserContext: Аутентифицированный контекст браузера
    """
    domain_name, base_url = multi_domain_context

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

    # Авторизация для ВСЕХ доменов (bll, expert, bonus, ca, cp)
    print(f"🎯 Домен {domain_name}: используем умную авторизацию с проверкой кук")
    auth_manager = SmartAuthManager()
    cookies_list = auth_manager.get_valid_cookies_list(role="admin")

    if cookies_list:
        # Добавляем куки в контекст
        context.add_cookies(cookies_list)
        print(f"✅ Авторизация для домена {domain_name} выполнена")
    else:
        print(f"⚠️ Не удалось получить куки для домена {domain_name}, используется fallback")
        # Fallback на стандартную авторизацию
        from framework.utils.auth_cookie_provider import get_auth_cookies
        context.add_cookies(get_auth_cookies(role="admin"))

    yield context

    # Очистка после тестов
    context.close()
