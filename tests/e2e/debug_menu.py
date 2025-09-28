"""
Скрипт для диагностики бургер-меню на сайте bll.by
"""
import logging
from playwright.sync_api import sync_playwright

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def diagnose_burger_menu():
    """Диагностика бургер-меню"""
    with sync_playwright() as p:
        # Запуск браузера
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Переход на главную страницу
            logger.info("Переход на https://bll.by/")
            page.goto("https://bll.by/", wait_until="domcontentloaded")

            # Ждем загрузки страницы
            page.wait_for_timeout(3000)

            # Ищем кнопку бургер-меню разными способами
            logger.info("Поиск кнопки бургер-меню...")

            # Вариант 1: Текущий селектор
            burger_button = page.locator("a.menu-btn.menu-btn_new")
            count1 = burger_button.count()
            logger.info(f"Селектор 'a.menu-btn.menu-btn_new': найдено {count1} элементов")

            # Вариант 2: Более общий селектор
            burger_button2 = page.locator("a.menu-btn")
            count2 = burger_button2.count()
            logger.info(f"Селектор 'a.menu-btn': найдено {count2} элементов")

            # Вариант 3: По классу
            burger_button3 = page.locator(".menu-btn")
            count3 = burger_button3.count()
            logger.info(f"Селектор '.menu-btn': найдено {count3} элементов")

            # Вариант 4: По частичному классу
            burger_button4 = page.locator("[class*='menu-btn']")
            count4 = burger_button4.count()
            logger.info(f"Селектор '[class*=\"menu-btn\"]': найдено {count4} элементов")

            # Вариант 5: По ARIA роли
            burger_button5 = page.get_by_role("button", name="Меню")
            count5 = burger_button5.count()
            logger.info(f"ARIA роль 'button' с именем 'Меню': найдено {count5} элементов")

            # Вариант 6: По тексту
            burger_button6 = page.locator("text=Меню")
            count6 = burger_button6.count()
            logger.info(f"Текст 'Меню': найдено {count6} элементов")

            # Проверяем все найденные элементы
            if count1 > 0:
                logger.info("Анализ первого найденного элемента:")
                element = burger_button.first
                tag_name = element.evaluate("el => el.tagName")
                classes = element.evaluate("el => el.className")
                text = element.text_content()
                visible = element.is_visible()
                logger.info(f"  Тег: {tag_name}")
                logger.info(f"  Классы: {classes}")
                logger.info(f"  Текст: {text}")
                logger.info(f"  Видимый: {visible}")

            # Ищем контейнер меню
            logger.info("\nПоиск контейнера меню...")
            menu_container = page.locator(".new-menu.new-menu_main")
            count_container = menu_container.count()
            logger.info(f"Селектор '.new-menu.new-menu_main': найдено {count_container} элементов")

            # Ищем элементы меню
            logger.info("\nПоиск элементов меню...")
            menu_items = page.locator("a.menu_item_link")
            count_items = menu_items.count()
            logger.info(f"Селектор 'a.menu_item_link': найдено {count_items} элементов")

            # Проверяем HTML структуры
            logger.info("\nПроверка HTML структуры...")
            html = page.locator("html").inner_html()
            if "menu-btn" in html:
                logger.info("✓ Найден 'menu-btn' в HTML")
            else:
                logger.info("✗ Не найден 'menu-btn' в HTML")

            if "new-menu" in html:
                logger.info("✓ Найден 'new-menu' в HTML")
            else:
                logger.info("✗ Не найден 'new-menu' в HTML")

            if "menu_item_link" in html:
                logger.info("✓ Найден 'menu_item_link' в HTML")
            else:
                logger.info("✗ Не найден 'menu_item_link' в HTML")

            # Делаем скриншот
            page.screenshot(path="burger_menu_diagnosis.png")
            logger.info("Скриншот сохранен: burger_menu_diagnosis.png")

            # Дополнительная диагностика - проверяем все элементы с классом menu
            logger.info("\nПоиск всех элементов с классом 'menu'...")
            menu_elements = page.locator("[class*='menu']")
            count_menu = menu_elements.count()
            logger.info(f"Найдено элементов с 'menu' в классе: {count_menu}")

            for i in range(min(count_menu, 10)):  # Показываем первые 10
                try:
                    element = menu_elements.nth(i)
                    classes = element.evaluate("el => el.className")
                    tag = element.evaluate("el => el.tagName")
                    text = element.text_content().strip()[:50] if element.text_content() else ""
                    logger.info(f"  {i}: {tag}.{classes} - '{text}'")
                except Exception as e:
                    logger.warning(f"Ошибка при анализе элемента {i}: {e}")

            # Проверяем наличие конкретных элементов
            logger.info("\nПроверка наличия конкретных элементов:")
            news_link = page.locator("text=Новости")
            news_count = news_link.count()
            logger.info(f"Ссылка 'Новости': найдено {news_count} элементов")

            sprav_link = page.locator("text=Справочная информация")
            sprav_count = sprav_link.count()
            logger.info(f"Ссылка 'Справочная информация': найдено {sprav_count} элементов")

            logger.info("Диагностика завершена. Закрываем браузер...")

        except Exception as e:
            logger.error(f"Ошибка при диагностике: {e}")
            page.screenshot(path="burger_menu_error.png")
            logger.info("Скриншот ошибки сохранен: burger_menu_error.png")
        finally:
            browser.close()


if __name__ == "__main__":
    diagnose_burger_menu()