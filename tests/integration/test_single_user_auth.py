"""
Тест базовой авторизации через UI с сохранением куки и записью в БД.

- Логин и пароль берутся из creds.env (или переменных окружения)
- Авторизация через UI (Playwright)
- Проверка успешного входа по нику на странице профиля
- Сохранение куки в cookies/<login>_cookies.json
- Обновление записи в БД LiteSQL (login, role, subscription, cookie_file, last_cookie_update)
- Тест падает при любой ошибке авторизации

Этот тест служит эталоном для сценариев single-user авторизации.
"""
import os
from pathlib import Path
from typing import Any
import pytest
from playwright.sync_api import sync_playwright, Page
from framework.app.pages.login_page import LoginPage
from framework.db_utils.database_manager import DatabaseManager

# Импортируем функцию получения логина/пароля (реализуйте в framework/utils/auth_utils или аналоге)
def get_credentials() -> tuple[str, str]:
    """
    Получает логин и пароль из переменных окружения или creds.env.
    """
    login = os.environ.get("LOGIN")
    password = os.environ.get("PASS")
    if not login or not password:
        raise ValueError("LOGIN и/или PASS не заданы в переменных окружения или creds.env")
    return login, password

# Импортируйте роль/подписку из конфига или задайте вручную для single-user
def get_user_role_and_subscription(login: str) -> tuple[str, str]:
    """
    Возвращает роль и подписку пользователя (можно доработать под свои нужды).
    """
    # Для single-user теста можно захардкодить или получить из env/конфига
    return "admin", "basic"

@pytest.mark.integration
def test_single_user_authorization_and_cookie(tmp_path: Path) -> None:
    """
    Тестирует авторизацию одного пользователя через UI, сохраняет куки и обновляет БД.

    Args:
        tmp_path (Path): Временная директория pytest (не используется, но может пригодиться для отладки)

    Raises:
        AssertionError: Если авторизация не удалась или куки не сохранены
    """
    # 1. Получаем логин и пароль
    login, password = get_credentials()
    role, subscription = get_user_role_and_subscription(login)

    # 2. Готовим путь для cookies
    cookies_dir = Path("cookies")
    cookies_dir.mkdir(exist_ok=True)
    cookie_file = cookies_dir / f"{login}_cookies.json"

    # 3. Запускаем браузер и авторизуемся через UI
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page: Page = context.new_page()
        login_page = LoginPage(page)
        page.goto("https://ca.bll.by/login", timeout=30000)
        login_page.fill_username(login)
        login_page.fill_password(password)
        login_page.click_submit()
        page.goto("https://ca.bll.by/user/profile", timeout=30000)
        # Проверяем, что ник на странице совпадает с логином
        nickname_locator = page.locator("div.user-in__nick")
        assert nickname_locator.is_visible(timeout=5000), "Ник пользователя не найден на странице профиля"
        actual_nick = nickname_locator.inner_text().strip()
        assert actual_nick == login, f"Ожидали ник '{login}', а получили '{actual_nick}'"
        # 4. Сохраняем куки в файл
        cookies = context.cookies()
        import json
        with open(cookie_file, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        assert cookie_file.exists(), f"Файл куки не создан: {cookie_file}"
        # 5. Обновляем запись в БД
        with DatabaseManager() as db:
            db.add_or_update_user(
                login=login,
                role=role,
                subscription=subscription,
                cookie_file=str(cookie_file)
            )
        # 6. Проверяем, что запись в БД обновилась
        with DatabaseManager() as db:
            user = db.get_user(login)
            assert user is not None, "Пользователь не найден в БД после авторизации"
            assert user["cookie_file"] == str(cookie_file), "Путь к куке в БД не совпадает с сохранённым"
        context.close()
        browser.close() 