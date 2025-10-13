"""
Burger Menu Right Column - My Data Navigation - Multi-Domain Parameterized Tests.

Параметризованные тесты раздела 'Мои данные' правой колонки бургер-меню.
Тестирует навигацию в личные данные пользователя на всех доменах.
Поддерживает умную авторизацию с правильными параметрами куки.
Использует SmartAuthManager для автоматической проверки и обновления сессии.
"""

import pytest
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage

@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.right_column
class TestMyDataNavigationParams:
    @pytest.mark.parametrize('multi_domain_context',
                            ['bll', 'expert', 'bonus', 'ca', 'cp'],
                            indirect=True,
                            ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_my_data_navigation(self, multi_domain_context, domain_aware_authenticated_context):
        """
        Мульти-домен доступ к разделу 'Мои данные' - enterprise coverage.

        Тестирует переход в личные данные пользователя на каждом домене.
        Домены могут иметь разные UI для доступа к личным данным.
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
            burger_menu.click_link_by_role("Мои данные")

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            # My data should redirect to ca.bll.by/user/profile for most domains
            assert "ca.bll.by" in current_url.lower() and "user/profile" in current_url.lower(), \
                f"URL не содержит ca.bll.by/user/profile: {current_url}"
        finally:
            page.close()
