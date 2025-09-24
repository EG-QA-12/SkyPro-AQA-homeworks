from playwright.sync_api import sync_playwright
import logging

# Файл с сохраненными куками
COOKIES_FILE = "Cookies_user.txt"

# Целевой URL
TARGET_URL = "https://ca.bll.by/"

def load_auth_cookie():
    """Загрузить значение куки bii_auth_session из файла"""
    try:
        with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    login, cookie_value = line.split(';')
                    print(f"Loaded cookie for {login}: {cookie_value}")
                    return cookie_value.strip()  # Берем первое значение
    except Exception as e:
        logging.error(f"Error loading auth cookie: {e}")
        raise

def replace_cookie_and_verify():
    """Заменить куку неавторизованного пользователя на значение из файла"""
    auth_cookie_value = load_auth_cookie()
    if not auth_cookie_value:
        logging.error("No valid auth cookie found!")
        return

    with sync_playwright() as p:
        # Запуск браузера
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Открываем целевую страницу
        page.goto(TARGET_URL)

        # Получаем текущие куки
        initial_cookies = context.cookies()
        print(f"Initial cookies: {initial_cookies}")

        # Заменяем куки на значение из файла
        context.add_cookies([{
            "name": "bii_auth_session",
            "value": auth_cookie_value,
            "domain": "ca.bll.by",  # Домен обновлен для вашего случая
            "path": "/",
            "httpOnly": True,
            "secure": True,
        }])

        # Перезагружаем страницу
        page.reload()

        # Проверяем, авторизован ли пользователь
        try:
            profile_link = page.get_by_role("link", name="Мой профиль")
            assert profile_link.is_visible(), "Authorization failed after replacing cookie!"
            print("Authorization successful with replaced cookie.")
        except Exception as e:
            print(f"Authorization check failed: {e}")

        # Закрываем браузер
        browser.close()

if __name__ == "__main__":
    replace_cookie_and_verify()
