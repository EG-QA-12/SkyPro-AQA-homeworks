"""Тесты авторизации (выделены в отдельный пакет `auth`).

Запуск только этих тестов:
    pytest -m auth
"""

import os
import pytest
from pathlib import Path
from playwright.sync_api import Page
from framework.utils.auth_utils import save_cookie, load_cookie
from framework.utils.cookie_helper import parse_auth_cookie

# Все тесты в этом модуле помечаем как 'auth', чтобы их можно было запускать выборочно.
pytestmark = pytest.mark.auth

# Константы
COOKIE_DIR = Path(os.getenv("COOKIE_DIR", "d:/Bll_tests/cookies"))
TARGET_DOMAIN = "bll.by"
# Используем базовый URL главной страницы, т.к. после установки куки
# проверяем элементы, видимые в шапке сайта.
LOGIN_URL = os.getenv("LOGIN_URL", "https://ca.bll.by")


# Получаем список файлов с cookie
cookie_files = [file for file in COOKIE_DIR.glob("*_cookies.json")]
cookie_file_ids = [file.name for file in cookie_files]

# Если нет файлов с cookie, пропускаем тесты
if not cookie_files:
    pytest.skip(
        "Не найдено ни одного файла с cookie для тестирования.",
        allow_module_level=True,
    )


@pytest.mark.parametrize("cookie_file_path", cookie_files, ids=cookie_file_ids)
def test_login_with_cookie(page: Page, cookie_file_path: Path):
    """Проверяет успешную авторизацию с использованием cookie."""
    # Загружаем куку из файла
    try:
        auth_cookie = parse_auth_cookie(cookie_file_path, TARGET_DOMAIN)
    except (FileNotFoundError, ValueError) as err:
        pytest.fail(f"Ошибка подготовки cookie: {err}")
    
    # Переходим на страницу логина
    page.goto(LOGIN_URL)
    
    # Устанавливаем куку
    page.context.add_cookies([auth_cookie])
    
    # Переходим на главную страницу вместо перезагрузки страницы логина
    page.goto("https://ca.bll.by", wait_until="networkidle")
    
    # Wait for potential redirect or element state
    page.wait_for_load_state('networkidle')

    # Check for successful authorization
    current_url = page.url
    if current_url == 'https://ca.bll.by/user/profile':
        assert True, "Редирект на профиль успешен"
    else:
        assert not page.is_visible('label[for="agree"]'), "Элемент 'label[for=\"agree\"]' видим, авторизация не удалась"

    # Optionally, check for other elements if needed
    # Проверяем элементы интерфейса
    assert page.is_visible('div.profile-top__ttl'), "Элемент 'Мои данные' не найден, авторизация не удалась"
    assert page.is_visible("#logout-btn"), "Не найдена кнопка выхода"

    # Сохраняем дополнительную отладку (URL, скрин, часть HTML)
    print(f"\nURL после перезагрузки: {page.url}")
    screenshot_dir = Path("screenshots")
    screenshot_dir.mkdir(exist_ok=True)
    shot_path = screenshot_dir / f"auth_{cookie_file_path.stem}.png"
    page.screenshot(path=str(shot_path))
    print(f"Скриншот сохранён: {shot_path}")
    print("HTML (первые 500 символов):", page.content()[:500], "…")
