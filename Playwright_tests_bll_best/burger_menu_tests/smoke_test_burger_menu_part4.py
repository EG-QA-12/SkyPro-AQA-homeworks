# smoke_test_burger_menu_part4.py

import pytest
import logging
from test_utils import (
    Config,
    RequestHandler,
    Auth,
    setup_logging,
    generate_random_text,
    ScreenshotManager
)


def test_run_part4(browser_fixture):
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

        # Проверка контрагента
        request_handler.set_current_step("Работа с проверкой контрагента")
        page.locator(".menu-btn").click()
        page.get_by_role("link", name="Проверка контрагента").click()
        page.get_by_placeholder("Введите УНП или название").click()
        page.get_by_placeholder("Введите УНП или название").fill("Лиза")
        page.get_by_text("Коллективное предприятия \"ЛИЗА\"").click()
        page.get_by_role("button", name="Проверить").click()

        # Избранное и напоминания
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Подборки и закладки").click()
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Документы на контроле").click()


        # Работа с напоминаниями
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Напоминания").click()
        page.get_by_text("Настройка напоминаний").click()
        page.get_by_role("link", name="Личные").click()
        page.get_by_role("link", name="Добавить").click()
        page.get_by_label("Дата (дд.мм.гггг)").click()
        page.get_by_label("Дата (дд.мм.гггг)").fill("10.11.2024")
        page.get_by_text("10", exact=True).click()
        page.get_by_role("combobox").select_option("weekly")
        page.get_by_placeholder("Введите текст").fill("Напоминание 1")
        page.get_by_text("Добавить напоминание Дата (дд.мм.гггг) Периодичность Нет Еженедельно Ежемесячно ").click()
        page.locator("input[value='Сохранить']").click()

        page.locator(".menu-btn").click()
        page.get_by_role("link", name="Напоминания").click()
        page.get_by_text("Настройка напоминаний").click()
        page.get_by_role("link", name="От «Бизнес-Инфо»").click()
        page.get_by_text("Выбрать все").first.click()
        page.get_by_text("Выбрать все").nth(3).click()
        page.get_by_role("button", name="Сохранить").nth(1).click()

        page.locator(".menu-btn").click()
        page.get_by_role("link", name="Напоминания").click()
        page.get_by_text("Настройка напоминаний").click()
        page.get_by_role("link", name="Личные").click()
        page.get_by_text("Выделить все").click()
        page.get_by_role("button", name="Удалить").click()
        page.get_by_role("link", name="Бизнес-Инфо").click()

        # Новые документы
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Новые документы").click()

        # Сообщество
        page.get_by_role("link", name="Бизнес-Инфо", exact=True).click()
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Задать вопрос").click()
        page.locator("[id=\"p\"]").fill(f"Тестовый вопрос (!!!подлежит удалению!!!) {generate_random_text()}")
        page.get_by_role("button", name="Опубликовать вопрос").click()

        # Мой профиль
        request_handler.set_current_step("Настройка профиля")
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Мои данные").click()
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Я эксперт").click()
        page.locator("label").first.click()
        page.locator("div:nth-child(2) > div > .prof-expert_list > div > .check-wrap > .profile-top__ttl").first.click()
        page.locator(
            "div:nth-child(2) > div:nth-child(2) > .prof-expert_list > div > .check-wrap > .profile-top__ttl").click()
        page.locator("form div").filter(
            has_text="Я эксперт После выбора нажмите кнопку Сохранить Сохранить").get_by_role("button").click()
        page.get_by_role("button", name="Сохранить").nth(1).click()

        request_handler.set_current_step("Настройка уведомлений")
        page.get_by_role("link", name="Бизнес-Инфо").click()
        page.locator(".menu-btn").click()
        page.get_by_role("link", name="Настройка уведомлений").click()
        page.get_by_label("На e-mail и на Главной").check()
        page.get_by_label("В Viber и на Главной").check()
        page.get_by_label("Только на Главной").check()
        page.get_by_text("ИТ", exact=True).click()
        page.get_by_text("Спорт", exact=True).click()
        page.get_by_text("Налог на прибыль").click()
        page.get_by_text("Охрана окружающей среды и природопользование").click()
        page.get_by_role("button", name="Сохранить").nth(1).click()
        page.locator(".menu-btn").click()
        page.get_by_role("banner").get_by_role("link", name="Личный кабинет").click()

        page.goto(f"{Config.BaseUrl}/")

        # Бонусы
        request_handler.set_current_step("Работа с бонусами")
        page.locator(".menu-btn").click()
        page.get_by_role("link", name="Бонусы").first.click()
        page.get_by_role("link", name="КАТАЛОГ БОНУСОВ").click()
        page.get_by_text("История заказов").click()
        page.get_by_text("Корзина").click()
        page.goto(f"{Config.BonusUrl}/")
        page.get_by_role("link", name="Заполните").click()
        page.goto(f"{Config.BonusUrl}/")
        page.get_by_role("link", name="Пройдите").click()
        page.goto(f"{Config.BonusUrl}/")
        page.get_by_role("link", name="Скачайте").click()
        page.goto(f"{Config.BonusUrl}/")
        page.get_by_role("link", name="Задайте").click()
        page.goto(f"{Config.BonusUrl}/")
        page.get_by_role("link", name="Ответьте").click()
        page.goto(f"{Config.BaseUrl}/")

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