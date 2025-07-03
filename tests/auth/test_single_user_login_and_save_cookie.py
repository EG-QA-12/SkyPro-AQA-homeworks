"""
Эталонный тест авторизации через UI с сохранением куки для одного или всех пользователей из creds.env.

- По умолчанию (AUTH_MODE=all) авторизует всех пользователей (admin, moderator, expert, user)
- Если AUTH_MODE=one — авторизует только admin
- Для каждого пользователя отдельный assert с пояснением в логе
- Для запуска всех пользователей:
    pytest tests/integration/test_single_user_login_and_save_cookie.py --headed -v -s
- Для запуска только admin:
    AUTH_MODE=one pytest tests/integration/test_single_user_login_and_save_cookie.py --headed -v -s

- Все параметры берутся из creds.env
"""

from dotenv import load_dotenv
import pytest
import os
from playwright.sync_api import Browser
from pathlib import Path
from framework.utils.auth_utils import save_cookie, get_cookie_path
from framework.utils.url_utils import add_allow_session_param, is_headless
from framework.utils.db_helpers import update_user_in_db

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../creds.env'))

@pytest.mark.integration
def test_login_and_save_cookies(browser: Browser) -> None:
    """
    Эталонный тест авторизации через UI с сохранением куки для одного или всех пользователей.
    Режим определяется переменной окружения AUTH_MODE: 'all' (по умолчанию) или 'one'.
    """
    mode = os.getenv("AUTH_MODE", "all").lower()
    if mode == "one":
        users = [
            (os.getenv("ADMIN_AUTH_USERNAME"), os.getenv("ADMIN_AUTH_PASSWORD"), "admin")
        ]
    else:
        users = [
            (os.getenv("ADMIN_AUTH_USERNAME"), os.getenv("ADMIN_AUTH_PASSWORD"), "admin"),
            (os.getenv("MODERATOR_AUTH_USERNAME"), os.getenv("MODERATOR_AUTH_PASSWORD"), "moderator"),
            (os.getenv("EXPERT_AUTH_USERNAME"), os.getenv("EXPERT_AUTH_PASSWORD"), "expert"),
            (os.getenv("USER_AUTH_USERNAME"), os.getenv("USER_AUTH_PASSWORD"), "user")
        ]
    domain = os.getenv("AUTH_DOMAIN", "ca.bll.by")
    for username, password, role in users:
        if not username or not password:
            pytest.skip(f"Пропускаем {role}: не заданы переменные для логина/пароля")
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto(add_allow_session_param(f"https://{domain}/login", is_headless()), timeout=20000)
            page.fill("input[name='login'], input[name='email'], #login", username)
            page.fill("input[type='password'], input[name='password'], #password", password)
            page.click("button[type='submit'], input[type='submit'], button:has-text('Войти')")
            page.wait_for_selector(".user-in__nick", timeout=15000)
            nickname = page.locator(".user-in__nick").text_content().strip()
            print(f"[INFO] Авторизация {role}: найден никнейм '{nickname}' на странице.")
            assert nickname == username, f"[ASSERT FAIL] Для пользователя {role}: ожидали никнейм '{username}', а получили '{nickname}'"
            print(f"[ASSERT OK] Для пользователя {role}: никнейм совпадает с логином.")
            # Сохраняем куку после успешной авторизации
            save_cookie(context, str(get_cookie_path(role)))
            print(f"[INFO] Кука для {role} сохранена в {get_cookie_path(role)}")
            # Обновляем информацию о пользователе в БД
            update_user_in_db(
                login=username,
                role=role,
                subscription=os.getenv(f"{role.upper()}_SUBSCRIPTION", "basic"),
                cookie_file=str(get_cookie_path(role))
            )
        except Exception as e:
            screenshot_path = Path(f"auth_fail_{role}.png")
            page.screenshot(path=str(screenshot_path))
            print(f"[ERROR] Не удалось найти никнейм для {role}. Скриншот сохранён: {screenshot_path}")
            raise
        finally:
            context.close() 