"""
Burger Menu Right Column - New Documents Navigation - Multi-Domain Parameterized Tests.

Параметризованные тесты раздела 'Новые документы' правой колонки бургер-меню.
Использует эмуляцию взаимодействий с элементами меню.
Поддерживает умную авторизацию с правильными параметрами куки.
Использует SmartAuthManager для автоматической проверки и обновления сессии.
"""

import pytest
import re
import requests
from framework.utils.url_utils import add_allow_session_param, is_headless
from framework.utils.smart_auth_manager import SmartAuthManager
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage

@pytest.fixture
def fx_auth_manager():
    """Инициализация умного менеджера авторизации"""
    return SmartAuthManager()

@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.right_column
class TestNewDocumentsNavigationParams:

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_new_documents_navigation(self, multi_domain_context, browser, fx_auth_manager):
        """
        Мульти-домен навигация к новым документам - enterprise coverage.

        Тестирует переход в раздел "Новые документы".
        Использует сложный селектор как в baseline для правой колонки.
        """
        domain_name, base_url = multi_domain_context

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True
        )

        # Используем SmartAuthManager для умной авторизации
        cookie_info = fx_auth_manager.get_valid_session_cookie(role="admin")
        assert cookie_info, "Не удалось получить валидную куку через SmartAuthManager"

        # Устанавливаем полную информацию о куке (name, value, domain, sameSite)
        context.add_cookies([cookie_info])

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

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            # Allow redirects to follow final destination
            response = requests.get(current_url, allow_redirects=True)
            print(f"HTTP статус после редиректов: {response.status_code}")
            print(f"финальный URL: {response.url}")

            # Accept both 200 and 301 as valid responses
            assert response.status_code in [200, 301, 302], f"HTTP {response.status_code} for URL: {current_url}"

            # URL assertion для новых документов - всегда /docs/new
            assert re.search(r'/docs/new$', current_url), \
                f"URL не ведет на новые документы для домена {domain_name}: {current_url}"

        finally:
            page.close()
            context.close()
