"""
Burger Menu Left Column - Buy Navigation - Multi-Domain Parameterized Tests.

Использует домен-зависимую авторизацию для корректной работы во всех доменах.
"""

import pytest
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage


@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.left_column
class TestBuyNavigationParams:
    @pytest.mark.parametrize(
        'multi_domain_context',
        ['bll', 'expert', 'bonus', 'ca', 'cp'],
        indirect=True,
        ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP']
    )
    def test_buy_navigation(
        self, domain_aware_authenticated_context, multi_domain_context
    ):
        domain_name, base_url = multi_domain_context

        # Создание страницы из домен-зависимого аутентифицированного контекста
        page = domain_aware_authenticated_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            # Переход на главную страницу
            page.goto(base_url, wait_until="domcontentloaded")
            burger_menu.smart_wait_for_page_ready()  # Умное ожидание готовности страницы

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Купить")

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            assert "buy" in current_url.lower() and "bll.by" in current_url, \
                f"URL не содержит buy и bll.by: {current_url}"
        finally:
            page.close()
