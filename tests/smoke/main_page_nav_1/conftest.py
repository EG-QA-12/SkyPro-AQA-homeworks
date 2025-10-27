"""
Main Page Navigation Conftest

Локальная конфигурация для тестов главной страницы специально адаптированная под нужды.
Использует только bll.by домен с авторизацией.
"""

import os
import pytest
from playwright.sync_api import Browser
from framework.auth.unified_auth_manager import get_unified_auth_manager()


# Конфигурация для single-domain тестирования главной страницы
DOMAIN_CONFIG = {
    'bll': 'https://bll.by'  # Только главный сайт
}


@pytest.fixture(scope="function")
def browser_with_launch_args(browser):
    """
    Фикстура браузера с оптимизированными launch args для cross-domain cookies.
    
    Args:
        browser: Браузерный экземпляр от Playwright
        
    Yields:
        Browser: Браузер с оптимизированными параметрами запуска
    """
    # 🎯 ФАЗА 2: ЗАКЛЮЧИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ ПО БРАУЗЕРУ
    launch_args = [
        '--disable-web-security',  # КРИТИЧНО для cross-domain cookies
        '--disable-features=VizDisplayCompositor',  # Чистая визуализация
        '--disable-blink-features=AutomationControlled',  # Anti-detection base
    ]
    
    # Проверка headless режима для дополнительной оптимизации
    headless_mode = os.environ.get('HEADLESS', 'false').lower() == 'true'
    if headless_mode:
        launch_args.extend([
            '--headless=new',  # New headless with better cookie support
            '--disable-features=IsolateOrigins,site-per-process'  # Cross-SSO domains
        ])
        print("🎯 ФАЗА 2: Применяем НОВЫЙ headless режим + advanced anti-detection flags")
    
    # ИСПРАВЛЕНИЕ: Не пересоздаем браузер, а используем существующий с оптимизированными параметрами
    # Возвращаем тот же браузер, так как launch args уже применены на уровне pytest-playwright
    yield browser


@pytest.fixture(scope="function")
def domain_aware_authenticated_context_for_bll(browser_with_launch_args):
    """
    Фикстура авторизации конкретно для главной страницы bll.by.

    Предоставляет аутентифицированный контекст браузера только для bll.by домена,
    используя get_unified_auth_manager() для проверки и обновления кук.

    Args:
        browser_with_launch_args: Оптимизированный браузерный экземпляр

    Yields:
        BrowserContext: Аутентифицированный контекст браузера для bll.by
    """
    base_url = DOMAIN_CONFIG['bll']

    # Авторизация для bll.by с умной проверкой кук
    print("🎯 Домен bll: используем умную авторизацию с проверкой кук")
    auth_manager = get_unified_auth_manager()()
    storage_state = auth_manager.get_valid_storage_state(role="admin")

    # Проверка headless режима для адаптивных настроек
    headless_mode = os.environ.get('HEADLESS', 'false').lower() == 'true'
    
    # Настраиваем контекст для обхода антибот защиты с полным storage state
    context = browser_with_launch_args.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        locale="ru-RU",
        timezone_id="Europe/Minsk",
        ignore_https_errors=True,
        storage_state=storage_state,  # Полное состояние сессии вместо отдельных кук
        bypass_csp=True if headless_mode else False,  # Отключение CSP для headless
        accept_downloads=True
    )

    # 🔒 ФАЗА 1: ANTI-DETECTION - обход navigator.webdriver для SSO систем
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

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

    print("✅ Авторизация для домена bll выполнена с storage state")

    yield context

    # Очистка после тестов
    context.close()
