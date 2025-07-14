import pytest
import allure
from typing import Tuple
from playwright.sync_api import BrowserContext, Page
from framework.utils.auth_utils import get_random_user_cookie, is_guest, is_authorized
from framework.utils.reporting.allure_utils import allure_step

@pytest.mark.parametrize("url", [
    "https://bll.by/",
    "https://ca.bll.by/",
    "https://expert.bll.by/",
    "https://cp.bll.by/",
    "https://gz.bll.by/",
    "https://bonus.bll.by/",
])
@allure.title("Проверка cookie-авторизации на {url}")
def test_cookie_auth_on_domain(isolated_context: Tuple[BrowserContext, Page], url: str) -> None:
    """
    Тест проверки авторизации через cookies на разных доменах.
    
    Шаги:
    1. Перейти на URL как гость и проверить отсутствие авторизации.
    2. Добавить случайные валидные cookies.
    3. Перезагрузить страницу и проверить наличие авторизации.
    """
    context, page = isolated_context

    with allure_step("Шаг 1: Проверка отсутствия авторизации"):
        page.goto(url)
        assert is_guest(page), "Ожидалось, что пользователь не авторизован, но найдены признаки авторизации"

    with allure_step("Шаг 2: Добавление авторизационных cookies"):
        cookies = get_random_user_cookie(context)
        if not cookies:
            pytest.fail("Не удалось получить валидные cookies")
        context.add_cookies(cookies)

    with allure_step("Шаг 3: Проверка наличия авторизации после добавления cookies"):
        page.reload()
        assert is_authorized(page), "Ожидалась авторизация после добавления cookies, но признаки не найдены"