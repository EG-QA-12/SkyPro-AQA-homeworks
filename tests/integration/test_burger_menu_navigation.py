"""
Расширенный тест навигации по бургер-меню.
Проверяет все 83 ссылки бургер-меню с авторизацией через куки.
"""

import pytest
import csv
from playwright.sync_api import Page, Browser, TimeoutError as PlaywrightTimeoutError
from framework.utils.auth_cookie_provider import get_auth_cookies
from typing import Iterator, List, Tuple
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import os

# Путь к CSV файлу с ссылками бургер-меню
CSV_PATH = "tests/data/burger_menu_links.csv"
WAIT_TIMEOUT = 5000  # Таймаут ожидания в миллисекундах

def load_burger_menu_links() -> List[Tuple[str, str]]:
    """Загружает параметры теста из CSV-файла.

    Returns:
        Список кортежей (текст ссылки, href).
    """
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [(row["link_text"].strip(), row["href"].strip()) for row in reader]

@pytest.fixture(scope="session")
def browser() -> Iterator[Browser]:
    """Создаёт браузер для сессии Playwright с антибот защитой."""
    from playwright.sync_api import sync_playwright
    
    # Читаем режим из окружения
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

def add_allow_session_param(url: str) -> str:
    """Добавляет параметр allow-session=2 к URL корректно (через ? или &)."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query['allow-session'] = ['2']
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

@pytest.fixture(scope="function")
def page_with_auth(browser: Browser) -> Iterator[Page]:
    """Создаёт страницу с авторизацией через куки (роль admin) для каждого теста.
    
    Использует function scope для полной изоляции тестов.
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
    
    page = context.new_page()
    yield page
    page.close()
    context.close()

def test_burger_menu_opens(page_with_auth: Page) -> None:
    """Проверяет, что бургер-меню открывается корректно."""
    main_url = add_allow_session_param("https://bll.by/")
    page_with_auth.goto(main_url)
    
    # Находим и кликаем по кнопке бургер-меню
    burger_button = page_with_auth.locator("a.menu-btn.menu-btn_new")
    burger_button.wait_for(state="visible", timeout=WAIT_TIMEOUT)
    burger_button.click()
    
    # Проверяем, что меню открылось (ищем элементы меню)
    menu_items = page_with_auth.locator("a.menu_item_link")
    menu_items.first.wait_for(state="visible", timeout=WAIT_TIMEOUT)
    
    # Проверяем, что есть хотя бы одна ссылка
    assert menu_items.count() > 0, "Бургер-меню не открылось или не содержит элементов"

@pytest.mark.parametrize("link_text,href", load_burger_menu_links())
def test_burger_menu_link_navigation(page_with_auth: Page, link_text: str, href: str) -> None:
    """Проверяет переход по ссылке бургер-меню.
    
    Args:
        page_with_auth: Страница с авторизацией
        link_text: Текст ссылки
        href: URL ссылки
    """
    main_url = add_allow_session_param("https://bll.by/")
    
    # Для телефонных ссылок проверяем только видимость
    if href.startswith('tel:'):
        page_with_auth.goto(main_url)
        burger_button = page_with_auth.locator("a.menu-btn.menu-btn_new")
        burger_button.wait_for(state="visible", timeout=WAIT_TIMEOUT)
        burger_button.click()
        
        # Ищем телефонную ссылку
        link = page_with_auth.locator(f"a.menu_item_link[href='{href}']")
        if link.count() == 0:
            link = page_with_auth.locator(f"a.menu_item_link:has-text('{link_text}')")
        
        link.wait_for(state="visible", timeout=WAIT_TIMEOUT)
        assert link.is_visible(), f"Телефонная ссылка '{link_text}' не найдена в бургер-меню"
        return
    
    # Для остальных ссылок проверяем переход
    page_with_auth.goto(main_url)
    burger_button = page_with_auth.locator("a.menu-btn.menu-btn_new")
    burger_button.wait_for(state="visible", timeout=WAIT_TIMEOUT)
    burger_button.click()
    
    # Ищем ссылку с учетом различных стратегий
    link = page_with_auth.locator(f"a.menu_item_link[href='{href}']:has-text('{link_text}')").first
    
    # Если не нашли, пробуем более общий селектор по тексту
    if link.count() == 0:
        link = page_with_auth.locator(f"a.menu_item_link:has-text('{link_text}')").first
    
    # Если все еще не нашли, ищем по href
    if link.count() == 0:
        link = page_with_auth.locator(f"a.menu_item_link[href*='{href.split('/')[-1]}']").first
    
    link.wait_for(state="visible", timeout=WAIT_TIMEOUT)
    assert link.is_visible(), f"Ссылка '{link_text}' не найдена в бургер-меню"
    
    # Кликаем по ссылке
    link.click()
    
    # Для внутренних ссылок проверяем заголовок или URL
    if "bll.by" in href or "expert.bll.by" in href:
        try:
            # Пытаемся найти заголовок с текстом ссылки
            heading = page_with_auth.locator(f"h1:has-text('{link_text}')")
            heading.wait_for(state="visible", timeout=WAIT_TIMEOUT)
        except PlaywrightTimeoutError:
            # Если заголовок не найден, проверяем URL
            current_url = page_with_auth.url
            if href not in current_url:
                pytest.fail(f"Заголовок '{link_text}' не найден и переход не удался ({href}). Текущий URL: {current_url}")
    else:
        # Для внешних ссылок проверяем только изменение URL
        current_url = page_with_auth.url
        if href not in current_url and href.replace('https://', '') not in current_url:
            pytest.fail(f"Переход по внешней ссылке не удался ({href}). Текущий URL: {current_url}")

def test_burger_menu_structure(page_with_auth: Page) -> None:
    """Проверяет структуру бургер-меню и наличие основных разделов."""
    main_url = add_allow_session_param("https://bll.by/")
    page_with_auth.goto(main_url)
    
    # Открываем бургер-меню
    burger_button = page_with_auth.locator("a.menu-btn.menu-btn_new")
    burger_button.wait_for(state="visible", timeout=WAIT_TIMEOUT)
    burger_button.click()
    
    # Проверяем наличие основных категорий
    expected_categories = [
        "Новости",
        "Справочная информация", 
        "Кодексы",
        "Горячие темы",
        "Всё по одной теме",
        "Навигаторы",
        "Чек-листы",
        "Каталоги форм",
        "Конструкторы",
        "Справочники",
        "Калькуляторы",
        "Тесты"
    ]
    
    for category in expected_categories:
        category_link = page_with_auth.locator(f"a.menu_item_link:has-text('{category}')")
        assert category_link.count() > 0, f"Категория '{category}' не найдена в бургер-меню"
        assert category_link.first.is_visible(), f"Категория '{category}' не видна в бургер-меню"
