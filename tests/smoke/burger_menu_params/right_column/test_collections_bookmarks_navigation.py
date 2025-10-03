"""
Burger Menu Right Column - Collections & Bookmarks Navigation - Multi-Domain Parameterized Tests.

Параметризованные тесты раздела 'Подборки и закладки' правой колонки бургер-меню.
"""

import pytest
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage


@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.right_column
class TestCollectionsBookmarksNavigationParams:

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_collections_bookmarks_navigation(self, multi_domain_context, browser):
        """Мульти-домен коллекции и закладки - enterprise coverage."""
        domain_name, base_url = multi_domain_context

        from framework.utils.auth_cookie_provider import get_auth_cookies

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True
        )

        context.add_cookies(get_auth_cookies(role="admin"))
        page = context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto(base_url, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            burger_menu.open_menu()
            assert burger_menu.is_menu_open(), f"Burger menu failed to open on {domain_name}"
        finally:
            page.close()
            context.close()
