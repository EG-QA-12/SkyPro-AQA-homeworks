"""
Burger Menu Left Column - Checklists Navigation - Multi-Domain Parameterized Tests.

Параметризованные тесты раздела 'Чек-листы' левой колонки бургер-меню.
Использует SmartAuthManager для умной авторизации и проверки HTTP статусов.
"""

import pytest
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage


@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.left_column
class TestChecklistsNavigationParams:

    @pytest.mark.parametrize('multi_domain_context',
                           ['bll', 'expert', 'bonus', 'ca', 'cp'],
                           indirect=True,
                           ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_checklists_navigation(self, multi_domain_context, domain_aware_authenticated_context):
        """
        Мульти-домен навигация к чек-листам - enterprise coverage.

        Проверяет URL ID: 487105
        """
        domain_name, base_url = multi_domain_context

        # Создание страницы из домен-зависимого аутентифицированного контекста
        page = domain_aware_authenticated_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            # Переход на главную страницу
            page.goto(base_url, wait_until="domcontentloaded")
            burger_menu.smart_wait_for_page_ready()  # Умное ожидание готовности страницы

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Чек-листы")

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            assert "chek-list-dokumentov-487105" in current_url.lower(), \
                f"URL не содержит паттерн чек-листов chek-list-dokumentov-487105: {current_url}"
        finally:
            page.close()
