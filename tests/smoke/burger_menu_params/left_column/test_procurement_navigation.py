"""
Burger Menu Left Column - Procurement Navigation - Multi-Domain Parameterized Tests.

Параметризованные тесты раздела 'Закупки' левой колонки бургер-меню.
Тестирует cross-domain redirect на gz.bll.by для всех доменов.
"""

import pytest
import re
import requests
from framework.utils.url_utils import add_allow_session_param, is_headless
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage


@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.left_column
class TestProcurementNavigationParams:

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_procurement_navigation(self, multi_domain_context, browser):
        """
        Мульти-домен навигация к разделу закупок - enterprise coverage.

        Проверяет cross-domain redirect:
        - Все домены redirect на gz.bll.by (внешний домен)
        - Учитывает redirects авторизации (301/302)
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
            page.goto(add_allow_session_param(base_url, is_headless()), wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            burger_menu.open_menu()

            # Клик по "Закупки"
            burger_menu.click_link_by_text("Закупки")

            # Cross-domain assertion: все домены redirect на gz.bll.by
            # Учитываем возможность redirects авторизации
            current_url = page.url

            # Check HTTP status code
            response = requests.get(current_url, allow_redirects=False)
            assert response.status_code == 200, f"HTTP {response.status_code} for URL: {current_url}"

            # Check URL pattern with regex (should redirect to gz.bll.by)
            assert re.search(r'gz\.bll\.by', current_url), \
                f"URL не содержит паттерн домена закупок gz.bll.by: {current_url}"

        finally:
            page.close()
            context.close()
