"""
Тест навигации по разделу 'Задать вопрос' в бургер-меню.

Проверяет корректность перехода на страницу задания вопроса.
"""

import pytest
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage


@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.cross_domain
class TestAskQuestionNavigationParams:
    @pytest.mark.parametrize(
        'multi_domain_context',
        ['bll', 'expert', 'bonus', 'ca', 'cp'],
        indirect=True,
        ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP']
    )
    def test_ask_question_navigation(
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
            burger_menu.click_link_by_text("Задать вопрос")

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            assert "expert.bll.by" in current_url.lower(), \
                f"URL не содержит expert.bll.by: {current_url}"
        finally:
            page.close()
