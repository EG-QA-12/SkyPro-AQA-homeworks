"""
Burger Menu Left Column - Reference Info Navigation - Multi-Domain Parameterized Tests.

Параметризованные тесты раздела 'Справочная информация' левой колонки бургер-меню.
Использует regex pattern с ID для надежности.
Поддерживает headless режим с allow-session параметром для обхода защиты от ботов.
"""

import pytest
import re
from framework.utils.url_utils import add_allow_session_param, is_headless
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage


@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.left_column
class TestReferenceInfoNavigationParams:

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_reference_info_navigation(self, multi_domain_context, domain_aware_authenticated_context):
        """
        Мульти-домен навигация к справочной информации - enterprise coverage.

        Проверяет:
        - Текст клик: "Справочная информация"
        - Smart URL comparison: содержит ID "200083"
        - Использует умную логику сравнения ID как в baseline
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

        page = domain_aware_authenticated_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto(add_allow_session_param(base_url, is_headless()), wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            burger_menu.open_menu()

            # Текст клик как в baseline
            burger_menu.click_link_by_text("Справочная информация")

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            # Allow redirects to follow final destination
            response = requests.get(current_url, allow_redirects=True)
            print(f"HTTP статус после редиректов: {response.status_code}")
            print(f"финальный URL: {response.url}")

            # Accept both 200 and 301 as valid responses
            assert response.status_code in [200, 301, 302], f"HTTP {response.status_code} for URL: {current_url}"

            # Check URL pattern with regex (ignores query parameters)
            assert re.search(r'spravochnaya-informatsiya-200083', current_url), \
                f"URL не содержит паттерн справочной информации spravochnaya-informatsiya-200083: {current_url}"        finally:
            page.close()
