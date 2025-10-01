"""
Тесты навигации левой колонки бургер-меню.

Эти тесты проверяют стабильную навигацию по левой колонке меню.
Все тесты используют базовый класс с общей логикой.
Включает все 33 стабильных теста из оригинального файла.
"""

import allure
import pytest

from tests.smoke.burger_menu.base_burger_menu_test import BaseBurgerMenuNavigationTest


class TestLeftColumnNavigation(BaseBurgerMenuNavigationTest):
    """
    Тесты навигации по левой колонке бургер-меню.

    Включает все стабильные тесты (33 шт), которые проходят в CI/CD.
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

    @allure.title("Навигация: Справочники")
    @allure.description("Проверка перехода в Справочники - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_directories_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Справочники".

        Проверяет:
        - Статус код: 200
        - URL ID: 220099
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate_docs(page, "Справочники", "220099")
        finally:
            page.close()

    @allure.title("Навигация: Калькуляторы")
    @allure.description("Проверка перехода в Калькуляторы - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_calculators_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Калькуляторы".

        Проверяет:
        - Статус код: 200
        - URL ID: 40171
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate_docs(page, "Калькуляторы", "40171")
        finally:
            page.close()

    @allure.title("Навигация: Тесты")
    @allure.description("Проверка перехода в Тесты - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_tests_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Тесты".

        Проверяет:
        - Статус код: 200
        - URL ID: 212555
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate_docs(page, "Тесты", "212555")
        finally:
            page.close()

    @allure.title("Навигация: Навигаторы")
    @allure.description("Проверка перехода в Навигаторы - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_navigators_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Навигаторы".

        Проверяет:
        - Статус код: 200
        - URL ID: 140000
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate_docs(page, "Навигаторы", "140000")
        finally:
            page.close()

    @allure.title("Навигация: Полезные ссылки")
    @allure.description("Проверка перехода в Полезные ссылки - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_useful_links_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Полезные ссылки".

        Проверяет:
        - Статус код: 200
        - URL ID: 219924
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate_docs(page, "Полезные ссылки", "219924")
        finally:
            page.close()

    @allure.title("Навигация: Ваш личный юрист")
    @allure.description("Проверка перехода к личному юристу - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_personal_lawyer_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Ваш личный юрист".

        Проверяет:
        - Статус код: 200
        - URL ID: 206044
        """
        page = authenticated_burger_context.new_page()
        try:
            # Переход на главную страницу
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Обеспечиваем авторизацию
            self._ensure_authenticated(page)

            self._navigate_and_validate_docs(page, "Ваш личный юрист", "206044")
        finally:
            page.close()

    @allure.title("Навигация: Всё по одной теме")
    @allure.description("Проверка перехода в Подборки по темам - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_topic_collections_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Всё по одной теме".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_docs(page, "Всё по одной теме", "200084")
        finally:
            page.close()

    @allure.title("Навигация: Руководство пользователя")
    @allure.description("Проверка перехода к руководству пользователя - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_user_guide_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Руководство пользователя".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_docs(page, "Руководство пользователя", "436351")
        finally:
            page.close()

    @allure.title("Навигация: Видеоответы")
    @allure.description("Проверка перехода в Видеоответы - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_video_answers_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Видеоответы".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_docs(page, "Видеоответы", "490299")
        finally:
            page.close()

    @allure.title("Навигация: Закупки")
    @allure.description("Проверка перехода в Закупки - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_procurement_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Закупки".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_external(page, "Закупки", "gz.bll.by")
        finally:
            page.close()

    @allure.title("Навигация: Главная страница")
    @allure.description("Проверка перехода на Главную страницу - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_home_page_navigation(self, authenticated_burger_context):
        """
        Проверка навигации на главную страницу.
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/docs", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate(page, "Главная страница", "https://bll.by/")
        finally:
            page.close()

    @allure.title("Навигация: Купить")
    @allure.description("Проверка перехода в Купить - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_buy_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Купить".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate(page, "Купить", "https://bll.by/buy")
        finally:
            page.close()

    @allure.title("Навигация: Получить демодоступ")
    @allure.description("Проверка перехода в Получить демодоступ - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_demo_access_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Получить демодоступ".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate(page, "Получить демодоступ", "https://bll.by/buy?request")
        finally:
            page.close()

    @allure.title("Навигация: Мероприятия")
    @allure.description("Проверка перехода в Мероприятия - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_events_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Мероприятия".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_docs(page, "Мероприятия", "471630")
        finally:
            page.close()

    @allure.title("Навигация: Поиск в базе документов")
    @allure.description("Проверка перехода в Поиск в базе документов - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_document_search_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Поиск в базе документов".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate(page, "Поиск в базе документов", "https://bll.by/docs")
        finally:
            page.close()

    @allure.title("Навигация: Поиск в сообществе")
    @allure.description("Проверка перехода в Поиск в сообществе - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_community_search_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Поиск в сообществе".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_external(page, "Поиск в сообществе", "expert.bll.by")
        finally:
            page.close()

    @allure.title("Навигация: Проверка контрагента")
    @allure.description("Проверка перехода в Проверка контрагента - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_contractor_check_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Проверка контрагента".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_external(page, "Проверка контрагента", "cp.bll.by")
        finally:
            page.close()

    @allure.title("Навигация: Задать вопрос")
    @allure.description("Проверка перехода в Задать вопрос - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_ask_question_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Задать вопрос".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_external(page, "Задать вопрос", "expert.bll.by")
        finally:
            page.close()

    @allure.title("Навигация: Мои вопросы и ответы")
    @allure.description("Проверка перехода в Мои вопросы и ответы - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_my_questions_answers_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Мои вопросы и ответы".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_external(page, "Мои вопросы и ответы", "expert.bll.by")
        finally:
            page.close()

    @allure.title("Навигация: Топики на контроле")
    @allure.description("Проверка перехода в Топики на контроле - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_topics_control_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Топики на контроле".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_external(page, "Топики на контроле", "expert.bll.by")
        finally:
            page.close()

    @allure.title("Навигация: Сообщения от модератора")
    @allure.description("Проверка перехода в Сообщения от модератора - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_moderator_messages_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Сообщения от модератора".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_external(page, "Сообщения от модератора", "expert.bll.by")
        finally:
            page.close()

    @allure.title("Навигация: Мне - эксперту")
    @allure.description("Проверка перехода в Мне - эксперту - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_expert_section_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Мне - эксперту".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_external(page, "Мне - эксперту", "expert.bll.by")
        finally:
            page.close()

    @allure.title("Навигация: Клуб экспертов")
    @allure.description("Проверка перехода в Клуб экспертов - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_experts_club_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Клуб экспертов".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_external(page, "Клуб экспертов", "expert.bll.by")
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
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate(page, "О платформе", "https://bll.by/about")
        finally:
            page.close()

    @allure.title("Навигация: Телефонный номер")
    @allure.description("Проверка клика по телефонному номеру - открытие приложения")
    @pytest.mark.burger_menu
    @pytest.mark.left_column
    @pytest.mark.stable
    def test_phone_number_click(self, authenticated_burger_context):
        """
        Проверка клика по телефонному номеру "+375 17 388 32 52".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)

            phone_link = page.get_by_role("link", name="+375 17 388 32")
            assert phone_link.is_visible(), "Телефонная ссылка не найдена"
            phone_href = phone_link.get_attribute("href")
            assert phone_href and phone_href.startswith("tel:"), f"Неверный href для телефонной ссылки: {phone_href}"

        finally:
            page.close()
