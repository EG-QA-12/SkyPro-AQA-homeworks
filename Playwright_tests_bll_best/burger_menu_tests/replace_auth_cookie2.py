from playwright.sync_api import sync_playwright
import logging

# Файл с сохраненными куками
COOKIES_FILE = "Cookies_user_1.txt"

# Целевые URL
LOGIN_URL = "https://ca.bll.by/login"
LOGOUT_URL = "https://ca.bll.by/logout"
TARGET_URL = "https://ca.bll.by/"

def load_auth_cookies():
    """Загрузить куки bii_auth_session из файла"""
    cookies = []
    try:
        with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    login, cookie_value = line.split(';')
                    cookies.append((login.strip(), cookie_value.strip()))
        return cookies
    except Exception as e:
        logging.error(f"Error loading auth cookies: {e}")
        raise

def replace_cookie_and_verify():
    """Заменить куку неавторизованного пользователя и проверить авторизацию"""
    cookies = load_auth_cookies()
    if not cookies:
        logging.error("No valid cookies found!")
        return

    with sync_playwright() as p:
        # Запуск браузера
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        for login, auth_cookie_value in cookies:
            try:
                logging.info(f"Testing with login: {login}")
                # Заходим на страницу авторизации
                page.goto(LOGIN_URL)

                # Заменяем куки на значение из файла
                context.add_cookies([{
                    "name": "bii_auth_session",
                    "value": auth_cookie_value,
                    "domain": "ca.bll.by",  # Домен
                    "path": "/",
                    "httpOnly": True,
                    "secure": True,
                }])

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
    replace_cookie_and_verify()
