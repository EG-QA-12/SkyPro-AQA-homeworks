# smoke_test_burger_menu_part2.py

import pytest
import logging
from test_utils import (
    Config,
    RequestHandler,
    Auth,
    setup_logging,
    generate_random_text,
    FolderUtils,
    ScreenshotManager
)

def test_run_part2(browser_fixture):
    setup_logging()
    page = browser_fixture
    request_handler = RequestHandler()
    request_handler.setup_js_monitoring(page)
    page.on("response", request_handler.handle_response)

    try:
        # Авторизация
        request_handler.set_current_step("Авторизация")
        username, password = Auth.get_credentials()
        Auth.login(page, username, password)

        # Навигаторы и каталоги
        request_handler.set_current_step("Работа с навигаторами")
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Навигаторы").click()
        page.get_by_role("link", name="Всем пользователям").click()  # Это было пропущено в нерабочей версии
        page.locator("#document_content").get_by_role("link", name="Экономисту").click()
        page.goto(f"{Config.BaseUrl}/docs/navigatory-140000")
        page.locator("#navigation").get_by_role("link", name="Бухгалтеру").click()
        page.locator("#navigation").get_by_role("link", name="Специалисту по охране труда", exact=True).click()
        page.locator("#navigation").get_by_role("link", name="Экологу", exact=True).click()
        page.locator("div.topic-text").get_by_text("Резервирование подрядчиком средств").click()
        page.get_by_role("link", name="Бизнес-Инфо").click()

        # Каталоги форм
        request_handler.set_current_step("Работа с каталогами форм")
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Каталоги форм").click()
        page.get_by_title("Каталоги форм секретарю").nth(1).click()
        page.get_by_role("heading", name="Каталоги форм секретарю").click()
        page.get_by_role("link", name="Акт в делопроизводстве и архивном деле: каталог форм").click()
        page.locator("#navigation p").filter(has_text="Формы с заполнением").get_by_role("link").click()
        page.get_by_title("Акт приема-передачи дел при смене главного бухгалтера (пример) (с комментарием)").click()
        page.get_by_role("link", name="абз").click()
        page.get_by_role("link", name="абз. 2").click()
        page.get_by_role("link", name="Глава 1.").click()
        page.get_by_role("link", name="Статья 2.").click()

        # Конструкторы
        request_handler.set_current_step("Работа с конструкторами")
        page.locator(".menu-btn").click()
        page.get_by_role("link", name="Конструкторы").click()
        page.get_by_role("heading", name="Бухгалтеру").click()
        page.get_by_role("link", name="Учетная политика организации в 2024 году").click()
        page.get_by_text("Торговля").click()
        page.get_by_text("Промышленность").click()
        page.get_by_text("Банк", exact=True).click()
        page.locator("#performer_id1").get_by_text("да").click()
        page.locator("#performer_id2").get_by_text("да").click()
        page.get_by_role("link", name="Бизнес-Инфо").click()

        # Справочники
        request_handler.set_current_step("Работа со справочниками")
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Справочники").click()
        page.get_by_role("link", name="Коды назначения платежа по ISO").nth(1).click()
        page.goto(f"{Config.BaseUrl}/docs/spravochniki-220099")
        page.get_by_role("link", name="Момент фактической реализации для целей исчисления НДС").click()
        page.get_by_placeholder("объект реализации").click()
        page.get_by_role("button", name="Найти").click()
        page.get_by_role("link", name="Бизнес-Инфо").click()

        # Калькуляторы
        request_handler.set_current_step("Работа с калькуляторами")
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Калькуляторы").click()
        page.get_by_title("Калькуляторы специалисту в строительстве").nth(1).click()

        # Тесты
        request_handler.set_current_step("Работа с тестами")
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Тесты").click()
        page.get_by_title("Тесты для проверки знаний бухгалтера").nth(1).click()
        page.get_by_role("link", name="• Случаи выставления ЭСЧФ").click()

        # Полезные ссылки
        request_handler.set_current_step("Работа с полезными ссылками")
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Полезные ссылки").click()
        page.get_by_role("link", name="МАРТ").click()
        page.get_by_role("link", name="Минжилкомхоз").click()
        page.locator("#navigation").get_by_role("link", name="Минсельхозпрод").click()
        page.locator("#navigation").get_by_role("link", name="Республиканская").click()
        page.get_by_role("link", name="Бизнес-Инфо").click()

        # Словарь
        request_handler.set_current_step("Работа со словарем")
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Словарь").click()
        page.get_by_role("link", name="В", exact=True).click()
        page.get_by_role("link", name="К", exact=True).click()
        page.get_by_role("link", name="Ч", exact=True).click()
        page.get_by_role("link", name="G").click()
        page.get_by_role("link", name="4", exact=True).click()
        page.get_by_role("link", name="Р", exact=True).click()
        page.get_by_role("link", name="Щ", exact=True).click()
        page.get_by_role("link", name="Я", exact=True).click()
        page.get_by_role("link", name="Э", exact=True).click()
        page.get_by_role("link", name="Эквивалентная доза").click()
        page.get_by_role("link", name="Все термины").click()
        page.locator("#navigation").get_by_role("link", name="3").click()
        page.get_by_role("link", name="3D-принтер").click()
        page.get_by_role("link", name="Пункт").click()

        # Проверка результатов
        logging.info(request_handler.get_requests_summary())
        request_handler.assert_all_responses_successful()

    except AssertionError as e:
        logging.error(request_handler.get_requests_summary())
        ScreenshotManager.take_screenshot(page, "assertion_error")
        logging.error(f"Ошибка произошла на шаге: {request_handler.current_step}")
        logging.error(f"Последний успешный URL: {request_handler.get_last_successful_url()}")
        raise e
    except Exception as e:
        logging.error(f"Неожиданная ошибка в тесте: {str(e)}")
        ScreenshotManager.take_screenshot(page, "error_screenshot")
        logging.error(f"Ошибка произошла на шаге: {request_handler.current_step}")
        logging.error(f"Последний успешный URL: {request_handler.get_last_successful_url()}")
        raise