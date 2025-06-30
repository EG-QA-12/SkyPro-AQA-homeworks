"""
Тесты авторизации через cookie для сайта ca.bll.by.

Этот модуль содержит тесты, проверяющие возможность авторизации на сайте
с помощью заранее сохраненных cookie-файлов.
"""


import logging
from pathlib import Path
import pytest
from playwright.sync_api import expect, Page

# Импортируем вспомогательные функции из модуля helpers
from framework.utils.cookie_helper import get_cookie_files, parse_auth_cookie

# Настройка логирования
logger = logging.getLogger(__name__)

# --- Константы для теста ---
LOGIN_URL = "https://ca.bll.by/login"
TARGET_DOMAIN = "ca.bll.by"


def pytest_addoption(parser):
    """
    Регистрируем кастомные опции командной строки для pytest.
    
    Эта функция позволяет добавлять собственные аргументы командной строки,
    которые можно использовать при запуске тестов.
    
    Args:
        parser: Парсер аргументов pytest.
    """
    parser.addoption("--cookie-file", action="store", default=None,
                     help="Путь к cookie-файлу или 'all' для всех файлов")


def pytest_generate_tests(metafunc):
    """
    Генерируем тесты на основе параметров командной строки.
    
    Эта функция динамически параметризует тесты в зависимости от
    переданных аргументов командной строки.
    
    Args:
        metafunc: Объект метафункции pytest.
    """
    if "cookie_file" in metafunc.fixturenames:
        cookie_file_option = metafunc.config.getoption("--cookie-file")
        limit = metafunc.config.getoption("limit")

        if cookie_file_option == "all":
            # Получаем все файлы cookies в директории
            cookies_dir = Path(__file__).parent.parent / 'cookies'
            cookie_files = get_cookie_files(cookies_dir, '*_cookies.json')
        elif cookie_file_option:
            # Разделяем строку по запятым, если передано несколько файлов
            cookies_dir = Path(__file__).parent.parent / 'cookies'
            file_names = [name.strip() for name in cookie_file_option.split(",")]
            cookie_files = [cookies_dir / name for name in file_names]
        else:
            cookie_files = []
        
        if not cookie_files:
            pytest.skip("Не найдено cookie-файлов для теста.")

        # Если задан лимит и он меньше общего числа файлов, берем случайную выборку
        if limit and limit > 0 and len(cookie_files) > limit:
            print(f"Выбрано {limit} случ. файлов из {len(cookie_files)}.")
            cookie_files = random.sample(cookie_files, limit)

        # Создаем понятные ID для каждого теста (имя файла)
        ids = [file.name for file in cookie_files]
        metafunc.parametrize("cookie_file", cookie_files, ids=ids)


# Тест

def test_auth_with_cookie(page: Page, cookie_file: Path):
    """
    Тестирует авторизацию на сайте, используя один cookie-файл.
    
    Этот тест запускается отдельно для каждого файла. Он выполняет следующие шаги:
    1. Загружает авторизационный cookie из файла.
    2. Переходит на страницу входа.
    3. Добавляет cookie в контекст браузера.
    4. Переходит на главную страницу.
    5. Проверяет наличие элемента с ником пользователя.
    
    Args:
        page: Фикстура Playwright Page, предоставляемая pytest-playwright.
        cookie_file: Путь к cookie-файлу.
    """
    auth_cookie = parse_auth_cookie(cookie_file, TARGET_DOMAIN)
    assert auth_cookie, f"Не найдена auth-cookie в файле: {cookie_file.name}"

    # Логируем cookie для отладки
    logger.info(f"[{cookie_file.name}] Используем cookie: {auth_cookie}")

    # Playwright Page уже создана фикстурой, просто используем её
    page.goto(LOGIN_URL)  # Сначала переходим на страницу
    page.context.add_cookies([auth_cookie])  # Добавляем куки
    logger.info(f"[{cookie_file.name}] Куки в контексте браузера после добавления: "
                f"{page.context.cookies()}")

    # Переходим на главную страницу и ждем загрузки
    logger.info(f"[{cookie_file.name}] Переход на главную страницу и ожидание сетевой стабильности.")
    page.goto("https://ca.bll.by/", wait_until="networkidle")

    # Проверяем, что элемент с ником пользователя виден
    user_nick = page.locator('div.user-in__nick')

    try:
        # Проверяем, что элемент видим на странице
        expect(user_nick).to_be_visible(timeout=10000)
        logger.info(f"Успешная авторизация с файлом: {cookie_file.name}")

    except AssertionError:
        # Сохраняем скриншот и HTML страницы для отладки при ошибке
        log_base = cookie_file.name.replace('.json', '')
        screenshot_path = f"screenshots/{log_base}_debug.png"
        html_path = f"screenshots/{log_base}_debug.html"
        page.screenshot(path=screenshot_path)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page.content())
        logger.error(f"Ошибка авторизации с файлом: {cookie_file.name}")
        logger.error(f"Скриншот сохранен: {screenshot_path}")
        logger.error(f"HTML сохранен: {html_path}")
        raise
