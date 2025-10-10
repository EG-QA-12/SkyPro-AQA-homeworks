"""
Объединенные тесты навигации по левой колонке бургер-меню.

Заменяет ~30 отдельных файлов одним параметризованным тестом.
Полностью соответствует принципам AQA с Allure разметкой и автоматической диагностикой.
"""

import pytest
import allure
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage
from framework.utils.http_assert_utils import assert_http_status_with_better_message
from framework.utils.reporting.allure_utils import ui_test


# Данные для параметризации - заменяют 30+ отдельных тестов
LEFT_COLUMN_TEST_DATA = [
    # (link_text, expected_url_contains, description)
    ("О Платформе", "about", "Навигация на страницу 'О Платформе'"),
    ("Задать вопрос", "expert.bll.by", "Переход к форме задания вопроса"),
    ("Купить", "buy", "Навигация на страницу покупок"),
    ("Калькуляторы", "calculators", "Переход к калькуляторам"),
    ("Каталоги", "catalogs", "Навигация по каталогам"),
    ("Чек-листы", "checklists", "Переход к чек-листам"),
    ("Коды", "codes", "Навигация по кодам"),
    ("Поиск сообщества", "community", "Переход к поиску сообщества"),
    ("Конструкторы", "constructors", "Навигация по конструкторам"),
    ("Проверка контрагента", "contractor", "Переход к проверке контрагента"),
    ("Доступ к демо", "demo", "Навигация к демо-доступу"),
    ("Справочники", "directories", "Переход к справочникам"),
    ("Документы", "docs", "Навигация по документам"),
    ("Поиск документов", "document", "Переход к поиску документов"),
    ("События", "events", "Навигация по событиям"),
    ("Экспертный раздел", "expert", "Переход к экспертному разделу"),
    ("Клуб экспертов", "experts", "Навигация к клубу экспертов"),
    ("Главная страница", "/", "Возврат на главную"),
    ("Горячие темы", "hot", "Переход к горячим темам"),
    ("Сообщения модератора", "moderator", "Навигация к сообщениям модератора"),
    ("Мои вопросы/ответы", "questions", "Переход к моим вопросам"),
    ("Навигаторы", "navigators", "Навигация по навигаторам"),
    ("Новости", "news", "Переход к новостям"),
    ("Личный юрист", "lawyer", "Навигация к личному юристу"),
    ("Номер телефона", "phone", "Переход к номеру телефона"),
    ("Закупки", "procurement", "Навигация по закупкам"),
    ("Справочная информация", "reference", "Переход к справочной информации"),
    ("Поддержка", "support", "Навигация к поддержке"),
    ("Тесты", "tests", "Переход к тестам"),
    ("Коллекции тем", "collections", "Навигация по коллекциям тем"),
    ("Управление темами", "topics", "Переход к управлению темами"),
    ("Полезные ссылки", "links", "Навигация по полезным ссылкам"),
    ("Руководство пользователя", "guide", "Переход к руководству"),
    ("Видеоответы", "video", "Навигация к видеоответам"),
]


@pytest.mark.smoke
@pytest.mark.burger_menu_params
@pytest.mark.left_column
class TestLeftColumnNavigationParams:
    """Объединенные тесты навигации по левой колонке бургер-меню."""

    @pytest.mark.parametrize(
        'multi_domain_context',
        ['bll', 'expert', 'bonus', 'ca', 'cp'],
        indirect=True,
        ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP']
    )
    @pytest.mark.parametrize(
        'link_text,expected_url_contains,test_description',
        LEFT_COLUMN_TEST_DATA,
        ids=[item[0] for item in LEFT_COLUMN_TEST_DATA]
    )
    @ui_test(
        title="Навигация по левой колонке бургер-меню: {link_text}",
        description="Проверяет корректность перехода по ссылке '{link_text}' "
                   "в левой колонке бургер-меню",
        feature="Бургер-меню: Левая колонка",
        story="Навигация по разделам"
    )
    def test_left_column_navigation(
        self,
        domain_aware_authenticated_context,
        multi_domain_context,
        playwright_allure,
        link_text,
        expected_url_contains,
        test_description
    ):
        """
        Параметризованный тест навигации по левой колонке бургер-меню.

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
                self._verify_navigation(page, expected_url_contains, base_url, link_text)

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

    def _verify_navigation(self, page, expected_url_contains, base_url, link_text):
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

        # Специальная обработка для разных типов ссылок
        if link_text == "Задать вопрос":
            # Проверяем переход на expert.bll.by
            assert "expert.bll.by" in current_url, (
                f"URL должен содержать expert.bll.by: {current_url}"
            )

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

        elif link_text == "Главная страница":
            # Для главной страницы проверяем базовый URL
            assert expected_url_contains in current_url or base_url.rstrip('/') in current_url, (
                f"URL должен содержать '{expected_url_contains}' или базовый URL: {current_url}"
            )

        else:
            # Стандартная проверка для остальных ссылок
            assert expected_url_contains.lower() in current_url.lower(), (
                f"URL должен содержать '{expected_url_contains}': {current_url}"
            )