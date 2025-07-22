import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from framework.utils.auth_cookie_provider import get_auth_cookies
from typing import List, Dict

def print_menu_links(page, label: str, screenshot_name: str) -> None:
    links = page.locator("a.menu_item_link")
    count = links.count()
    print(f"\n[{label}] Найдено {count} ссылок с классом menu_item_link:")
    for i in range(count):
        link = links.nth(i)
        try:
            text = link.inner_text().strip()
        except Exception:
            text = "<ошибка чтения текста>"
        try:
            href = link.get_attribute("href")
        except Exception:
            href = "<ошибка href>"
        visible = link.is_visible()
        print(f"{i+1}: '{text}' | href: {href} | visible: {visible}")
    page.screenshot(path=screenshot_name)
    print(f"Скриншот сохранён: {screenshot_name}")

def diagnose_burger_menu(url: str = "https://bll.by/") -> None:
    """Диагностирует бургер-меню: выводит все ссылки до и после прокрутки, делает скриншоты.

    Args:
        url: URL главной страницы сайта.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.add_cookies(get_auth_cookies(role="admin"))
        page = context.new_page()
        page.goto(url)
        print(f"Открыта страница: {url}")
        try:
            burger_button = page.locator("a.menu-btn.menu-btn_new")
            burger_button.wait_for(state="visible", timeout=3000)
            burger_button.click()
            print("Бургер-меню открыто.")
        except PlaywrightTimeoutError:
            print("Ошибка: бургер-меню не найдено или не открылось.")
            page.screenshot(path="burger_menu_error.png")
            browser.close()
            return
        # Выводим ссылки до прокрутки
        print_menu_links(page, label="До прокрутки", screenshot_name="burger_menu_before_scroll.png")
        # Прокручиваем контейнер меню вниз
        try:
            # Находим контейнер меню (может потребоваться скорректировать селектор)
            menu_container = page.locator(".menu__list")
            if menu_container.count() > 0:
                page.evaluate("el => el.scrollTop = el.scrollHeight", menu_container)
                print("Прокрутка контейнера меню вниз выполнена.")
            else:
                print("Контейнер меню .menu__list не найден, прокрутка не выполнена.")
        except Exception as e:
            print(f"Ошибка при прокрутке меню: {e}")
        # Выводим ссылки после прокрутки
        print_menu_links(page, label="После прокрутки", screenshot_name="burger_menu_after_scroll.png")
        browser.close()

if __name__ == "__main__":
    diagnose_burger_menu() 