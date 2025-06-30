import logging
from pathlib import Path
import random

import pytest
from playwright.sync_api import expect, Page

from helpers.cookie_helper import get_cookie_files, parse_auth_cookie

logger = logging.getLogger(__name__)

# --- Константы для теста ---
LOGIN_URL = "https://ca.bll.by/login"
TARGET_DOMAIN = "ca.bll.by"


def get_cookie_file_list(option_value: str) -> list[Path]:
    """
    Собирает список cookie-файлов для теста на основе параметра --cookie-file.

    Args:
        option_value: Значение, переданное в --cookie-file.

    Returns:
        Список объектов Path к cookie-файлам.
    """
    # Путь к папке 'cookies' находится на уровень выше папки 'projects'
    cookies_dir = Path(__file__).parent.parent / 'cookies'

    if not option_value:
        pytest.skip("Параметр --cookie-file не был передан. Тест пропущен.")

    if option_value.lower() == 'all':
        return get_cookie_files(cookies_dir, '*_cookies.json')

    # Разбираем имена файлов, перечисленные через запятую
    file_names = [name.strip() for name in option_value.split(',')]
    return [cookies_dir / name for name in file_names]


def pytest_generate_tests(metafunc):
    """
    Хук Pytest для динамической параметризации.
    Запускает тест для каждого файла, найденного по параметру --cookie-file.
    Поддерживает ограничение --limit для запуска случайной выборки.
    """
    if "cookie_file" in metafunc.fixturenames:
        option_value = metafunc.config.getoption("cookie_file")
        limit = metafunc.config.getoption("limit")

        file_list = get_cookie_file_list(option_value)

        if not file_list:
            pytest.skip("Не найдено cookie-файлов для теста.")

        # Если задан лимит и он меньше общего числа файлов, берем случайную выборку
        if limit and limit > 0 and \
           len(file_list) > limit:
            print(f"Выбрано {limit} случ. файлов из {len(file_list)}.")
            file_list = random.sample(file_list, limit)

        # Создаем понятные ID для каждого теста (имя файла)
        ids = [file.name for file in file_list]
        metafunc.parametrize("cookie_file", file_list, ids=ids)


def test_auth_with_cookie(page: Page, cookie_file: Path):
    """
    Тестирует авторизацию на сайте, используя один cookie-файл.
    Этот тест запускается отдельно для каждого файла.

    Args:
        page: Фикстура Playwright Page, предоставляемая pytest-playwright.
        cookie_file: Путь к cookie-файлу (передается через параметризацию).
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

    # Перезагружаем страницу и ждем, пока она полностью не загрузится.
    # wait_until="networkidle" — это ключевой момент для стабильности.
    # Он гарантирует, что мы не начнем проверку, пока страница еще грузится.
    logger.info(f"[{cookie_file.name}] Перезагрузка страницы и ожидание сетевой стабильности.")
    page.goto("https://ca.bll.by/", wait_until="networkidle")

    # Проверяем, что элемент с ником пользователя виден
    user_nick = page.locator('div.user-in__nick')

    try:
        # 1. Проверяем, что элемент видим на странице.
        expect(user_nick).to_be_visible(timeout=10000)

        logger.info(f"Успешная авторизация с файлом: {cookie_file.name}")

    except AssertionError:
        # Если проверка не удалась, сохраняем артефакты для отладки
        log_base = cookie_file.name.replace('.json', '')
        screenshot_path = f"screenshots/{log_base}_debug.png"
        html_path = f"screenshots/{log_base}_debug.html"

        page.screenshot(path=screenshot_path)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page.content())
        # Перевыбрасываем исключение, чтобы тест был помечен как упавший
        raise
