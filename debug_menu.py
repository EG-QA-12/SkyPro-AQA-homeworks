#!/usr/bin/env python3
"""
Скрипт для диагностики структуры бургер-меню
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def debug_menu():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            # Переходим на сайт
            page.goto("https://bll.by/", wait_until="domcontentloaded")

            # Открываем меню
            burger_button = page.locator("a.menu-btn.menu-btn_new")
            burger_button.wait_for(state="visible", timeout=5000)
            burger_button.click()

            # Ждем загрузки меню
            menu_container = page.locator(".new-menu.new-menu_main")
            menu_container.wait_for(state="visible", timeout=5000)

            # Получаем контейнер меню
            menu_container = page.locator(".new-menu.new-menu_main")
            print(f"Контейнер меню найден: {menu_container.is_visible()}")

            # Получаем все ссылки меню
            menu_links = page.locator("a.menu_item_link")

            print(f"Найдено {menu_links.count()} элементов меню:")

            # Проверим структуру меню
            menu_html = menu_container.inner_html()
            print(f"HTML меню (первые 500 символов): {menu_html[:500]}...")

            for i in range(min(menu_links.count(), 10)):  # Покажем только первые 10
                try:
                    link = menu_links.nth(i)
                    text = link.text_content().strip()
                    href = link.get_attribute("href") or ""

                    if text and href:
                        print(f"{i+1}. '{text}' -> {href}")

                        # Проверим видимость
                        is_visible = link.is_visible()
                        print(f"   Видимый: {is_visible}")

                        # Bounding box
                        bbox = link.bounding_box()
                        print(f"   Bounding box: {bbox}")

                except Exception as e:
                    print(f"Ошибка при обработке элемента {i}: {e}")

            # Проверим элементы docs/new
            docs_new_links = page.locator("a.menu_item_link[href*='docs/new']")
            print(f"Найдено ссылок docs/new: {docs_new_links.count()}")
            if docs_new_links.count() > 0:
                link = docs_new_links.first
                print(f"Текст: '{link.text_content().strip()}'")
                print(f"Видимый: {link.is_visible()}")
                bbox = link.bounding_box()
                print(f"Bounding box: {bbox}")

        finally:
            browser.close()

if __name__ == "__main__":
    debug_menu()