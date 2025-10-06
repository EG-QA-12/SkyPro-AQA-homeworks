"""
Enterprise test for Experts Club Navigation - Клуб экспертов.
Tests navigation to experts club section: https://expert.bll.by/experts

Supports multi-domain testing (5 domains).
"""
import pytest
import allure
import re
import requests
from playwright.sync_api import expect
from framework.utils.url_utils import add_allow_session_param, is_headless
from tests.e2e.pages.burger_menu_page import BurgerMenuPage


class TestExpertsClubNavigation:
    """Test Experts Club Navigation across multiple domains."""

    DOMAINS = {
        "bll.by": "https://bll.by",
        "expert.bll.by": "https://expert.bll.by",
        "demo.bll.by": "https://demo.bll.by",
        "ca.bll.by": "https://ca.bll.by",
        "business-info.by": "https://business-info.by"
    }

    @allure.epic("Burger Menu Navigation")
    @allure.feature("Experts Club Navigation")
    @allure.story("Navigate to Experts Club Section")
    @allure.title("Навигация: Клуб экспертов на домене {domain_name}")
    @allure.description("Проверка перехода в раздел Клуб экспертов на домене {domain_name}")
    @allure.severity("normal")
    @pytest.mark.smoke
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.parametrize("domain_name,domain_url", list(DOMAINS.items()))
    def test_experts_club_navigation(self, authenticated_burger_context, domain_name, domain_url):
        """
        Test Experts Club Navigation for domain {domain_name}.

        Tests navigation to "Клуб экспертов" section at expert.bll.by/experts.
        May redirect through expert.bll.by depending on domain.
        """
        page = authenticated_burger_context.new_page()
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

            # Try to click experts club link
            with page.expect_response("https://expert.bll.by/experts") as response_info:
                assert burger_menu.click_link_by_text("Клуб экспертов"), \
                    "Не удалось кликнуть по ссылке 'Клуб экспертов'"

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Verify navigation to experts club
            current_url = page.url

            # Additional HTTP status check for final URL
            response = requests.get(current_url, allow_redirects=False)
            assert response.status_code == 200, f"HTTP {response.status_code} for final URL: {current_url}"

            # Check URL pattern with regex (ignores query parameters)
            assert re.search(r'expert\.bll\.by', current_url), \
                f"URL не содержит паттерн домена expert.bll.by: {current_url}"

        finally:
            page.close()
