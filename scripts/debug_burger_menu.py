#!/usr/bin/env python3
"""
Скрипт для диагностики структуры бургер-меню на сайте bll.by
"""

import logging
from playwright.sync_api import sync_playwright

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_burger_menu():
    """Диагностика структуры бургер-меню"""

    with sync_playwright() as p:
        # Запуск браузера в headless режиме
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        # Создание новой страницы
        page = context.new_page()

        try:
            logger.info("Переход на главную страницу...")
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            logger.info("Анализ структуры меню...")

            # Проверяем различные селекторы кнопки меню
            selectors_to_check = [
                ".menu-gumb_new.menu-mobile",
                ".menu-toggle",
                ".hamburger",
                ".burger-menu",
                "[data-menu-toggle]",
                ".mobile-menu-toggle",
                ".navbar-toggler",
                ".menu-btn",
                ".menu-button",
                ".menu-gumb",
                ".menu-mobile",
                ".gumb",
                ".mobile-menu",
                ".burger"
            ]

            logger.info("Проверка селекторов кнопки меню:")
            for selector in selectors_to_check:
                count = page.locator(selector).count()
                if count > 0:
                    logger.info(f"✓ Найден селектор: {selector} (количество: {count})")
                    # Получаем дополнительную информацию
                    element = page.locator(selector).first
                    is_visible = element.is_visible()
                    classes = element.get_attribute("class") or ""
                    logger.info(f"  - Видимый: {is_visible}")
                    logger.info(f"  - Классы: {classes}")
                else:
                    logger.info(f"✗ Селектор не найден: {selector}")

            # Проверяем наличие элементов меню
            menu_selectors = [
                ".new-menu.new-menu_main",
                ".new-menu",
                ".menu_main",
                ".burger-menu-content",
                ".mobile-menu-content",
                ".menu-content"
            ]

            logger.info("\nПроверка селекторов контейнера меню:")
            for selector in menu_selectors:
                count = page.locator(selector).count()
                if count > 0:
                    logger.info(f"✓ Найден селектор меню: {selector} (количество: {count})")
                    element = page.locator(selector).first
                    is_visible = element.is_visible()
                    logger.info(f"  - Видимый: {is_visible}")
                else:
                    logger.info(f"✗ Селектор меню не найден: {selector}")

            # Проверяем ссылки в меню
            link_selectors = [
                "a.menu_item_link",
                "a.menu-bl-item__link",
                ".menu_item_link",
                ".menu-link",
                "a[href]"
            ]

            logger.info("\nПроверка селекторов ссылок меню:")
            for selector in link_selectors:
                count = page.locator(selector).count()
                if count > 0:
                    logger.info(f"✓ Найдены ссылки: {selector} (количество: {count})")
                    # Получаем текст первых нескольких ссылок
                    links = page.locator(selector).all()[:5]  # Первые 5
                    for i, link in enumerate(links):
                        text = link.text_content().strip()
                        href = link.get_attribute("href") or ""
                        if text:
                            logger.info(f"  - Ссылка {i+1}: '{text}' -> {href}")
                else:
                    logger.info(f"✗ Ссылки не найдены: {selector}")

            # JavaScript анализ структуры
            logger.info("\nJavaScript анализ структуры меню:")
            js_result = page.evaluate("""
                // Анализ всех элементов с классами, содержащими 'menu' или 'burger'
                const elements = document.querySelectorAll('[class*="menu"], [class*="burger"], [class*="gumb"]');
                const result = [];

                for (let el of elements) {
                    const rect = el.getBoundingClientRect();
                    result.push({
                        tag: el.tagName,
                        classes: el.className,
                        visible: rect.width > 0 && rect.height > 0,
                        text: el.textContent.trim().substring(0, 50),
                        position: { x: rect.left, y: rect.top, width: rect.width, height: rect.height }
                    });
                }

                return result.slice(0, 10); // Первые 10 элементов
            """)

            for item in js_result:
                logger.info(f"Элемент: {item['tag']} .{item['classes']} | Видимый: {item['visible']} | Текст: '{item['text']}'")

            # Проверяем, есть ли уже открытые элементы меню
            logger.info("\nПроверка на уже открытые элементы меню:")
            visible_menu_elements = page.locator("a[href]").all()
            news_links = []

            for link in visible_menu_elements:
                if link.is_visible():
                    text = link.text_content().strip()
                    href = link.get_attribute("href") or ""
                    if "новост" in text.lower() or "news" in href.lower():
                        news_links.append((text, href))

            if news_links:
                logger.info("Найдены видимые ссылки на новости:")
                for text, href in news_links[:3]:
                    logger.info(f"  - '{text}' -> {href}")
            else:
                logger.info("Видимые ссылки на новости не найдены")

        except Exception as e:
            logger.error(f"Ошибка при диагностике: {e}")

        finally:
            page.close()
            context.close()
            browser.close()

if __name__ == "__main__":
    debug_burger_menu()