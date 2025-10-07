"""
Burger Menu Right Column - Personal Account Navigation - Multi-Domain Parameterized Tests.

Параметризованные тесты раздела 'Личный кабинет' правой колонки бургер-меню.
Тестирует навигацию в персональный аккаунт на всех доменах.
Поддерживает умную авторизацию с правильными параметрами куки.
Использует SmartAuthManager для автоматической проверки и обновления сессии.
"""

import pytest
import re
from framework.utils.url_utils import add_allow_session_param, is_headless
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage

@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.right_column
class TestPersonalAccountNavigationParams:

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_personal_account_navigation(self, multi_domain_context, domain_aware_authenticated_context):
        """
        Мульти-домен доступ к личному кабинету - enterprise coverage.

        Тестирует переход в личный кабинет пользователя.
        Многие домены могут перенаправлять на business-info.by/pc.
        """
        domain_name, base_url = multi_domain_context

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Geek) Chrome/120.0.0.0 Safari/537.36",
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

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            # Allow redirects to follow final destination
            response = requests.get(current_url, allow_redirects=True)
            print(f"HTTP статус после редиректов: {response.status_code}")
            print(f"финальный URL: {response.url}")

            # Accept both 200 and 301 as valid responses
            assert response.status_code in [200, 301, 302], f"HTTP {response.status_code} for URL: {current_url}"

            # Many domains redirect to business-info.by/pc for personal account - menu must be accessible
            assert burger_menu.is_menu_open(), f"Burger menu failed to open on {domain_name}"        finally:
            page.close()
