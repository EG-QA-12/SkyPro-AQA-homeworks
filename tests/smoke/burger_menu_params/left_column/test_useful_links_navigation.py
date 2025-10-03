"""
Burger Menu Left Column - Useful Links Navigation - Multi-Domain Parameterized Tests.

Параметризованные тесты раздела 'Полезные ссылки' левой колонки бургер-меню.
Использует custom селектор как в baseline для точного клика.
"""

import pytest
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage


@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.left_column
class TestUsefulLinksNavigationParams:

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_useful_links_navigation(self, multi_domain_context, browser):
        """
        Мульти-домен навигация к полезным ссылкам - enterprise coverage.

        Проверяет:
        - Custom селектор из baseline: "a.menu_item_link[href*='poleznye-ssylki-219924']"
        - URL ID: 219924 для всех доменов
        """
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

            # Используем custom селектор из baseline как в smoke version
            page.locator("a.menu_item_link[href*='poleznye-ssylki-219924']").first.click()

            # URL assertion с ID comparison (рабочий для всех доменов)
            assert "poleznye-ssylki-219924" in page.url, \
                f"URL не содержит ожидаемый ID 219924 для домена {domain_name}: {page.url}"

        finally:
            page.close()
            context.close()
