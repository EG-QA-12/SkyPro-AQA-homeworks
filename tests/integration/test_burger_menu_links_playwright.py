import pytest
import csv
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from framework.utils.auth_cookie_provider import get_auth_cookies


def load_burger_menu_cases(csv_path):
    cases = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            link_text = row["Текст ссылки"].strip()
            url = row["URL"].strip()
            cases.append((link_text, url))
    return cases

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()

@pytest.fixture(scope="session")
def admin_cookies():
    """Получает куки для роли admin один раз на сессию."""
    return get_auth_cookies(role="admin")

@pytest.mark.parametrize("link_text,url", load_burger_menu_cases("scripts/data/burger_menu_links_admin.csv"))
def test_burger_menu_link_and_heading(browser: Browser, admin_cookies, link_text: str, url: str):
    """
    Проверяет, что после клика по ссылке в бургер-меню открывается страница с ожидаемым заголовком.
    Для каждой проверки:
      - Открывает главную страницу
      - Кликает по бургер-меню
      - Кликает по нужной ссылке
      - Проверяет заголовок
      - Возвращается на главную для следующей итерации
    """
    context: BrowserContext = browser.new_context()
    context.add_cookies(admin_cookies)
    page: Page = context.new_page()

    try:
        # 1. Открыть главную страницу
        page.goto("https://bll.by/")
        # 2. Клик по бургер-меню (заменить локатор на актуальный для вашего сайта)
        # Пример: aria-label="Открыть меню" или уникальный класс
        burger_button = page.get_by_role("button", name="Открыть меню")
        burger_button.wait_for(state="visible", timeout=5000)
        burger_button.click()
        # 3. Явное ожидание появления нужной ссылки
        menu_link = page.get_by_role("link", name=link_text)
        menu_link.wait_for(state="visible", timeout=5000)
        # 4. Клик по нужной ссылке
        menu_link.click()
        # 5. Проверка заголовка (ожидаем, что он совпадает с текстом ссылки)
        heading = page.get_by_role("heading", name=link_text)
        assert heading.is_visible(), f"Заголовок '{link_text}' не найден после перехода по '{link_text}'"
        # 6. Возврат на главную страницу для следующей итерации
        page.goto("https://bll.by/")
    finally:
        page.close()
        context.close() 