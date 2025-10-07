"""
Тест навигации по разделу 'Задать вопрос' в бургер-меню.

Проверяет корректность перехода на страницу задания вопроса.
"""

import pytest
import requests
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage
from framework.utils.http_assert_utils import assert_http_status_with_better_message


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
            burger_menu.smart_wait_for_page_ready()  # Allow page to stabilize

            # Открытие бургер-меню
            burger_menu.open_menu()

            # Use page.get_by_role for precise element selection
            ask_link = page.get_by_role("banner").get_by_role(
                "link", name="Задать вопрос"
            )
            ask_link.click()

            # Check the final URL (with redirects followed)
            current_url = page.url
            print(f"Текущий URL: {current_url}")  # Для отладки

            # Cross-domain navigation to expert question creation page
            assert "expert.bll.by" in current_url, (
                f"URL должен содержать expert.bll.by: {current_url}"
            )

            # Allow redirects to follow final destination
            response = requests.get(current_url, allow_redirects=True)
            print(f"HTTP статус после редиректов: {response.status_code}")
            print(f"Финальный URL: {response.url}")

            # Проверяем HTTP статус с понятным сообщением об ошибке
            assert_http_status_with_better_message(
                response.status_code,
                [200, 301, 302],
                current_url,
                "Проверка финального URL после навигации 'Задать вопрос'"
            )

        finally:
            page.close()
