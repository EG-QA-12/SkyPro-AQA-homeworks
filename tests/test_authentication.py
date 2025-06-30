"""
Тесты аутентификации через cookie.
"""


import pytest
from pathlib import Path
from playwright.sync_api import Page, expect
from typing import List

# Импортируем наши вспомогательные функции
from framework.utils.cookie_helper import get_cookie_files, parse_auth_cookie

# --- Конфигурация теста ---
# Определяем базовые URL и пути здесь, чтобы их было легко изменить.
BASE_URL = "https://ca.bll.by"
LOGIN_URL = f"{BASE_URL}/login"
# Путь к папке с cookie. pathlib.Path гарантирует кросс-платформенность.
# ВАЖНО: Укажите ваш реальный путь к папке.
# Пример для Windows: Path("d:/Bll_tests/cookies/")
# Пример для Linux/MacOS: Path("/home/user/Bll_tests/cookies/")
COOKIES_DIR = Path("d:/Bll_tests/cookies/")
# Домен, для которого мы устанавливаем cookie
TARGET_DOMAIN = "ca.bll.by"
# Имя пользователя, которое мы ожидаем увидеть после успешного входа
EXPECTED_NICKNAME = "EvgenQA"

# --- Сбор данных для параметризации ---
# Находим все файлы с cookie ПЕРЕД запуском тестов.
# Pytest использует этот список для создания отдельных тестовых случаев.
cookie_files: List[Path] = get_cookie_files(COOKIES_DIR, "*_cookies.json")

# Создаем понятные ID для тестов. Вместо полного пути к файлу
# в отчете будет отображаться только имя файла (например, '283_cookies.json').
cookie_file_ids: List[str] = [path.name for path in cookie_files]

# --- Тест ---

# Пропускаем все тесты в этом файле, если не найдено ни одного cookie-файла.
# Это лучше, чем падение тестов с ошибкой.
if not cookie_files:
    pytest.skip("Не найдено ни одного файла с cookie для тестирования.", allow_module_level=True)


@pytest.mark.parametrize("cookie_file_path", cookie_files, ids=cookie_file_ids)
def test_login_with_cookie(page: Page, cookie_file_path: Path):
    """
    Проверяет успешную авторизацию на сайте с использованием cookie из файла.

    Этот тест выполняет следующие шаги:
    1. Получает путь к файлу с cookie (благодаря параметризации).
    2. Парсит файл, чтобы извлечь авторизационный cookie.
    3. Открывает страницу входа, чтобы браузер "знал" домен.
    4. Добавляет cookie в контекст браузера.
    5. Перезагружает страницу.
    6. Проверяет, что на странице появился элемент с никнеймом пользователя,
       что подтверждает успешную авторизацию.

    Args:
        page (Page): Фикстура Playwright, предоставляющая доступ к странице браузера.
        cookie_file_path (Path): Путь к файлу с cookie для текущего тестового запуска.
                                 Этот аргумент поставляется Pytest'ом.
    """
    # Шаг 1: Парсинг cookie из файла
    # Используем наш helper, чтобы получить cookie в формате, готовом для Playwright.
    try:
        auth_cookie = parse_auth_cookie(cookie_file_path, TARGET_DOMAIN)
    except (FileNotFoundError, ValueError) as e:
        # Если helper не смог найти файл или cookie, тест должен упасть
        # с понятным сообщением об ошибке.
        pytest.fail(f"Ошибка подготовки cookie: {e}")

    # Шаг 2: Навигация и установка cookie
    # Сначала заходим на сайт, чтобы установить домен для контекста.
    page.goto(LOGIN_URL)
    
    # Добавляем наш подготовленный cookie в браузер.
    # Playwright требует передавать cookie в виде списка.
    page.context.add_cookies([auth_cookie])

    # Шаг 3: Перезагрузка страницы и проверка результата
    # Перезагружаем страницу. Теперь сервер должен получить наш cookie
    # и считать нас авторизованным пользователем.
    page.reload()

    # Шаг 4: Проверка (Assertion)
    # Это ключевой момент. Мы ищем элемент с никнеймом.
    # Мы используем локатор '.user-in__nick'.
    user_nick_locator = page.locator(".user-in__nick")

    # Используем явные ожидания Playwright.
    # 1. Проверяем, что элемент видим на странице.
    #    `to_be_visible` будет ждать появления элемента в течение таймаута.
    expect(user_nick_locator).to_be_visible(timeout=10000)
    
    # 2. Проверяем, что текст внутри элемента соответствует ожидаемому.
    expect(user_nick_locator).to_have_text(EXPECTED_NICKNAME)

    # Если обе проверки прошли успешно, тест считается пройденным.
    # Можно добавить информационное сообщение в лог для наглядности.
    print(f"\nУспешная авторизация с файлом: {cookie_file_path.name}")
