# smoke_test_burger_menu_part3.py

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

def test_run_part3(browser_fixture):
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

        # Личный юрист
        request_handler.set_current_step("Работа с разделом 'Личный юрист'")
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Ваш личный юрист").click()
        page.get_by_role("link", name="1.1.", exact=True).click()
        page.get_by_role("link", name="1.2.", exact=True).click()
        page.get_by_role("link", name="5.4.").click()
        page.get_by_role("link", name="27.").click()
        page.get_by_role("link", name="Бизнес-Инфо", exact=True).click()

        # Закупки
        request_handler.set_current_step("Работа с разделом 'Закупки'")
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Закупки").click()
        page.get_by_role("link", name="Инструкция").click()
        page.get_by_role("link", name="Бизнес-Инфо", exact=True).click()

        # Поиск и фильтры
        request_handler.set_current_step("Работа с поиском и фильтрами")
        page.locator(".menu-btn").click()
        page.get_by_role("link", name="Поиск в базе документов").click()
        page.locator("#kind_ids-ts-control").click()
        page.get_by_role("option", name="Закон Республики Беларусь").click()

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