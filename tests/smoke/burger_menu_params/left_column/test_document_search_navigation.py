"""
Enterprise test for Document Search Navigation - Поиск в базе документов.
Tests navigation to document search section: https://bll.by/docs

Поддерживает умную авторизацию с SmartAuthManager для автоматической проверки сессии.
Supports multi-domain testing (5 domains).
"""
import pytest
import allure
import re
import requests
from playwright.sync_api import expect
from framework.utils.url_utils import add_allow_session_param, is_headless
from framework.utils.smart_auth_manager import SmartAuthManager
from tests.e2e.pages.burger_menu_page import BurgerMenuPage

@pytest.fixture
def fx_auth_manager():
    """Инициализация умного менеджера авторизации"""
    return SmartAuthManager()


class TestDocumentSearchNavigation:
    """Test Document Search Navigation across multiple domains."""

    DOMAINS = {
        "bll.by": "https://bll.by",
        "expert.bll.by": "https://expert.bll.by",
        "demo.bll.by": "https://demo.bll.by",
        "ca.bll.by": "https://ca.bll.by",
        "business-info.by": "https://business-info.by"
    }

    @allure.epic("Burger Menu Navigation")
    @allure.feature("Document Search Navigation")
    @allure.story("Navigate to Document Search Section")
    @allure.title("Навигация: Поиск в базе документов на домене {domain_name}")
    @allure.description("Проверка перехода в раздел Поиск в базе документов на домене {domain_name}")
    @allure.severity("critical")
    @pytest.mark.smoke
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.parametrize("domain_name,domain_url", list(DOMAINS.items()))
    def test_document_search_navigation(self, browser, fx_auth_manager, domain_name, domain_url):
        """
        Test Document Search Navigation for domain {domain_name}.

        Tests navigation to document search section at /docs.
        This is a core navigation feature available on all domains.
        """
        # SSO-aware browser settings for enterprise testing
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True
        )

        # Используем SmartAuthManager для умной авторизации
        cookie_info = fx_auth_manager.get_valid_session_cookie(role="admin")
        assert cookie_info, "Не удалось получить валидную куку через SmartAuthManager"

        # Устанавливаем полную информацию о куке (name, value, domain, sameSite)
        context.add_cookies([cookie_info])

        page = context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            # Navigate to domain with allow-session parameter
            page.goto(add_allow_session_param(f"{domain_url}/", is_headless()), wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            # Open burger menu with retry
            max_retries = 3
            for attempt in range(max_retries):
                if burger_menu.open_menu():
                    break
                if attempt < max_retries - 1:
                    page.wait_for_timeout(1000)
                    page.reload()
                else:
                    pytest.fail("Не удалось открыть бургер-меню после нескольких попыток")

            # Click document search link
            assert burger_menu.click_link_by_text("Поиск в базе документов"), \
                "Не удалось кликнуть по ссылке 'Поиск в базе документов'"

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            # Allow redirects to follow final destination
            response = requests.get(current_url, allow_redirects=True)
            print(f"HTTP статус после редиректов: {response.status_code}")
            print(f"финальный URL: {response.url}")

            assert response.status_code in [200, 301, 302], f"HTTP {response.status_code} for URL: {current_url}"

            # Check URL pattern with regex (ignores query parameters)
            assert re.search(r'docs.*bll\.by', current_url), \
                f"URL не содержит паттерн docs с доменом bll.by: {current_url}"

            # Keep original Playwright assertion for backward compatibility
            expect(page).to_have_url("https://bll.by/docs")

        finally:
            page.close()
            context.close()
