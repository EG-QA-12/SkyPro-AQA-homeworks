import pytest
import csv
from playwright.sync_api import Page, Browser, TimeoutError as PlaywrightTimeoutError
from framework.utils.auth_cookie_provider import get_auth_cookies
from typing import Iterator, List, Tuple
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

CSV_PATH = "tests/data/burger_menu_links.csv"
WAIT_TIMEOUT = 5000  # увеличенный таймаут ожидания в миллисекундах

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
    import os
    
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

@pytest.fixture(scope="session")
def page(browser: Browser) -> Iterator[Page]:
    """Создаёт страницу с авторизацией через куки (роль admin) и антибот защитой."""
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

@pytest.mark.parametrize("link_text,href", load_burger_menu_links())
def test_burger_menu_link(page: Page, link_text: str, href: str) -> None:
    """Проверяет переход по уникальной видимой ссылке бургер-меню и наличие заголовка с текстом ссылки."""
    is_headless = True  # В этом тесте всегда headless, но можно сделать параметром
    main_url = "https://bll.by/"
    if is_headless:
        main_url = add_allow_session_param(main_url)
        href = add_allow_session_param(href)
    page.goto(main_url)
    burger_button = page.locator("a.menu-btn.menu-btn_new")
    burger_button.wait_for(state="visible", timeout=WAIT_TIMEOUT)
    burger_button.click()
    # Используем более гибкий подход для поиска элементов, как в рабочем тесте
    # Сначала пробуем точный селектор
    link = page.locator(f"a.menu_item_link[href='{href}']:has-text('{link_text}')").first
    
    # Если не нашли, пробуем более общий селектор по тексту
    if link.count() == 0:
        link = page.locator(f"a.menu_item_link:has-text('{link_text}')").first
    
    # Если все еще не нашли, ищем по href
    if link.count() == 0:
        link = page.locator(f"a.menu_item_link[href*='{href.split('/')[-1]}']").first
    
    link.wait_for(state="visible", timeout=WAIT_TIMEOUT)
    link.click()
    heading = page.locator(f"h1:has-text('{link_text}')")
    try:
        heading.wait_for(state="visible", timeout=WAIT_TIMEOUT)
    except PlaywrightTimeoutError:
        raise AssertionError(f"Заголовок '{link_text}' не найден после перехода по ссылке ({href})")
    assert heading.is_visible(), f"Заголовок '{link_text}' не найден на странице после перехода по ссылке ({href})"
