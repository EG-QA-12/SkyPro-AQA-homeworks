"""
Тест ссылок главной страницы.
Проверяет основные ссылки главной страницы в авторизованном режиме.
"""

import pytest
from playwright.sync_api import Page, Browser
from framework.utils.auth_cookie_provider import get_auth_cookies
from typing import Iterator
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import os

WAIT_TIMEOUT = 5000  # Таймаут ожидания в миллисекундах

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
    """Создаёт страницу с авторизацией через куки (роль admin) для каждого теста."""
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

def test_main_page_loads(page_with_auth: Page) -> None:
    """Проверяет, что главная страница загружается корректно."""
    main_url = add_allow_session_param("https://bll.by/")
    page_with_auth.goto(main_url)
    
    # Проверяем заголовок страницы
    title = page_with_auth.title()
    assert "Бизнес-Инфо" in title or "Business-Info" in title, f"Некорректный заголовок страницы: {title}"
    
    # Проверяем наличие основных элементов
    logo = page_with_auth.locator("img[alt='Бизнес-Инфо']")
    assert logo.count() > 0, "Логотип не найден на главной странице"

def test_header_navigation_links(page_with_auth: Page) -> None:
    """Проверяет ссылки в верхнем меню навигации."""
    main_url = add_allow_session_param("https://bll.by/")
    page_with_auth.goto(main_url)
    
    # Проверяем основные ссылки в хедере
    header_links = [
        ("О Платформе", "https://bll.by/about"),
        ("Клуб Экспертов", "https://expert.bll.by/experts"),
        ("Купить", "https://bll.by/buy")
    ]
    
    for link_text, expected_href in header_links:
        link = page_with_auth.locator(f"a:has-text('{link_text}')")
        assert link.count() > 0, f"Ссылка '{link_text}' не найдена в хедере"
        assert link.first.is_visible(), f"Ссылка '{link_text}' не видна в хедере"
        
        # Проверяем переход для внутренних ссылок
        if "bll.by" in expected_href:
            original_url = page_with_auth.url
            link.first.click()
            page_with_auth.wait_for_timeout(1000)  # Ждем загрузки
            
            # Проверяем, что URL изменился
            new_url = page_with_auth.url
            assert new_url != original_url, f"Переход по ссылке '{link_text}' не произошел"
            
            # Возвращаемся на главную страницу для следующей проверки
            page_with_auth.goto(main_url)

def test_main_content_sections(page_with_auth: Page) -> None:
    """Проверяет основные разделы контента на главной странице."""
    main_url = add_allow_session_param("https://bll.by/")
    page_with_auth.goto(main_url)
    
    # Проверяем основные разделы
    main_sections = [
        "Интервью",
        "Мероприятия", 
        "Видеоответы",
        "Кодексы",
        "Горячие темы",
        "Всё по одной теме",
        "Навигаторы",
        "Чек-листы",
        "Каталоги форм",
        "Конструкторы",
        "Справочники",
        "Калькуляторы",
        "Закупки",
        "Тесты"
    ]
    
    for section in main_sections:
        section_element = page_with_auth.locator(f"a:has-text('{section}')")
        assert section_element.count() > 0, f"Раздел '{section}' не найден на главной странице"
        assert section_element.first.is_visible(), f"Раздел '{section}' не виден на главной странице"

def test_community_section_links(page_with_auth: Page) -> None:
    """Проверяет ссылки в разделе Сообщество."""
    main_url = add_allow_session_param("https://bll.by/")
    page_with_auth.goto(main_url)
    
    community_links = [
        ("Сообщество", "https://expert.bll.by"),
        ("Задать вопрос", "https://expert.bll.by/questions/create"),
        ("Все вопросы", "https://expert.bll.by/questions")
    ]
    
    for link_text, expected_href in community_links:
        link = page_with_auth.locator(f"a:has-text('{link_text}')")
        assert link.count() > 0, f"Ссылка '{link_text}' не найдена в разделе Сообщество"
        assert link.first.is_visible(), f"Ссылка '{link_text}' не видна в разделе Сообщество"

def test_footer_links(page_with_auth: Page) -> None:
    """Проверяет ссылки в футере."""
    main_url = add_allow_session_param("https://bll.by/")
    page_with_auth.goto(main_url)
    
    footer_links = [
        ("Политика Оператора", "https://bll.by/files/privacy_21.pdf"),
        ("Договор присоединения", "https://bll.by/files/dogovor-prisoedineniya.pdf"),
        ("Руководство пользователя", "https://bll.by/docs/436351"),
        ("Программа лояльности", "https://bll.by/files/programma-loyalnosti.pdf")
    ]
    
    for link_text, expected_href in footer_links:
        link = page_with_auth.locator(f"a:has-text('{link_text}')")
        assert link.count() > 0, f"Ссылка '{link_text}' не найдена в футере"
        assert link.first.is_visible(), f"Ссылка '{link_text}' не видна в футере"

def test_search_functionality(page_with_auth: Page) -> None:
    """Проверяет функциональность поиска."""
    main_url = add_allow_session_param("https://bll.by/")
    page_with_auth.goto(main_url)
    
    # Проверяем наличие поля поиска
    search_input = page_with_auth.locator("textbox[placeholder*='Искать']")
    assert search_input.count() > 0, "Поле поиска не найдено"
    assert search_input.first.is_visible(), "Поле поиска не видно"
    
    # Проверяем наличие кнопки поиска
    search_button = page_with_auth.locator("button:has-text('Submit')")
    assert search_button.count() > 0, "Кнопка поиска не найдена"
    assert search_button.first.is_visible(), "Кнопка поиска не видна"

def test_reference_info_section(page_with_auth: Page) -> None:
    """Проверяет раздел справочной информации."""
    main_url = add_allow_session_param("https://bll.by/")
    page_with_auth.goto(main_url)
    
    # Проверяем ссылку "Справочная информация"
    reference_link = page_with_auth.locator("a:has-text('Справочная информация')")
    assert reference_link.count() > 0, "Ссылка 'Справочная информация' не найдена"
    assert reference_link.first.is_visible(), "Ссылка 'Справочная информация' не видна"
    
    # Проверяем основные элементы справочной информации
    reference_items = [
        "Ставка рефинансирования",
        "Базовая величина", 
        "Средняя з/п за январь",
        "Пособия на детей",
        "Базовая арендная величина",
        "МЗП за февраль",
        "БПМ"
    ]
    
    for item in reference_items:
        item_element = page_with_auth.locator(f"a:has-text('{item}')")
        assert item_element.count() > 0, f"Элемент справочной информации '{item}' не найден"
        assert item_element.first.is_visible(), f"Элемент справочной информации '{item}' не виден"
