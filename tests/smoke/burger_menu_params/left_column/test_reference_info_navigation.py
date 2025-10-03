"""
Burger Menu Left Column - Reference Info Navigation - Multi-Domain Parameterized Tests.

Параметризованные тесты раздела 'Справочная информация' левой колонки бургер-меню.
Использует smart URL comparison с ID как в baseline.
"""

import pytest
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage


@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.left_column
class TestReferenceInfoNavigationParams:

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_reference_info_navigation(self, multi_domain_context, browser):
        """
        Мульти-домен навигация к справочной информации - enterprise coverage.

        Проверяет:
        - Текст клик: "Справочная информация"
        - Smart URL comparison: содержит ID "200083"
        - Использует умную логику сравнения ID как в baseline
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

            # Текст клик как в baseline
            burger_menu.click_link_by_text("Справочная информация")

            # Умная проверка URL как в baseline - сравнение по ID
            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "200083"), \
                f"URL не содержит ожидаемый ID 200083 для домена {domain_name}: {current_url}"

        finally:
            page.close()
            context.close()
