"""
E2E тесты доступа к главной странице для разных типов пользователей.

Данные тесты проверяют полные пользовательские сценарии:
- Загрузка главной страницы с проверкой всех элементов
- Отсутствие JS ошибок
- Корректное отображение контента
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect
import allure
from framework.utils.url_utils import add_allow_session_param, is_headless

# Импортируем утилиты Allure из корневой директории
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from framework.utils.reporting.allure_utils import ui_test, AllureReporter


@ui_test(
    title="Модератор успешно загружает главную страницу",
    description="E2E сценарий: авторизованный модератор открывает главную страницу и проверяет корректность загрузки",
    feature="Главная страница"
)
@pytest.mark.smoke
@pytest.mark.user_journey
def test_main_page_loads_successfully_for_moderator(authenticated_page_moderator: Page) -> None:
    """
    E2E тест: Модератор успешно загружает главную страницу.
    
    Пользовательский сценарий:
    1. Модератор авторизован в системе
    2. Переходит на главную страницу
    3. Страница загружается без ошибок
    4. Весь контент отображается корректно
    
    Args:
        authenticated_page_moderator: Страница с авторизацией модератора.
    """
    test_main_page_loads_successfully(authenticated_page_moderator)


@ui_test(
    title="Анонимный пользователь успешно загружает главную страницу",
    description="E2E сценарий: неавторизованный пользователь открывает главную страницу и проверяет доступность публичного контента",
    feature="Главная страница"
)
@pytest.mark.smoke
@pytest.mark.user_journey 
def test_main_page_loads_successfully_for_anonymous(page: Page) -> None:
    """
    E2E тест: Анонимный пользователь успешно загружает главную страницу.
    
    Пользовательский сценарий:
    1. Неавторизованный пользователь заходит на сайт
    2. Переходит на главную страницу
    3. Страница загружается без ошибок
    4. Публичный контент отображается корректно
    
    Args:
        page: Страница браузера без авторизации.
    """
    test_main_page_loads_successfully(page)


def test_main_page_loads_successfully(page: Page) -> None:
    """
    Базовая проверка загрузки главной страницы.

    Проверяет:
    1. Отслеживание JS ошибок в консоли
    2. Успешный HTTP статус-код (200)
    3. Полную загрузку страницы
    4. Отсутствие JS ошибок
    5. Корректный заголовок страницы
    6. Видимость основного контента

    Args:
        page: Страница браузера для тестирования.
    """
    js_errors = []
    page.on("pageerror", lambda error: js_errors.append(error))

    # Переходим на страницу и проверяем ответ  
    main_url = add_allow_session_param("https://bll.by", is_headless())
    response = page.goto(main_url)
    assert response is not None, "Не получен ответ от сервера"
    assert response.status == 200, f"Сайт не загружен, статус {response.status} вместо 200"

    # Ждем полной загрузки страницы
    page.wait_for_load_state('networkidle')

    # Проверяем, что не было ошибок JS
    assert len(js_errors) == 0, f"Обнаружены JS-ошибки: {js_errors}"

    # Обновленная проверка заголовка
    title = page.title()
    assert "Бизнес-Инфо" in title, f"Неверный заголовок страницы: '{title}'"

    # Проверяем видимость основного контента страницы
    main_content_selectors = [
        "body",        # Основной контент должен быть виден
        "header",      # Заголовок страницы
        "main",        # Основной раздел
        ".container",  # Контейнер
        "#header",     # ID заголовка
        ".header"      # Класс заголовка
    ]
    
    content_found = False
    for selector in main_content_selectors:
        try:
            if page.is_visible(selector):
                content_found = True
                break
        except Exception:
            continue
            
    assert content_found, "Основной контент страницы не найден или не виден"



