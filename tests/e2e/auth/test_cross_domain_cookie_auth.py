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
    
    Выполняет проверку работы единого входа (SSO) через куки на всех
    доменах экосистемы Bll. Тест использует Playwright для управления
    браузером и проверки состояния авторизации на уровне UI.
    
    Сценарий теста:
    1. Переход на указанный URL в режиме гостя
    2. Проверка отсутствия признаков авторизации (is_guest)
    3. Добавление валидных кук авторизации из случайного пользователя
    4. Перезагрузка страницы для активации сессии
    5. Проверка наличия признаков авторизации (is_authorized)
    
    Тест параметризован по доменам, что позволяет проверить SSO
    на всех сервисах экосистемы в рамках одного тестового класса.
    
    Args:
        isolated_context: Кортеж из изолированного BrowserContext и Page,
            гарантирующий чистое состояние браузера для каждого теста
        url: URL домена для тестирования (параметризовано через pytest.mark.parametrize)
        
    Returns:
        None: Тест использует assert для проверки условий
        
    Raises:
        AssertionError: при неудачной проверке состояния авторизации
        pytest.fail: при невозможности получить валидные куки
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
