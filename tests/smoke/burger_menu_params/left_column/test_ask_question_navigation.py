"""
Burger Menu Cross-Domain Navigation - Ask Question - Expert Domain.

Поддерживает умную авторизацию с правильными параметрами куки.
Использует SmartAuthManager для автоматической проверки и обновления сессии.
"""
import pytest
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
@pytest.mark.cross_domain
class TestAskQuestionNavigationParams:
    @pytest.mark.parametrize('multi_domain_context',['bll', 'expert', 'bonus', 'ca', 'cp'], indirect=True, ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_ask_question_navigation(self, multi_domain_context, browser, fx_auth_manager):
        domain_name, base_url = multi_domain_context

        # SSO-aware cross-domain navigation
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

        page = context.new_page()
        burger_menu = BurgerMenuPage(page)
        try:
            page.goto(add_allow_session_param(base_url, is_headless()), wait_until="domcontentloaded")
            page.wait_for_timeout(2000)  # Allow SSO redirects

            burger_menu.open_menu()

            # Use page.get_by_role for precise element selection
            ask_link = page.get_by_role("banner").get_by_role("link", name="Задать вопрос")
            ask_link.click()

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            # Cross-domain navigation to expert question creation page
            assert "expert.bll.by" in current_url, f"URL должен содержать expert.bll.by: {current_url}"

            # Allow redirects to follow final destination
            response = requests.get(current_url, allow_redirects=True)
            print(f"HTTP статус после редиректов: {response.status_code}")
            print(f"финальный URL: {response.url}")

            # Accept both 200 and 301 as valid responses
            assert response.status_code in [200, 301, 302], f"HTTP {response.status_code} for URL: {current_url}"
        finally:
            page.close()
            context.close()
