"""
Рефакторированные E2E тесты навигации бургер-меню.

Эти тесты проверяют ТОЛЬКО:
- Статус код ответа (200/201)
- Корректность URL перехода

Используют умную логику сравнения URL:
- Для docs URL сравнивают только ID (487105)
- Для остальных URL - полное сравнение

Убирают проверки контента страниц для повышения стабильности.
"""
import re
import allure
import pytest
from playwright.sync_api import expect

from tests.e2e.pages.burger_menu_page import BurgerMenuPage


class TestBurgerMenuNavigationRefactored:
    """
    Рефакторированные тесты навигации бургер-меню.

    Проверяют только статус код и URL, без валидации контента.
    """

    @allure.title("Навигация: Новости")
    @allure.description("Проверка перехода в Новости - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    @pytest.mark.critical
    def test_news_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Новости".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/news
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            # Переход на главную
            page.goto("https://bll.by/", wait_until="domcontentloaded")

            # Открытие меню
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            # Переход по ссылке с проверкой ответа
            with page.expect_response(lambda response: response.url == "https://bll.by/news") as response_info:
                assert burger_menu.click_link_by_text("Новости"), "Не удалось кликнуть по ссылке 'Новости'"

            # Проверка статус кода
            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            # Проверка URL
            expect(page).to_have_url("https://bll.by/news")

        finally:
            page.close()

    @allure.title("Навигация: Справочная информация")
    @allure.description("Проверка перехода в Справочную информацию - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    @pytest.mark.critical
    def test_reference_info_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Справочная информация".

        Проверяет:
        - Статус код: 200
        - URL ID: 200083 (текстовая часть может меняться)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            # Переход на главную
            page.goto("https://bll.by/", wait_until="domcontentloaded")

            # Открытие меню
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            # Переход по ссылке с проверкой ответа
            with page.expect_response("**/spravochnaya-informatsiya-200083**") as response_info:
                assert burger_menu.click_link_by_text("Справочная информация"), "Не удалось кликнуть по ссылке"

            # Проверка статус кода
            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            # Умная проверка URL - сравнение только ID
            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "200083"), \
                f"URL не содержит ожидаемый ID 200083: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Кодексы")
    @allure.description("Проверка перехода в Кодексы - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    @pytest.mark.critical
    def test_codes_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Кодексы".

        Проверяет:
        - Статус код: 200
        - URL ID: 141580
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/kodeksy-dejstvuyushchie-na-territorii-respubliki-belarus-141580**") as response_info:
                assert burger_menu.click_link_by_text("Кодексы"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "141580"), \
                f"URL не содержит ожидаемый ID 141580: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Чек-листы")
    @allure.description("Проверка перехода в Чек-листы - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_checklists_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Чек-листы".

        Проверяет:
        - Статус код: 200
        - URL ID: 487105
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/perechen-tem-chek-list-dokumentov-487105**") as response_info:
                assert burger_menu.click_link_by_text("Чек-листы"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "487105"), \
                f"URL не содержит ожидаемый ID 487105: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Каталоги форм")
    @allure.description("Проверка перехода в Каталоги форм - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_catalogs_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Каталоги форм".

        Проверяет:
        - Статус код: 200
        - URL ID: 22555
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/katalogi-form-22555**") as response_info:
                assert burger_menu.click_link_by_text("Каталоги форм"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "22555"), \
                f"URL не содержит ожидаемый ID 22555: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Словарь")
    @allure.description("Проверка перехода в Словарь - статус код и точный URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_dictionary_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Словарь".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/terms (точное совпадение)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/terms**") as response_info:
                assert burger_menu.click_link_by_text("Словарь"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            # Для словаря - точное сравнение URL
            expect(page).to_have_url("https://bll.by/terms")

        finally:
            page.close()

    @allure.title("Навигация: Конструкторы")
    @allure.description("Проверка перехода в Конструкторы - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_constructors_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Конструкторы".

        Проверяет:
        - Статус код: 200
        - URL ID: 200077
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/konstruktory-200077**") as response_info:
                assert burger_menu.click_link_by_text("Конструкторы"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "200077"), \
                f"URL не содержит ожидаемый ID 200077: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Справочники")
    @allure.description("Проверка перехода в Справочники - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_directories_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Справочники".

        Проверяет:
        - Статус код: 200
        - URL ID: 220099
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/spravochniki-220099**") as response_info:
                assert burger_menu.click_link_by_text("Справочники"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "220099"), \
                f"URL не содержит ожидаемый ID 220099: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Калькуляторы")
    @allure.description("Проверка перехода в Калькуляторы - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_calculators_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Калькуляторы".

        Проверяет:
        - Статус код: 200
        - URL ID: 40171
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/kalkulyatory-40171**") as response_info:
                assert burger_menu.click_link_by_text("Калькуляторы"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "40171"), \
                f"URL не содержит ожидаемый ID 40171: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Тесты")
    @allure.description("Проверка перехода в Тесты - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_tests_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Тесты".

        Проверяет:
        - Статус код: 200
        - URL ID: 212555
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/testy-dlya-proverki-znanij-212555**") as response_info:
                assert burger_menu.click_link_by_text("Тесты"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "212555"), \
                f"URL не содержит ожидаемый ID 212555: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Горячие темы")
    @allure.description("Проверка перехода в Горячие темы - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_hot_topics_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Горячие темы".

        Проверяет:
        - Статус код: 200
        - URL ID: 200085
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/goryachie-temy-200085**") as response_info:
                assert burger_menu.click_link_by_text("Горячие темы"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "200085"), \
                f"URL не содержит ожидаемый ID 200085: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Навигаторы")
    @allure.description("Проверка перехода в Навигаторы - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_navigators_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Навигаторы".

        Проверяет:
        - Статус код: 200
        - URL ID: 140000
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/navigatory-140000**") as response_info:
                assert burger_menu.click_link_by_text("Навигаторы"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "140000"), \
                f"URL не содержит ожидаемый ID 140000: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Полезные ссылки")
    @allure.description("Проверка перехода в Полезные ссылки - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_useful_links_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Полезные ссылки".

        Проверяет:
        - Статус код: 200
        - URL ID: 219924
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/poleznye-ssylki-219924**") as response_info:
                assert burger_menu.click_link_by_text("Полезные ссылки"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "219924"), \
                f"URL не содержит ожидаемый ID 219924: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Ваш личный юрист")
    @allure.description("Проверка перехода к личному юристу - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_personal_lawyer_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Ваш личный юрист".

        Проверяет:
        - Статус код: 200
        - URL ID: 206044
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/vash-lichnyj-yurist-206044**") as response_info:
                assert burger_menu.click_link_by_text("Ваш личный юрист"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "206044"), \
                f"URL не содержит ожидаемый ID 206044: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Всё по одной теме")
    @allure.description("Проверка перехода в подборки по темам - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_topic_collections_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Всё по одной теме".

        Проверяет:
        - Статус код: 200
        - URL ID: 200084
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/podborki-vsyo-po-odnoj-teme-200084**") as response_info:
                assert burger_menu.click_link_by_text("Всё по одной теме"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "200084"), \
                f"URL не содержит ожидаемый ID 200084: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Руководство пользователя")
    @allure.description("Проверка перехода к руководству пользователя - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_user_guide_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Руководство пользователя".

        Проверяет:
        - Статус код: 200
        - URL ID: 436351
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/rukovodstvo-polzovatelya-platformy-biznes-info-436351**") as response_info:
                assert burger_menu.click_link_by_text("Руководство пользователя"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "436351"), \
                f"URL не содержит ожидаемый ID 436351: {current_url}"

        finally:
            page.close()