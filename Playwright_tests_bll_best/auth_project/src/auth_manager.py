import json
import logging
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

DATA_DIR = Path(__file__).parent.parent / 'data'
COOKIES_PATH = DATA_DIR / 'cookies.json'
CREDS_PATH = DATA_DIR / 'creds.env'

load_dotenv(dotenv_path=CREDS_PATH)

LOGIN_URL = "https://ca.bll.by/login"
TARGET_URL = "https://ca.bll.by/"


def get_credentials():
    login = os.getenv('LOGIN')
    password = os.getenv('PASSWORD')
    if not login or not password:
        raise ValueError("LOGIN и/или PASSWORD не заданы в data/creds.env")
    return login, password


def save_cookies(context, login):
    cookies = context.cookies()
    auth_cookie = next((c for c in cookies if c["name"] == "bii_auth_session"), None)
    remember_cookie = next((c for c in cookies if "remember_web_" in c["name"]), None)
    data = {
        "login": login,
        "bii_auth_session": auth_cookie["value"] if auth_cookie else "",
        "remember_key": remember_cookie["name"] if remember_cookie else "",
        "remember_value": remember_cookie["value"] if remember_cookie else ""
    }
    with open(COOKIES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Cookies сохранены для пользователя {login}")


def load_cookies():
    if not COOKIES_PATH.exists():
        return None
    with open(COOKIES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def authorize_and_save_cookies():
    login, password = get_credentials()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(LOGIN_URL)
        page.get_by_label("Логин").fill(login)
        page.get_by_label("Пароль (чувствителен к регистру)").fill(password)
        page.get_by_role("button", name="Войти").click()
        user_nick_locator = f"//div[@class='user-in__nick' and text()='{login}']"
        page.wait_for_selector(user_nick_locator, timeout=10000)
        print(f"Авторизация успешна для пользователя: {login}")
        page.reload()
        page.wait_for_timeout(2000)
        save_cookies(context, login)
        browser.close()


def set_cookies_and_open():
    cookies = load_cookies()
    if not cookies:
        raise RuntimeError("Нет сохранённых кук. Сначала выполните авторизацию.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.add_cookies([
            {
                "name": "bii_auth_session",
                "value": cookies["bii_auth_session"],
                "domain": "ca.bll.by",
                "path": "/",
                "httpOnly": True,
                "secure": True,
            },
            {
                "name": cookies["remember_key"],
                "value": cookies["remember_value"],
                "domain": "ca.bll.by",
                "path": "/",
                "httpOnly": True,
                "secure": True,
            } if cookies["remember_key"] else None
        ])
        page = context.new_page()
        page.goto(TARGET_URL)
        login = cookies["login"]
        user_nick_locator = f"//div[@class='user-in__nick' and text()='{login}']"
        if page.locator(user_nick_locator).is_visible():
            print(f"Вход по кукам успешен для пользователя: {login}")
        else:
            print(f"Вход по кукам не удался для пользователя: {login}")
        browser.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Авторизация и работа с куками")
    parser.add_argument('--auth', action='store_true', help='Выполнить авторизацию и сохранить куки')
    parser.add_argument('--use-cookies', action='store_true', help='Войти с помощью сохранённых кук')
    args = parser.parse_args()
    if args.auth:
        authorize_and_save_cookies()
    elif args.use_cookies:
        set_cookies_and_open()
    else:
        print("Используйте --auth для авторизации или --use-cookies для входа по кукам")
