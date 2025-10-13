"""
Burger Menu Left Column - Reference Info Navigation - Multi-Domain Parameterized Tests.

Параметризованные тесты раздела 'Справочная информация' левой колонки бургер-меню.
Использует regex pattern с ID для надежности.
Поддерживает headless режим с allow-session параметром для обхода защиты от ботов.
"""

import pytest
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
        domain_name, base_url = multi_domain_context

        # Создание страницы из домен-зависимого аутентифицированного контекста
        page = domain_aware_authenticated_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            # Переход на главную страницу
            page.goto(base_url, wait_until="domcontentloaded")
            burger_menu.smart_wait_for_page_ready()  # Умное ожидание готовности страницы

            burger_menu.open_menu()

            # Текст клик как в baseline
            burger_menu.click_link_by_text("Справочная информация")

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            assert "spravochnaya-informatsiya-200083" in current_url.lower(), \
                f"URL не содержит spravochnaya-informatsiya-200083: {current_url}"
        finally:
            page.close()
