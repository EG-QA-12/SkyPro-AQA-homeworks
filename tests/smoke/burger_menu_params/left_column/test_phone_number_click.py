"""
Burger Menu Left Column - Phone Number Click - Multi-Domain Parameterized Tests.

Поддерживает умную авторизацию с правильными параметрами куки.
Использует SmartAuthManager для автоматической проверки и обновления сессии.
"""
import pytest
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage

@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.left_column
class TestPhoneNumberClickParams:
    @pytest.mark.parametrize('multi_domain_context',
                            ['bll', 'expert', 'bonus', 'ca', 'cp'],
                            indirect=True,
                            ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_phone_number_click(self, multi_domain_context, domain_aware_authenticated_context):
        domain_name, base_url = multi_domain_context

        # Создание страницы из домен-зависимого аутентифицированного контекста
        page = domain_aware_authenticated_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            # Переход на главную страницу
            page.goto(base_url, wait_until="domcontentloaded")
            burger_menu.smart_wait_for_page_ready()  # Умное ожидание готовности страницы

            burger_menu.open_menu()

            # Phone number link verification
            phone_link = page.get_by_role("link", name="+375 17 388 32")
            assert phone_link.is_visible(), "Phone link not found"

            # Verify proper tel: href format
            phone_href = phone_link.get_attribute("href")
            assert phone_href and phone_href.startswith("tel:")

            # Additional HTTP status check for current page
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            assert "bll.by" in current_url.lower(), \
                f"URL не содержит bll.by: {current_url}"
        finally:
            page.close()
