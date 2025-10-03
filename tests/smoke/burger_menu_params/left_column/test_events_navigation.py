"""
Enterprise test for Events Navigation - Мероприятия.
Tests navigation to events section with ID 471630: https://bll.by/docs/events-471630

Supports multi-domain testing (5 domains).
"""
import pytest
import allure
from playwright.sync_api import expect
from tests.e2e.pages.burger_menu_page import BurgerMenuPage


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
    def test_events_navigation(self, authenticated_burger_context, domain_name, domain_url):
        """
        Test Events Navigation for domain {domain_name}.

        Tests navigation to events section with ID 471630.
        For domains without events section, should maintain SSO stability.
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            # Navigate to domain
            page.goto(f"{domain_url}/", wait_until="domcontentloaded")
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

            with page.expect_response("**/471630**") as response_info:
                events_link.click()

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Verify URL contains expected ID
            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "471630"), \
                f"URL не содержит ожидаемый ID 471630: {current_url}"

        finally:
            page.close()
