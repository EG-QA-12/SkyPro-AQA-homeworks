"""
Burger Menu Right Column - Personal Account Navigation - Multi-Domain Parameterized Tests.

Параметризованные тесты раздела 'Личный кабинет' правой колонки бургер-меню.
Тестирует навигацию в персональный аккаунт на всех доменах.
Поддерживает умную авторизацию с правильными параметрами куки.
Использует SmartAuthManager для автоматической проверки и обновления сессии.
"""

import pytest
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

        # Создание страницы из домен-зависимого аутентифицированного контекста
        page = domain_aware_authenticated_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            # Переход на главную страницу
            page.goto(base_url, wait_until="domcontentloaded")
            burger_menu.smart_wait_for_page_ready()  # Умное ожидание готовности страницы

            burger_menu.open_menu()
            burger_menu.click_link_by_role("Личный кабинет")

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            # Personal account should redirect to business-info.by/pc for most domains
            assert "business-info.by" in current_url.lower() and "/pc" in current_url.lower(), \
                f"URL не содержит business-info.by/pc: {current_url}"
        finally:
            page.close()
