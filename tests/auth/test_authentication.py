"""Тесты авторизации (выделены в отдельный пакет `auth`).

Запуск только этих тестов:
    pytest -m auth
"""

import os
import pytest
from pathlib import Path
from playwright.sync_api import Page

# Все тесты в этом модуле помечаем как 'auth', чтобы их можно было запускать выборочно.
pytestmark = pytest.mark.auth

# Импортируем наши вспомогательные функции
from framework.utils.cookie_helper import get_cookie_files, parse_auth_cookie

# Константы
COOKIE_DIR = Path(os.getenv("COOKIE_DIR", "d:/Bll_tests/cookies"))
TARGET_DOMAIN = "ca.bll.by"
LOGIN_URL = "https://ca.bll.by/login"

# Получаем список файлов с cookie
cookie_files = get_cookie_files(COOKIE_DIR, "*_cookies.json")
cookie_file_ids = [file.name for file in cookie_files]

# Если нет файлов с cookie, пропускаем тесты
if not cookie_files:
    pytest.skip(
        "Не найдено ни одного файла с cookie для тестирования.",
        allow_module_level=True,
    )


@pytest.mark.parametrize("cookie_file_path", cookie_files, ids=cookie_file_ids)
def test_login_with_cookie(page: Page, cookie_file_path: Path):
    """Проверяет успешную авторизацию на сайте с использованием cookie.

    Шаги:
        1. Читаем куку из файла.
        2. Переходим на страницу входа.
        3. Добавляем куку в контекст.
        4. Перезагружаем и ждём загрузки.
        5. Проверяем, что появился хотя бы один из целевых элементов
           пользовательского меню.
    """

    # 1. Читаем куку
    try:
        auth_cookie = parse_auth_cookie(cookie_file_path, TARGET_DOMAIN)
    except (FileNotFoundError, ValueError) as err:
        pytest.fail(f"Ошибка подготовки cookie: {err}")

    # 2. Навигация и установка куки
    page.goto(LOGIN_URL)
    page.context.add_cookies([auth_cookie])

    # ========== Отладочная секция (можно убрать когда стабилизируется) ==========
    print("\nВсе куки после установки:")
    for c in page.context.cookies():
        print(f"{c['name']}: {c['value'][:15]}…")
    # ===========================================================================

    # 3. Перезагружаем страницу и ждём, пока сеть успокоится
    page.reload()
    page.wait_for_load_state("networkidle", timeout=10000)

    # 4. Сохраняем дополнительную отладку (URL, скрин, часть HTML)
    print(f"\nURL после перезагрузки: {page.url}")
    screenshot_dir = Path("screenshots")
    screenshot_dir.mkdir(exist_ok=True)
    shot_path = screenshot_dir / f"auth_{cookie_file_path.stem}.png"
    page.screenshot(path=str(shot_path))
    print(f"Скриншот сохранён: {shot_path}")
    print("HTML (первые 500 символов):", page.content()[:500], "…")

    # 5. Проверяем наличие хотя бы одного из подтверждающих селекторов
    selectors = [
        ".user-in__nick",
        "a.profile-menu__link-4",
        "a.profile-menu__link-5",
        ".profile-top__note",
    ]

    found = []
    for sel in selectors:
        try:
            page.wait_for_selector(sel, state="visible", timeout=5000)
            found.append(sel)
            print(f"✓ Найден элемент: {sel}")
        except Exception:
            print(f"✕ Не найден: {sel}")

    if not found:
        pytest.fail("Не найдено ни одного элемента подтверждения авторизации.")

    print(f"Успешная авторизация, подтверждающих элементов: {len(found)}")
