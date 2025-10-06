"""
Burger Menu Left Column - Topic Collections Navigation - Multi-Domain Parameterized Tests.

Поддерживает headless режим с allow-session параметром для обхода защиты от ботов.
"""
import pytest
import re
import requests
from framework.utils.url_utils import add_allow_session_param, is_headless
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage

@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.left_column
class TestTopicCollectionsNavigationParams:
    @pytest.mark.parametrize('multi_domain_context',['bll', 'expert', 'bonus', 'ca', 'cp'], indirect=True, ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_topic_collections_navigation(self, multi_domain_context, browser):
        domain_name, base_url = multi_domain_context
        from framework.utils.auth_cookie_provider import get_auth_cookies

        # SSO-aware domain-specific browser settings
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True
        )

        if domain_name in ['ca', 'bonus', 'cp']:
            context.set_default_timeout(30000)
        else:
            context.set_default_timeout(25000)

        context.add_cookies(get_auth_cookies(role="admin"))
        page = context.new_page()
        burger_menu = BurgerMenuPage(page)
        try:
            page.goto(add_allow_session_param(base_url, is_headless()), wait_until="domcontentloaded")
            page.wait_for_timeout(2000)  # Allow SSO redirects

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Всё по одной теме")

            # URL contains topic collections ID for all domains
            current_url = page.url

            # Check HTTP status code
            response = requests.get(current_url, allow_redirects=False)
            assert response.status_code == 200, f"HTTP {response.status_code} for URL: {current_url}"

            # Check URL pattern with regex (ignores query parameters)
            assert re.search(r'vse-po-odnoj-teme-200084', current_url), \
                f"URL не содержит паттерн коллекций тем vse-po-odnoj-teme-200084: {current_url}"
        finally:
            page.close()
            context.close()
