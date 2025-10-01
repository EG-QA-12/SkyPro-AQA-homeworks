#!/usr/bin/env python3
"""
Скрипт для анализа элементов правой колонки бургер-меню.

Используется для отладки и определения доступных элементов меню.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from playwright.sync_api import sync_playwright
from tests.e2e.pages.burger_menu_page import BurgerMenuPage


def debug_right_column_menu():
    """Анализирует элементы правой колонки бургер-меню."""
    with sync_playwright() as p:
        # Запускаем браузер в headless режиме для анализа
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        try:
            page = context.new_page()
            burger_menu = BurgerMenuPage(page)

            # Переходим на главную страницу
            print("Переход на https://bll.by/")
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Открываем меню
            print("Открытие бургер-меню...")
            if not burger_menu.open_menu():
                print("Не удалось открыть меню")
                return

            # Ждем загрузки меню
            page.wait_for_timeout(2000)

            # Ищем все ссылки в меню
            print("\n=== Все ссылки в меню ===")
            all_links = page.locator("a.menu_item_link").all()
            for i, link in enumerate(all_links):
                text = link.text_content().strip()
                href = link.get_attribute("href") or ""
                if text:
                    print(f"{i+1}. '{text}' -> {href}")

            # Ищем элементы с ARIA ролями
            print("\n=== Элементы с ARIA ролями ===")
            aria_links = page.get_by_role("link").all()
            for i, link in enumerate(aria_links):
                text = link.text_content().strip()
                if text and len(text) > 2:  # Фильтруем короткие тексты
                    print(f"{i+1}. '{text}'")

            # Ищем элементы правой колонки (обычно они имеют определенные CSS классы или находятся в определенных контейнерах)
            print("\n=== Элементы правой колонки (предположительно) ===")

            # Проверяем различные селекторы для правой колонки
            right_column_selectors = [
                ".menu_bl_list",  # Общий класс для блоков меню
                ".new-menu_main .menu_bl_list",  # Конкретный путь
                "div.menu_bl_list",  # Все блоки меню
            ]

            for selector in right_column_selectors:
                print(f"\nПроверка селектора: {selector}")
                blocks = page.locator(selector).all()
                for i, block in enumerate(blocks):
                    links = block.locator("a").all()
                    if links:
                        print(f"  Блок {i+1}:")
                        for j, link in enumerate(links):
                            text = link.text_content().strip()
                            href = link.get_attribute("href") or ""
                            if text:
                                print(f"    {j+1}. '{text}' -> {href}")

            # Проверяем наличие конкретных элементов, которые не найдены
            print("\n=== Проверка конкретных элементов ===")
            test_elements = [
                "Контроль документов",
                "Профиль эксперта",
                "Мои данные",
                "Напоминания",
                "Личный кабинет"
            ]

            for element_text in test_elements:
                # Проверяем по тексту
                text_links = page.locator(f"a:has-text('{element_text}')").all()
                print(f"'{element_text}': найдено {len(text_links)} ссылок по тексту")

                # Проверяем по ARIA роли
                aria_links = page.get_by_role("link", name=element_text).all()
                print(f"'{element_text}': найдено {len(aria_links)} ссылок по ARIA роли")

                # Проверяем по href
                href_links = page.locator(f"a[href*='{element_text.lower().replace(' ', '-')}']").all()
                print(f"'{element_text}': найдено {len(href_links)} ссылок по href")

        finally:
            browser.close()


if __name__ == "__main__":
    debug_right_column_menu()