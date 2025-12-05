"""
Оптимизированные тесты навигации по левой колонке бургер-меню.

Простые и читаемые тесты с параметризацией.
Используют проверенные селекторы из рабочего baseline.
"""

import pytest
import allure
from tests.smoke.burger_menu_best.pages.burger_menu_page import BurgerMenuPage


# Простые данные для параметризации - без over-engineering
LEFT_COLUMN_TEST_DATA = [
    # (link_text, expected_url_contains, description)
    ("О Платформе", "about", "Навигация на страницу 'О Платформе'"),
    ("Задать вопрос", "expert.bll.by", "Переход к форме задания вопроса"),
    ("Купить", "buy", "Навигация на страницу покупок"),
    ("Калькуляторы", "kalkulyatory", "Переход к калькуляторам"),
    ("Каталоги", "katalogi", "Навигация по каталогам"),
    ("Чек-листы", "perechen-tem-chek-list", "Переход к чек-листам"),
    ("Кодексы", "kodeksy", "Навигация по кодексам"),
    ("Поиск в сообществе", "expert.bll.by", "Переход к поиску в сообществе"),
    ("Конструкторы", "konstruktory", "Навигация по конструкторам"),
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
@pytest.mark.burger_menu
@pytest.mark.left_column
class TestLeftColumnNavigationBest:
    """
    Оптимизированные тесты навигации по левой колонке бургер-меню.
    """

    @pytest.mark.parametrize(
        'link_text,expected_url_contains,test_description',
        LEFT_COLUMN_TEST_DATA,
        ids=[item[0] for item in LEFT_COLUMN_TEST_DATA]
    )
    def test_left_column_navigation_simple(
        self,
        burger_menu_page,
        link_text,
        expected_url_contains,
        test_description
    ):
        """
        Простой параметризованный тест навигации.

        Args:
            burger_menu_page: Фикстура для работы с меню
            link_text: Текст ссылки для клика
            expected_url_contains: Ожидаемая подстрока в URL
            test_description: Описание теста
        """
        # Создаем экземпляр Page Object
        menu = BurgerMenuPage(burger_menu_page)

        # Открываем меню
        menu.open_menu()

        # Кликаем по ссылке
        menu.click_link_by_text(link_text)

        # Проверяем навигацию
        assert menu.verify_navigation(expected_url_contains), (
            f"Навигация по ссылке '{link_text}' не выполнена. "
            f"Ожидалось: {expected_url_contains}, "
            f"Получили: {burger_menu_page.url}"
        )
