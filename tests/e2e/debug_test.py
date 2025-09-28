#!/usr/bin/env python3
"""
Отладочный скрипт для проверки работы рефакторированных тестов бургер-меню.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.e2e.data.navigation_targets import NAVIGATION_TARGETS
from tests.e2e.pages.burger_menu_page import BurgerMenuPage
from framework.fixtures.auth_fixtures import authenticated_admin
from playwright.sync_api import sync_playwright

def test_navigation_visibility():
    """Простой тест для проверки видимости навигации."""
    print("🚀 Запуск отладочного теста...")

    with sync_playwright() as p:
        # Запускаем браузер в видимом режиме
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        print("✅ Браузер запущен в видимом режиме")

        # Создаем контекст с авторизацией
        context = authenticated_admin(browser)
        print("✅ Авторизация выполнена")

        # Создаем страницу
        page = context.new_page()
        print("✅ Страница создана")

        try:
            # Переходим на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            print(f"✅ Перешли на главную страницу: {page.url}")

            # Создаем Page Object
            burger_menu = BurgerMenuPage(page)
            print("✅ Page Object создан")

            # Открываем бургер-меню
            menu_opened = burger_menu.open_menu()
            print(f"✅ Меню открыто: {menu_opened}")

            if menu_opened:
                # Получаем все элементы меню
                items = burger_menu.get_all_menu_items()
                print(f"✅ Найдено элементов меню: {len(items)}")

                # Показываем первые 5 элементов
                for i, (text, href) in enumerate(items[:5]):
                    print(f"  {i+1}. {text} -> {href}")

                # Пробуем перейти в "Новости"
                target = NAVIGATION_TARGETS[0]  # Новости
                print(f"🧭 Пробуем перейти в: {target.menu_text}")

                success = burger_menu.navigate_to(target.menu_text)
                print(f"✅ Навигация выполнена: {success}")

                if success:
                    burger_menu.assert_navigation_result(target)
                    print(f"✅ Проверка результата успешна для: {target.menu_text}")
                    print(f"📍 Текущий URL: {page.url}")
                else:
                    print(f"❌ Навигация не удалась для: {target.menu_text}")
            else:
                print("❌ Не удалось открыть меню")

            # Ждем, чтобы пользователь мог увидеть результат
            input("Нажмите Enter для завершения теста...")

        finally:
            page.close()
            context.close()
            browser.close()

if __name__ == "__main__":
    test_navigation_visibility()