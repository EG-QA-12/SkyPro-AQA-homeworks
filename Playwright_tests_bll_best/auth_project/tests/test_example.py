import sys
from pathlib import Path
import pytest

# Добавляем src в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent / 'src'))
from auth_manager import load_cookies
from playwright.sync_api import sync_playwright

TARGET_URL = "https://ca.bll.by/"

@pytest.mark.skipif(load_cookies() is None, reason="Нет сохранённых кук для теста")
def test_open_with_cookies():
    cookies = load_cookies()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
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
        assert page.locator(user_nick_locator).is_visible(), "Пользователь не авторизован по кукам!"
        browser.close()
