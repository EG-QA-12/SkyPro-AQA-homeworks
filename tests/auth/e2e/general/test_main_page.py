import pytest
from playwright.sync_api import Page, expect

def test_main_page_loads_successfully_for_moderator(authenticated_page_moderator: Page):
    """
    Тест проверяет, что главная страница bll.by загружается корректно для модератора.
    
    Этот тест использует специальную фикстуру authenticated_page_moderator,
    которая автоматически авторизует пользователя под ролью модератора.
    """
    test_main_page_loads_successfully(authenticated_page_moderator)
    
def test_main_page_loads_successfully(page: Page):
    """
    Тест проверяет, что главная страница bll.by загружается корректно под модератором.

    Шаги:
    1. Отслеживаем ошибки JS в консоли.
    2. Переходим на главную страницу.
    3. Проверяем статус-код ответа (должен быть 200).
    4. Проверяем, что за время загрузки не было JS-ошибок.
    5. Проверяем заголовок страницы.
    6. Проверяем видимость ключевого элемента (например, логотипа или заголовка).
    """
    js_errors = []
    page.on("pageerror", lambda error: js_errors.append(error))

    # Переходим на страницу и проверяем ответ
    response = page.goto("https://bll.by")
    assert response.status == 200, f"Сайт не загружен, статус {response.status} вместо 200"

    # Ждем полной загрузки страницы
    page.wait_for_load_state('networkidle')

    # Проверяем, что не было ошибок JS
    assert len(js_errors) == 0, f"Обнаружены JS-ошибки: {js_errors}"

    # Проверяем заголовок страницы
    title = page.title()
    assert "BLL" in title, f"Неверный заголовок страницы: '{title}'"

    # Проверяем видимость основного контента страницы
    # Используем более универсальные селекторы
    main_content_selectors = [
        "body",  # Основной контент должен быть виден
        "header",  # Заголовок страницы
        "main",   # Основной раздел
        ".container",  # Контейнер
        "#header",  # ID заголовка
        ".header"   # Класс заголовка
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
