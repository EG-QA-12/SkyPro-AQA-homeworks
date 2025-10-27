"""
Unauthenticated User Conftest

Конфигурация для тестов главной страницы с неавторизованными пользователями.
Предоставляет контекст браузера без авторизации для тестирования
функциональности,
доступной без входа в систему.
"""

import pytest


@pytest.fixture(scope="function")
def domain_aware_context_for_bll(browser):
    """
    Фикстура для создания контекста браузера без авторизации.
    
    Предоставляет контекст браузера для bll.by домена без авторизационных кук,
    что позволяет тестировать функциональность, доступную для неавторизованных
    пользователей.
    
    Args:
        browser: Браузерный экземпляр от Playwright
        
    Yields:
        BrowserContext: Контекст браузера без авторизации для bll.by
    """
    # Настраиваем контекст для обхода антибот защиты
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1920, "height": 1080},
        locale="ru-RU",
        timezone_id="Europe/Minsk",
        ignore_https_errors=True
    )
    
    # Добавляем заголовки для обхода антибот защиты
    context.set_extra_http_headers({
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/webp,image/apng,*/*;q=0.8"
        ),
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    })
    
    print("✅ Создан контекст для неавторизованного пользователя")
    
    yield context
    
    # Очистка после тестов
    context.close()


@pytest.fixture(scope="function")
def domain_aware_context_for_bll_unauthenticated(browser):
    """
    Алиас для domain_aware_context_for_bll для явного указания
    неавторизованного доступа.
    
    Args:
        browser: Браузерный экземпляр от Playwright
        
    Yields:
        BrowserContext: Контекст браузера без авторизации для bll.by
    """
    # Настраиваем контекст для обхода антибот защиты
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1920, "height": 1080},
        locale="ru-RU",
        timezone_id="Europe/Minsk",
        ignore_https_errors=True
    )
    
    # Добавляем заголовки для обхода антибот защиты
    context.set_extra_http_headers({
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/webp,image/apng,*/*;q=0.8"
        ),
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    })
    
    print("✅ Создан контекст для неавторизованного пользователя (alias)")

    yield context

    # Очистка после тестов
    context.close()

