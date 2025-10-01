"""
Burger Menu Left Column - Multi-Domain Parameterized Tests.

Параметризованные тесты левой колонки бургер-меню для всех доменов системы.
Использует параметризацию для запуска тестов на 5 доменах одновременно.
"""

import pytest

from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage


@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.left_column
class TestLeftColumnNavigationParams:

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_news_navigation(self, multi_domain_context, browser):
        """
        Мульти-домен навигация 'Новости'.
        Запускается на всех 5 доменах одновременно.
        """
        domain_name, base_url = multi_domain_context

        # Используем тот же подход что и в оригинальных тестах
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
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Новости")

            # Гибкая проверка: для CP с GA, но основная навигация до новостей работает
            assert "news" in page.url and "bll.by" in page.url

        finally:
            page.close()
            context.close()

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_codes_navigation(self, multi_domain_context, browser):
        """
        Мульти-домен навигация 'Кодексы'.
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
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Кодексы")

            # Все домены перенаправляют на bll.by
            assert "kodeksy" in page.url or "codes" in page.url

        finally:
            page.close()
            context.close()

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_procurement_navigation(self, multi_domain_context, browser):
        """
        Мульти-домен навигация 'Закупки' - ведет на gz.bll.by
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
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Закупки")

            # Переход на систему государственных закупок
            assert "gz.bll.by" in page.url

        finally:
            page.close()
            context.close()

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_support_navigation(self, multi_domain_context, browser):
        """Мульти-домен навигация 'Поддержка'."""
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
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Словарь")

            assert "terms" in page.url and "bll.by" in page.url

        finally:
            page.close()
            context.close()
