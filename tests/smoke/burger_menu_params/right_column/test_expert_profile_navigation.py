"""
Burger Menu Right Column - Expert Profile Navigation - Multi-Domain Parameterized Tests.

Параметризованные тесты раздела 'Я эксперт' правой колонки бургер-меню.
Тестирует навигацию в экспертный профиль на всех доменах.
Поддерживает умную авторизацию с правильными параметрами куки.
Использует SmartAuthManager для автоматической проверки и обновления сессии.
"""

import pytest
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage

@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.right_column
class TestExpertProfileNavigationParams:
    @pytest.mark.parametrize('multi_domain_context',
                            ['bll', 'expert', 'bonus', 'ca', 'cp'],
                            indirect=True,
                            ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
    def test_expert_profile_navigation(self, multi_domain_context, domain_aware_authenticated_context):
        """
        Мульти-домен доступ к экспертному профилю - enterprise coverage.

        Тестирует переход в экспертный профиль.
        Перенаправляет на expert.bll.by/user/expert для большинства доменов.
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
            burger_menu.click_link_by_role("Я эксперт")

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            # Expert profile should redirect to expert.bll.by/user/expert
            assert "expert.bll.by" in current_url.lower() and "user/expert" in current_url.lower(), \
                f"URL не содержит expert.bll.by/user/expert: {current_url}"
        finally:
            page.close()
