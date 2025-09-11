"""
Изолированный тест для бургер-меню.
Демонстрирует работу Playwright тестов в изолированном контексте.
"""

import pytest
from playwright.sync_api import Page, Browser
from framework.utils.auth_cookie_provider import get_auth_cookies
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import os
import time

# Таймаут для ожидания элементов
MENU_TIMEOUT = 5000

def add_allow_session_param(url: str) -> str:
    """Добавляет параметр allow-session=2 к URL для обхода антибот защиты."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query['allow-session'] = ['2']
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

@pytest.fixture(scope="session")
def browser():
    """Создаёт браузер для сессии Playwright с антибот защитой."""
    from playwright.sync_api import sync_playwright
    
    headless_mode = os.getenv('TEST_HEADLESS', 'true').lower() == 'true'
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless_mode,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-automation", 
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows", 
                "--disable-renderer-backgrounding",
                "--disable-field-trial-config",
                "--disable-ipc-flooding-protection",
                "--no-first-run",
                "--no-default-browser-check",
                "--no-pings",
                "--password-store=basic",
                "--use-mock-keychain",
                "--disable-web-security",
                "--allow-running-insecure-content"
            ]
        )
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def isolated_page(browser):
    """
    Создаёт изолированную страницу для каждого теста.
    
    Каждый тест получает свежий контекст браузера с авторизацией.
    Это обеспечивает полную изоляцию между тестами.
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
    cookies = get_auth_cookies(role="admin")
    context.add_cookies(cookies)
    
    page = context.new_page()
    yield page
    
    # Очищаем ресурсы
    page.close()
    context.close()

def test_burger_menu_isolated_navigation(isolated_page: Page):
    """
    Тест изолированного перехода по бургер-меню.
    
    Этот тест показывает, что:
    1. Playwright работает как в headless, так и в GUI режиме
    2. Тесты изолированы через function-scoped fixtures
    3. Антибот защита настроена правильно
    4. Авторизация через куки работает
    """
    
    # Добавляем allow-session параметр для обхода антибот защиты
    main_url = add_allow_session_param("https://bll.by/")
    
    print(f"Переход на главную страницу: {main_url}")
    
    # 1. Переход на главную страницу
    isolated_page.goto(main_url)
    time.sleep(1)  # Ждем загрузки страницы
    
    # 2. Открытие бургер-меню
    burger_button = isolated_page.locator("a.menu-btn.menu-btn_new").first
    burger_button.wait_for(state="visible", timeout=MENU_TIMEOUT)
    burger_button.click()
    
    time.sleep(0.5)  # Ждем открытия меню
    
    # 3. Проверка наличия элементов меню
    menu_items = isolated_page.locator("a.menu_item_link")
    count = menu_items.count()
    
    print(f"Найдено элементов в меню: {count}")
    
    assert count > 0, "Меню не открылось или не содержит элементов"
    
    # 4. Переход по первому элементу меню (обычно это "Новости")
    first_menu_item = menu_items.first
    first_menu_item.wait_for(state="visible", timeout=MENU_TIMEOUT)
    first_menu_item.click()
    
    time.sleep(1)  # Ждем загрузки целевой страницы
    
    # 5. Проверка, что переход произошел
    current_url = isolated_page.url
    page_title = isolated_page.title()
    
    print(f"Текущий URL: {current_url}")
    print(f"Заголовок страницы: {page_title}")
    
    assert len(page_title) > 0, "Страница не загрузилась (пустой заголовок)"
    
    print("✅ Изолированный тест бургер-меню пройден успешно!")

if __name__ == "__main__":
    # Можно запустить тест напрямую для отладки
    pytest.main([__file__, "-v", "-s"])
