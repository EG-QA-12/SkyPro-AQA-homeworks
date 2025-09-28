"""
Ручная проверка работы рефакторинга бургер-меню
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from playwright.sync_api import sync_playwright
from tests.e2e.pages.burger_menu_page import BurgerMenuPage
from framework.utils.auth_cookie_provider import get_auth_cookies


def test_manual():
    """Ручная проверка работы"""
    print("Запуск ручной проверки бургер-меню...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="ru-RU",
            timezone_id="Europe/Minsk",
            ignore_https_errors=True
        )

        # Добавляем куки авторизации
        context.add_cookies(get_auth_cookies(role="admin"))

        page = context.new_page()

        try:
            print("Переход на главную страницу...")
            page.goto("https://bll.by/", wait_until="domcontentloaded")

            print("Создание объекта BurgerMenuPage...")
            burger_menu = BurgerMenuPage(page)

            print("Попытка открытия бургер-меню...")
            result = burger_menu.open_menu()
            print(f"Результат открытия меню: {result}")

            if result:
                print("Меню успешно открыто!")

                print("Проверка, открыто ли меню...")
                is_open = burger_menu.is_menu_open()
                print(f"Меню открыто: {is_open}")

                print("Попытка навигации в 'Новости'...")
                success = burger_menu.navigate_to("Новости")
                print(f"Результат навигации: {success}")

                if success:
                    print("Навигация успешна!")
                    print(f"Текущий URL: {page.url}")
                else:
                    print("Навигация не удалась")
            else:
                print("Не удалось открыть меню")

        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            input("Нажмите Enter для завершения...")
            browser.close()


if __name__ == "__main__":
    test_manual()