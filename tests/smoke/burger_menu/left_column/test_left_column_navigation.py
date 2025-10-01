"""
Тесты навигации левой колонки бургер-меню.

Эти тесты проверяют стабильную навигацию по левой колонке меню.
Все тесты используют базовый класс с общей логикой.
"""

import allure
import pytest

from tests.smoke.burger_menu.base_burger_menu_test import BaseBurgerMenuNavigationTest


class TestLeftColumnNavigation(BaseBurgerMenuNavigationTest):
    """
    Тесты навигации по левой колонке бургер-меню.

    Включает все стабильные тесты, которые проходят в CI/CD.
    """

    @allure.title("Навигация: Новости")
    @allure.description("Проверка перехода в Новости - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    @pytest.mark.critical
    def test_news_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Новости".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/news
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate(page, "Новости", "https://bll.by/news")
        finally:
            page.close()

    @allure.title("Навигация: Справочная информация")
    @allure.description("Проверка перехода в Справочную информацию - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    @pytest.mark.critical
    def test_reference_info_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Справочная информация".

        Проверяет:
        - Статус код: 200
        - URL ID: 200083
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate_docs(page, "Справочная информация", "200083")
        finally:
            page.close()

    @allure.title("Навигация: Кодексы")
    @allure.description("Проверка перехода в Кодексы - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    @pytest.mark.critical
    def test_codes_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Кодексы".

        Проверяет:
        - Статус код: 200
        - URL ID: 141580
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate_docs(page, "Кодексы", "141580")
        finally:
            page.close()

    @allure.title("Навигация: Чек-листы")
    @allure.description("Проверка перехода в Чек-листы - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_checklists_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Чек-листы".

        Проверяет:
        - Статус код: 200
        - URL ID: 487105
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate_docs(page, "Чек-листы", "487105")
        finally:
            page.close()

    @allure.title("Навигация: Каталоги форм")
    @allure.description("Проверка перехода в Каталоги форм - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_catalogs_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Каталоги форм".

        Проверяет:
        - Статус код: 200
        - URL ID: 22555
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate_docs(page, "Каталоги форм", "22555")
        finally:
            page.close()

    @allure.title("Навигация: Словарь")
    @allure.description("Проверка перехода в Словарь - статус код и точный URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_dictionary_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Словарь".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/terms (точное совпадение)
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate(page, "Словарь", "https://bll.by/terms")
        finally:
            page.close()

    @allure.title("Навигация: Конструкторы")
    @allure.description("Проверка перехода в Конструкторы - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_constructors_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Конструкторы".

        Проверяет:
        - Статус код: 200
        - URL ID: 200077
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate_docs(page, "Конструкторы", "200077")
        finally:
            page.close()

    @allure.title("Навигация: Горячие темы")
    @allure.description("Проверка перехода в Горячие темы - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_hot_topics_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Горячие темы".

        Проверяет:
        - Статус код: 200
        - URL ID: 200085
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate_docs(page, "Горячие темы", "200085")
        finally:
            page.close()

    @allure.title("Навигация: Всё по одной теме")
    @allure.description("Проверка перехода в Всё по одной теме - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_topic_collections_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Всё по одной теме".

        Проверяет:
        - Статус код: 200
        - URL ID: 200084
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate_docs(page, "Всё по одной теме", "200084")
        finally:
            page.close()

    @allure.title("Навигация: О платформе")
    @allure.description("Проверка перехода в О платформе - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_about_platform_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "О платформе".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/about
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate(page, "О платформе", "https://bll.by/about")
        finally:
            page.close()