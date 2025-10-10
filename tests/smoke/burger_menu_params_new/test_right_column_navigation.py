"""
Объединенные тесты навигации по правой колонке бургер-меню.

Заменяет ~9 отдельных файлов одним параметризованным тестом.
Полностью соответствует принципам AQA с Allure разметкой и автоматической диагностикой.
"""

import pytest
import allure
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage
from framework.utils.http_assert_utils import assert_http_status_with_better_message
from framework.utils.reporting.allure_utils import ui_test


# Данные для параметризации - заменяют 9 отдельных тестов
RIGHT_COLUMN_TEST_DATA = [
    # (link_text, expected_check, description)
    ("Бонусы", "bonus", "Навигация к бонусам"),
    ("Коллекции и закладки", "collections", "Переход к коллекциям"),
    ("Управление документами", "documents", "Навигация к управлению документами"),
    ("Профиль эксперта", "expert", "Переход к профилю эксперта"),
    ("Мои данные", "data", "Навигация к моим данным"),
    ("Новые документы", "new", "Переход к новым документам"),
    ("Настройки уведомлений", "notification", "Навигация к настройкам уведомлений"),
    ("Личный кабинет", "account", "Переход в личный кабинет"),
    ("Напоминания", "reminders", "Навигация к напоминаниям"),
]


@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.right_column
class TestRightColumnNavigationParams:
    """Объединенные тесты навигации по правой колонке бургер-меню."""

    @pytest.mark.parametrize(
        'multi_domain_context',
        ['bll', 'expert', 'bonus', 'ca', 'cp'],
        indirect=True,
        ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP']
    )
    @pytest.mark.parametrize(
        'link_text,expected_url_contains,test_description',
        RIGHT_COLUMN_TEST_DATA,
        ids=[item[0] for item in RIGHT_COLUMN_TEST_DATA]
    )
    @ui_test(
        title="Навигация по правой колонке бургер-меню: {link_text}",
        description="Проверяет корректность перехода по ссылке '{link_text}' "
                   "в правой колонке бургер-меню",
        feature="Бургер-меню: Правая колонка",
        story="Навигация по персональным разделам"
    )
    def test_right_column_navigation(
        self,
        domain_aware_authenticated_context,
        multi_domain_context,
        playwright_allure,
        link_text,
        expected_url_contains,
        test_description
    ):
        """
        Параметризованный тест навигации по правой колонке бургер-меню.

        Args:
            domain_aware_authenticated_context: Аутентифицированный контекст браузера
            multi_domain_context: Кортеж (domain_name, base_url)
            playwright_allure: Fixture для автоматической диагностики
            link_text: Текст ссылки для клика
            expected_url_contains: Ожидаемая подстрока в URL
            test_description: Описание теста для Allure
        """
        domain_name, base_url = multi_domain_context

        # Создание страницы из домен-зависимого аутентифицированного контекста
        page = domain_aware_authenticated_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            with allure.step("Переход на главную страницу"):
                page.goto(base_url, wait_until="domcontentloaded")
                burger_menu.smart_wait_for_page_ready()

            with allure.step("Открытие бургер-меню"):
                burger_menu.open_menu()

            with allure.step(f"Клик по ссылке '{link_text}'"):
                self._click_menu_link_with_retry(burger_menu, link_text)

            with allure.step("Проверка корректности перехода"):
                self._verify_navigation(page, expected_url_contains, base_url, link_text, burger_menu, domain_name)

        finally:
            with allure.step("Закрытие страницы"):
                page.close()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def _click_menu_link_with_retry(self, burger_menu, link_text):
        """
        Клик по ссылке меню с механизмом повторных попыток.

        Args:
            burger_menu: Экземпляр BurgerMenuPage
            link_text: Текст ссылки для клика
        """
        try:
            burger_menu.click_link_by_text(link_text)
        except Exception as e:
            allure.attach(
                f"Ошибка клика по '{link_text}': {str(e)}",
                name="Click Error",
                attachment_type=allure.attachment_type.TEXT
            )
            raise

    def _verify_navigation(self, page, expected_url_contains, base_url, link_text, burger_menu, domain_name):
        """
        Проверка корректности навигации после клика.

        Args:
            page: Экземпляр страницы Playwright
            expected_url_contains: Ожидаемая подстрока в URL
            base_url: Базовый URL домена
            link_text: Текст ссылки для отладки
        """
        current_url = page.url
        allure.attach(
            current_url,
            name="Current URL",
            attachment_type=allure.attachment_type.TEXT
        )

        # Специальная обработка для личного кабинета
        if link_text == "Личный кабинет":
            # Проверяем HTTP статус с понятным сообщением
            response = requests.get(current_url, allow_redirects=True)
            allure.attach(
                f"HTTP {response.status_code}: {response.url}",
                name="HTTP Response",
                attachment_type=allure.attachment_type.TEXT
            )

            assert_http_status_with_better_message(
                response.status_code,
                [200, 301, 302],
                current_url,
                f"Проверка финального URL после навигации '{link_text}'"
            )

            # Проверяем, что меню доступно (как в оригинальном тесте)
            assert burger_menu.is_menu_open(), (
                f"Бургер-меню не открылось на {domain_name}"
            )

        else:
            # Стандартная проверка для остальных ссылок
            assert expected_url_contains.lower() in current_url.lower(), (
                f"URL должен содержать '{expected_url_contains}': {current_url}"
            )