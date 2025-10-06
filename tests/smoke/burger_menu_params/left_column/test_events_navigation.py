"""
Enterprise test for Events Navigation - Мероприятия.
Tests navigation to events section with ID 471630: https://bll.by/docs/events-471630

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


class TestEventsNavigation:
    """Test Events Navigation across multiple domains."""

    DOMAINS = {
        "bll.by": "https://bll.by",
        "expert.bll.by": "https://expert.bll.by",
        "demo.bll.by": "https://demo.bll.by",
        "ca.bll.by": "https://ca.bll.by",
        "business-info.by": "https://business-info.by"
    }

    @allure.epic("Burger Menu Navigation")
    @allure.feature("Events Navigation")
    @allure.story("Navigate to Events Section")
    @allure.title("Навигация: Мероприятия на домене {domain_name}")
    @allure.description("Проверка перехода в раздел Мероприятия (ID 471630) на домене {domain_name}")
    @allure.severity("normal")
    @pytest.mark.smoke
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.parametrize("domain_name,domain_url", list(DOMAINS.items()))
    def test_events_navigation(self, browser, fx_auth_manager, domain_name, domain_url):
        """
        Test Events Navigation for domain {domain_name}.

        Tests navigation to events section with ID 471630.
        For domains without events section, should maintain SSO stability.
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

            # Try to find and click events link
            events_link = page.locator("a.menu_bl_ttl-events").first

            # Заменяем expect_response на standard click с HTTP проверкой
            events_link.click()

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            # Allow redirects to follow final destination
            response = requests.get(current_url, allow_redirects=True)
            print(f"HTTP статус после редиректов: {response.status_code}")
            print(f"финальный URL: {response.url}")

            assert response.status_code in [200, 301, 302], f"HTTP {response.status_code} for URL: {current_url}"

            # Check URL pattern with regex (ignores query parameters)
            assert re.search(r'events-471630', current_url), \
                f"URL не содержит паттерн events-471630: {current_url}"

        finally:
            page.close()
            context.close()
