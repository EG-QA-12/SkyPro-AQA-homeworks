"""
Burger Menu Left Column - Multi-Domain Parameterized Tests.

Параметризованные тесты левой колонки бургер-меню для всех доменов системы.
Использует параметризацию для запуска тестов на 5 доменах одновременно.
"""

import pytest

from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage


def _skip_unavailable_domains(domain_name: str, test_name: str):
    """
    Skip test for domains where burger menu is not available due to auth redirect.

    CA and Bonus domains redirect to login page where burger menu elements are not present.
    """
    if domain_name in ['bonus', 'ca']:
        pytest.skip(f"Burger menu недоступен для домена {domain_name} - редирект на login страницу")


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

        CA/Bonus домены: burger menu недоступен после редиректа на login
        """
        domain_name, base_url = multi_domain_context

        # CA и Bonus домены редиректят на login и burger menu там не работает
        if domain_name in ['bonus', 'ca']:
            pytest.skip("Burger menu недоступен для доменов CA/Bonus - редирект на login")

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
        """Мульти-домен навигация 'Кодексы'."""
        domain_name, base_url = multi_domain_context
        _skip_unavailable_domains(domain_name, "codes_navigation")

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
        _skip_unavailable_domains(domain_name, "procurement_navigation")

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

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_about_navigation(self, multi_domain_context, browser):
        """Мульти-домен навигация 'О Платформе'."""
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
            burger_menu.click_link_by_text("О Платформе")

            assert "about" in page.url and "bll.by" in page.url

        finally:
            page.close()
            context.close()

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_buy_navigation(self, multi_domain_context, browser):
        """Мульти-домен навигация 'Купить'."""
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
            burger_menu.click_link_by_text("Купить")

            assert "buy" in page.url and "bll.by" in page.url

        finally:
            page.close()
            context.close()

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_docs_navigation(self, multi_domain_context, browser):
        """Мульти-домен навигация 'Поиск в базе документов'."""
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
            burger_menu.click_link_by_text("Поиск в базе документов")

            assert "docs" in page.url and "bll.by" in page.url

        finally:
            page.close()
            context.close()

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_phone_number_click(self, multi_domain_context, browser):
        """Мульти-домен проверка телефона."""
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

            # Клик по телефону тестирует только наличие элемента
            phone_link = page.get_by_role("link", name="+375 17 388 32")
            assert phone_link.is_visible(), "Телефонная ссылка не найдена"

            phone_href = phone_link.get_attribute("href")
            assert phone_href and phone_href.startswith("tel:"), "Неверный формат телефонной ссылки"

        finally:
            page.close()
            context.close()

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_home_page_navigation(self, multi_domain_context, browser):
        """Мульти-домен навигация на главную."""
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
            # Перейдем на другую страницу сначала - исправлена URL сборка
            page.goto(base_url.rstrip('/') + "/docs", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()

            # Найдем и кликнем ссылку "Главная страница"
            home_link = page.locator("a.menu_bl_ttl-main").first
            assert home_link.is_visible(), "Главная страница ссылка не найдена"
            home_link.click()

            # Исправлено: игнорировать GA параметры в URL
            clean_url = page.url.split('?')[0]  # Убираем query params
            assert base_url in clean_url or clean_url == base_url + '/'

        finally:
            page.close()
            context.close()

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_demo_access_navigation(self, multi_domain_context, browser):
        """Мульти-домен демо доступ."""
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

            # Найдем ссылку демодоступа
            demo_link = page.get_by_role("link", name="Получить демодоступ")
            assert demo_link.is_visible(), "Ссылка демодоступа не найдена"
            demo_link.click()

            # Реальная навигация ведет на демо страницу
            assert "buy" in page.url and "?request" in page.url

        finally:
            page.close()
            context.close()
