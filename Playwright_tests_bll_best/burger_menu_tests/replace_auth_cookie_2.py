from playwright.sync_api import sync_playwright
import logging

# Файл с сохраненными куками
COOKIES_FILE = "Cookies_user.txt"

# Целевые URL
LOGIN_URL = "https://ca.bll.by/login"
LOGOUT_URL = "https://ca.bll.by/logout"
TARGET_URL = "https://ca.bll.by/"

def load_auth_cookies():
    """Загрузить куки bii_auth_session и remember_web из файла"""
    cookies = []
    try:
        with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(';')
                    if len(parts) == 4:
                        login, auth_cookie_value, remember_key, remember_value = parts
                        cookies.append({
                            "login": login.strip(),
                            "bii_auth_session": auth_cookie_value.strip(),
                            "remember_key": remember_key.strip(),
                            "remember_value": remember_value.strip()
                        })
        return cookies
    except Exception as e:
        logging.error(f"Error loading cookies: {e}")
        raise

def replace_cookies_and_verify():
    """Заменить куки и проверить авторизацию"""
    cookies = load_auth_cookies()
    if not cookies:
        logging.error("No valid cookies found!")
        return

    with sync_playwright() as p:
        # Запуск браузера
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        for cookie_data in cookies:
            try:
                login = cookie_data["login"]
                auth_cookie_value = cookie_data["bii_auth_session"]
                remember_key = cookie_data["remember_key"]
                remember_value = cookie_data["remember_value"]

                logging.info(f"Testing with login: {login}")

                # Заходим на страницу авторизации
                page.goto(LOGIN_URL)

                # Добавляем обе куки в контекст
                context.add_cookies([
                    {
                        "name": "bii_auth_session",
                        "value": auth_cookie_value,
                        "domain": "ca.bll.by",
                        "path": "/",
                        "httpOnly": True,
                        "secure": True,
                    },
                    {
                        "name": remember_key,
                        "value": remember_value,
                        "domain": "ca.bll.by",
                        "path": "/",
                        "httpOnly": True,
                        "secure": True,
                    }
                ])

                # Обновляем страницу
                page.goto(TARGET_URL)

                # Проверяем, что пользователь авторизован
                user_nick_locator = page.locator("//div[@class='user-in__nick' and text()='{login}']".replace("{login}", login))
                if user_nick_locator.is_visible():
                    print(f"Authorization successful for user: {login}")
                else:
                    raise AssertionError(f"Authorization failed for user: {login}")

                # Выход из аккаунта
                page.goto(LOGOUT_URL)
                print(f"Logged out for user: {login}")

            except Exception as e:
                print(f"Test failed for user {login}: {e}")

        # Закрываем браузер
        browser.close()

if __name__ == "__main__":
    replace_cookies_and_verify()
