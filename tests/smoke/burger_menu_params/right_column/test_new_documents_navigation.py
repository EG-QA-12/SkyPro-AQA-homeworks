"""
Burger Menu Right Column - New Documents Navigation - Multi-Domain Parameterized Tests.

Параметризованные тесты раздела 'Новые документы' правой колонки бургер-меню.
Использует эмуляцию взаимодействий с элементами меню.
Поддерживает headless режим с allow-session параметром для обхода защиты от ботов.
"""

import pytest
import re
import requests
from framework.utils.url_utils import add_allow_session_param, is_headless
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage


@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.right_column
class TestNewDocumentsNavigationParams:

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_new_documents_navigation(self, multi_domain_context, browser):
        """
        Мульти-домен навигация к новым документам - enterprise coverage.

        Тестирует переход в раздел "Новые документы".
        Использует сложный селектор как в baseline для правой колонки.
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

            # Сложный селектор из baseline для правой колонки
            # Имитируем раскрутку и клик по новыедокументам
            page.evaluate("window.scrollTo({ left: 1000, behavior: 'smooth' });")
            page.wait_for_timeout(1000)

            # Селектор из baseline - правый третий блок, четвертый элемент
            page.locator("body > div.layout.layout--docs > header > div > div > div.menu-gumb_new.menu-mobile.active > div.new-menu.new-menu_main > div > div:nth-child(2) > div:nth-child(3) > div.menu_bl_list > div:nth-child(4) > a").click()

            # Check HTTP status code for current page after navigation
            current_url = page.url
            response = requests.get(current_url, allow_redirects=False)
            assert response.status_code == 200, f"HTTP {response.status_code} for URL: {current_url}"

            # URL assertion для новых документов - всегда /docs/new
            assert re.search(r'/docs/new$', current_url), \
                f"URL не ведет на новые документы для домена {domain_name}: {current_url}"

        finally:
            page.close()
            context.close()
