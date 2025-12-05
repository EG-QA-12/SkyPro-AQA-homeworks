"""
Оптимизированные фикстуры для burger_menu_best тестов.

Простая и надежная конфигурация без over-engineering.
"""

import pytest
from framework.utils.smart_auth_manager import SmartAuthManager


@pytest.fixture(scope="class")
def authenticated_context(browser):
    """
    Простая фикстура для создания аутентифицированного контекста.

    Использует SmartAuthManager для получения валидной куки.
    """

    # Настраиваем контекст для обхода антибот защиты
    context = browser.new_context(
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36"),
        viewport={"width": 1920, "height": 1080},
        locale="ru-RU",
        timezone_id="Europe/Minsk",
        ignore_https_errors=True
    )

    # Добавляем заголовки для обхода антибот защиты
    context.set_extra_http_headers({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    })

    # Получаем валидную куку
    auth_manager = SmartAuthManager()
    session_cookie = auth_manager.get_valid_session_cookie(role="admin")

    if session_cookie:
        # Проверяем тип данных и корректно передаем в add_cookies
        if isinstance(session_cookie, list):
            context.add_cookies(session_cookie)
            print("✅ Валидные куки добавлены в контекст")
        elif isinstance(session_cookie, dict):
            context.add_cookies([session_cookie])
            print("✅ Валидная кука добавлена в контекст")
        else:
            print(f"⚠️ Неожиданный тип куки: {type(session_cookie)}")
            # Fallback на стандартную авторизацию
            from framework.utils.auth_cookie_provider import get_auth_cookies
            cookies_list = get_auth_cookies(role="admin")
            if isinstance(cookies_list, list):
                context.add_cookies(cookies_list)
            else:
                context.add_cookies([cookies_list])
    else:
        print("⚠️ Не удалось получить куку, используется fallback")
        # Fallback на стандартную авторизацию
        from framework.utils.auth_cookie_provider import get_auth_cookies
        cookies_list = get_auth_cookies(role="admin")
        if isinstance(cookies_list, list):
            context.add_cookies(cookies_list)
        else:
            context.add_cookies([cookies_list])

    yield context

    # Очистка после тестов
    context.close()


@pytest.fixture(scope="function")
def burger_menu_page(authenticated_context):
    """
    Фикстура для создания страницы с бургер-меню.

    Args:
        authenticated_context: Аутентифицированный контекст браузера

    Yields:
        Page: Страница с открытым бургер-меню
    """
    page = authenticated_context.new_page()

    # Переход на главную страницу
    page.goto("https://bll.by/", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)

    yield page

    # Очистка после теста
    page.close()


# Простые маркеры для группировки
def pytest_configure(config):
    """Регистрация кастомных маркеров."""
    config.addinivalue_line("markers", "burger_menu: тесты навигации бургер-меню")
    config.addinivalue_line("markers", "navigation: тесты навигации")
