"""
Enterprise test for Document Search Navigation - Поиск в базе документов.
Tests navigation to document search section: https://bll.by/docs

Supports multi-domain testing (5 domains).
"""
import pytest
import allure
import re
import requests
from playwright.sync_api import expect
from framework.utils.url_utils import add_allow_session_param, is_headless
from tests.e2e.pages.burger_menu_page import BurgerMenuPage


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
    def test_document_search_navigation(self, authenticated_burger_context, domain_name, domain_url):
        """
        Test Document Search Navigation for domain {domain_name}.

        Tests navigation to document search section at /docs.
        This is a core navigation feature available on all domains.
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

            # Click document search link
            with page.expect_response("**/docs**") as response_info:
                assert burger_menu.click_link_by_text("Поиск в базе документов"), \
                    "Не удалось кликнуть по ссылке 'Поиск в базе документов'"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            # Verify navigation to docs page
            current_url = page.url

            # Additional HTTP status check for final URL
            response = requests.get(current_url, allow_redirects=False)
            assert response.status_code == 200, f"HTTP {response.status_code} for final URL: {current_url}"

            # Check URL pattern with regex (ignores query parameters)
            assert re.search(r'docs.*bll\.by', current_url), \
                f"URL не содержит паттерн docs с доменом bll.by: {current_url}"

            # Keep original Playwright assertion as well
            expect(page).to_have_url("https://bll.by/docs")

        finally:
            page.close()
