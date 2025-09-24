# smoke_test_burger_menu_part1.py

import pytest
import os
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

def test_run_part1(browser_fixture):
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

        # Навигация по профилю и новостям
        request_handler.set_current_step("Навигация по новостям")
        page.goto(f"{Config.BaseUrl}/")
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Новости").click()
        page.get_by_role("link", name="за неделю").click()
        page.get_by_role("link", name="за месяц").click()

        # Фильтрация новостей
        request_handler.set_current_step("Фильтрация новостей")
        page.get_by_text("Промышленность и производство").click()
        page.get_by_text("Экология").click()
        page.get_by_text("Экономика и финансы").click()
        page.get_by_role("button", name="Найти").click()
        page.get_by_role("link", name="Подписаться на рассылку").click()

        # Переход к справочной информации
        request_handler.set_current_step("Работа со справочной информацией")
        page.goto(f"{Config.BaseUrl}/news?dateFrom=01.10.2024&dateTo=01.11.2024&partition%5B%5D=3&partition%5B%5D=4&partition%5B%5D=10")
        page.goto(f"{Config.BaseUrl}/")
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Справочная информация").click()
        page.get_by_role("link", name="Настроить напоминания").click()
        page.go_back()
        page.get_by_role("link", name="Базовая арендная величина").click()
        page.go_back()
        page.get_by_role("link", name="Календарь плательщика страховых взносов на 2024 год").click()
        page.go_back()
        page.get_by_role("link", name="Минимальная заработная плата").click()
        page.go_back()
        page.get_by_role("link", name="Размеры социальных стипендий").click()
        page.go_back()
        page.get_by_role("link", name="Производственный календарь").click()
        page.go_back()
        page.goto(f"{Config.BaseUrl}/")
        page.locator(".menu-btn").click()

        # Навигация по кодексам
        request_handler.set_current_step("Работа с кодексами")
        page.get_by_role("banner").get_by_role("link", name="Кодексы").click()
        page.get_by_role("link", name="Налоговый кодекс Республики Беларусь (Общая часть)").click()
        page.go_back()
        page.get_by_role("link", name="Трудовой кодекс Республики Беларусь").click()
        page.go_back()
        page.get_by_role("link", name="Банковский кодекс Республики Беларусь").click()
        page.go_back()
        page.get_by_role("link", name="Жилищный кодекс Республики Беларусь").click()

        # Работа с документом
        request_handler.set_current_step("Работа с документом")
        page.get_by_role("link", name="Карточка документа").click()
        page.get_by_role("link", name="Текст документа").click()

        # Сравнение редакций
        request_handler.set_current_step("Сравнение редакций")
        page.goto(f"{Config.BaseUrl}/")
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Кодексы").click()
        page.get_by_role("link", name="Банковский кодекс Республики Беларусь").click()
        page.get_by_role("link", name="Сравнение редакций").click()
        page.locator("select[name=\"v2\"]").select_option("20")
        page.get_by_role("button", name="Сравнить").click()

        # Горячие темы
        request_handler.set_current_step("Просмотр горячих тем")
        page.goto(f"{Config.BaseUrl}/")
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Горячие темы").click()

        # Проверка результатов
        logging.info(request_handler.get_requests_summary())
        request_handler.assert_all_responses_successful()

    except AssertionError as e:
        logging.error(request_handler.get_requests_summary())
        ScreenshotManager.take_screenshot(page, "assertion_error")
        raise e
    except Exception as e:
        logging.error(f"Неожиданная ошибка в тесте: {str(e)}")
        ScreenshotManager.take_screenshot(page, "error_screenshot")
        logging.error(f"Последний успешный URL: {request_handler.get_last_successful_url()}")
        logging.error(f"Ошибка произошла на шаге: {request_handler.current_step}")
        raise
