"""
Burger Menu Left Column - Demo Access Navigation - Multi-Domain Parameterized Tests.

Поддерживает умную авторизацию с правильными параметрами куки.
Использует SmartAuthManager для автоматической проверки и обновления сессии.
"""
import pytest
import re
from framework.utils.url_utils import add_allow_session_param, is_headless
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage

@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.left_column
class TestDemoAccessNavigationParams:
    @pytest.mark.parametrize('multi_domain_context',['bll', 'expert', 'bonus', 'ca', 'cp'], indirect=True, ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_demo_access_navigation(self, multi_domain_context, domain_aware_authenticated_context):
        domain_name, base_url = multi_domain_context

        # SSO-aware domain-specific browser settings
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True
        )

        if domain_name in ['ca', 'bonus', 'cp']:
            context.set_default_timeout(30000)
        else:
            context.set_default_timeout(25000)

        # Используем SmartAuthManager для умной авторизации
        cookie_info = fx_auth_manager.get_valid_session_cookie(role="admin")
        assert cookie_info, "Не удалось получить валидную куку через SmartAuthManager"

        # Устанавливаем полную информацию о куке (name, value, domain, sameSite)
        context.add_cookies([cookie_info])

        page = domain_aware_authenticated_context.new_page()
        burger_menu = BurgerMenuPage(page)
        try:
            page.goto(add_allow_session_param(base_url, is_headless()), wait_until="domcontentloaded")
            page.wait_for_timeout(2000)  # Allow SSO redirects

            burger_menu.open_menu()

            # Demo access link click
            demo_link = page.get_by_role("link", name="Получить демодоступ")
            assert demo_link.is_visible(), "Demo link not found"
            demo_link.click()

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
            assert re.search(r'buy.*request', current_url), \
                f"URL не содержит паттерн buy с request параметрами: {current_url}"        finally:
            page.close()
