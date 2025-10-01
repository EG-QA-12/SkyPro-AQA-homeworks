"""
Базовый класс для тестов навигации через бургер-меню.

Содержит общую логику для всех тестов навигации, включая retry-механизм и валидацию.
"""

import allure
import pytest
from playwright.sync_api import expect, Page

from tests.e2e.pages.burger_menu_page import BurgerMenuPage
from framework.app.pages.login_page import LoginPage
from framework.utils.auth_cookie_provider import AuthCookieProvider


class BaseBurgerMenuNavigationTest:
    """
    Базовый класс для всех тестов навигации через бургер-меню.

    Предоставляет общие методы для открытия меню, клика по ссылкам и валидации URL.
    """

    def _ensure_authenticated(self, page: Page) -> None:
        """
        Обеспечивает авторизацию пользователя на странице.

        Если страница находится на странице логина или содержит форму логина,
        выполняет авторизацию с помощью учетных данных администратора.

        Args:
            page: Экземпляр страницы Playwright
        """
        # Проверяем, находимся ли мы на странице логина
        if "login" in page.url.lower() or page.locator("input[name='login']").is_visible(timeout=5000):
            # Получаем учетные данные
            auth_provider = AuthCookieProvider()
            username, password = auth_provider._get_credentials_for_role("admin")

            if not username or not password:
                pytest.fail("Не удалось получить учетные данные для авторизации")

            # Выполняем логин
            login_page = LoginPage(page)
            login_page.login(username, password)

            # После логина переходим на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

    @allure.step("Открытие бургер-меню с retry")
    def _open_menu_with_retry(self, page: Page, max_retries: int = 3) -> bool:
        """
        Открывает бургер-меню с механизмом повторных попыток.
        
        Args:
            page: Экземпляр страницы Playwright
            max_retries: Максимальное количество попыток
            
        Returns:
            bool: True если меню успешно открыто
        """
        for attempt in range(max_retries):
            burger_menu = BurgerMenuPage(page)
            if burger_menu.open_menu():
                return True
            if attempt < max_retries - 1:
                page.wait_for_timeout(1000)
                page.reload()
            else:
                return False
        return False

    @allure.step("Навигация по ссылке с валидацией")
    def _navigate_and_validate(self, page: Page, link_text: str, expected_url: str, 
                              expected_status: list = [200, 201], external_domain: bool = False) -> bool:
        """
        Выполняет навигацию по ссылке и валидацию ответа.
        
        Args:
            page: Экземпляр страницы Playwright
            link_text: Текст ссылки для клика
            expected_url: Ожидаемый URL или паттерн
            expected_status: Ожидаемые статус-коды
            external_domain: Флаг для внешних доменов
            
        Returns:
            bool: True если навигация успешна
        """
        burger_menu = BurgerMenuPage(page)
        
        # Открытие меню
        if not self._open_menu_with_retry(page):
            assert False, "Не удалось открыть бургер-меню после нескольких попыток"
        
        # Клик по ссылке с ожиданием ответа
        with page.expect_response(lambda response: response.url == expected_url) as response_info:
            assert burger_menu.click_link_by_text(link_text), f"Не удалось кликнуть по ссылке '{link_text}'"
        
        # Проверка статус-кода
        response = response_info.value
        assert response.status in expected_status, f"Неверный статус код: {response.status}"
        
        # Валидация URL
        if external_domain:
            assert expected_url in page.url, f"URL не содержит ожидаемый домен: {page.url}"
        else:
            expect(page).to_have_url(expected_url)
        
        return True

    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @allure.title("Навигация: Новости")
    @allure.description("Проверка перехода в Новости - статус код и URL")
    def test_news_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Новости".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/news
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate(page, "Новости", "https://bll.by/news")
        finally:
            page.close()

    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @allure.title("Навигация: Словарь")
    @allure.description("Проверка перехода в Словарь - статус код и точный URL")
    def test_dictionary_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Словарь".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/terms (точное совпадение)
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate(page, "Словарь", "https://bll.by/terms")
        finally:
            page.close()

    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @allure.title("Навигация: О Платформе")
    @allure.description("Проверка перехода в О Платформе - статус код и URL")
    def test_about_platform_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "О Платформе".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/about
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate(page, "О Платформе", "https://bll.by/about")
        finally:
            page.close()