"""
Burger Menu Left Column - Hot Topics Navigation - Multi-Domain Parameterized Tests.

Параметризованные тесты раздела 'Горячие темы' левой колонки бургер-меню.
Использует custom селектор как в baseline для точного клика.
"""

import pytest
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage

@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.left_column
class TestHotTopicsNavigationParams:
    @pytest.mark.parametrize('multi_domain_context',
                            ['bll', 'expert', 'bonus', 'ca', 'cp'],
                            indirect=True,
                            ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_hot_topics_navigation(self, multi_domain_context, domain_aware_authenticated_context):
        domain_name, base_url = multi_domain_context

        # Создание страницы из домен-зависимого аутентифицированного контекста
        page = domain_aware_authenticated_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            # Переход на главную страницу
            page.goto(base_url, wait_until="domcontentloaded")
            burger_menu.smart_wait_for_page_ready()  # Умное ожидание готовности страницы

            burger_menu.open_menu()

            # Используем custom селектор из baseline как в smoke version
            page.locator("a.menu_item_link[href*='goryachie-temy-200085']").first.click()

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            assert "goryachie-temy-200085" in current_url.lower(), \
                f"URL не содержит goryachie-temy-200085: {current_url}"
        finally:
            page.close()
