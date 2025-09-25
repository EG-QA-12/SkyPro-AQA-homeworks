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

    @allure.title("Навигация: Видеоответы")
    @allure.description("Проверка перехода в Видеоответы - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_video_answers_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Видеоответы".

        Проверяет:
        - Статус код: 200
        - URL ID: 490299
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/videootvety-490299**") as response_info:
                assert burger_menu.click_link_by_text("Видеоответы"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "490299"), \
                f"URL не содержит ожидаемый ID 490299: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Закупки")
    @allure.description("Проверка перехода в Закупки - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_procurement_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Закупки".

        Проверяет:
        - Статус код: 200
        - URL: https://gz.bll.by (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("https://gz.bll.by") as response_info:
                assert burger_menu.click_link_by_text("Закупки"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена проверяем, что URL содержит gz.bll.by (учитывая редиректы на авторизацию)
            current_url = page.url
            assert "gz.bll.by" in current_url, f"URL не содержит gz.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Главная страница")
    @allure.description("Проверка перехода на Главную страницу - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_home_page_navigation(self, authenticated_burger_context):
        """
        Проверка навигации на главную страницу.

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by (возврат на главную)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            # Сначала перейдем на другую страницу
            page.goto("https://bll.by/docs", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            # Ищем ссылку "Главная страница" по селектору a.menu_bl_ttl-main
            home_link = page.locator("a.menu_bl_ttl-main").first

            with page.expect_response("https://bll.by/") as response_info:
                home_link.click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            # Проверка возврата на главную страницу
            expect(page).to_have_url("https://bll.by/")

        finally:
            page.close()

    @allure.title("Навигация: О Платформе")
    @allure.description("Проверка перехода в О Платформе - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_about_platform_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "О Платформе".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/about
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/about**") as response_info:
                assert burger_menu.click_link_by_text("О Платформе"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            # Точное сравнение для статического URL
            expect(page).to_have_url("https://bll.by/about")

        finally:
            page.close()

    @allure.title("Навигация: Купить")
    @allure.description("Проверка перехода в Купить - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_buy_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Купить".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/buy
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/buy**") as response_info:
                assert burger_menu.click_link_by_text("Купить"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            # Точное сравнение для страницы покупки
            expect(page).to_have_url("https://bll.by/buy")

        finally:
            page.close()

    @allure.title("Навигация: Получить демодоступ")
    @allure.description("Проверка перехода в Получить демодоступ - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_demo_access_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Получить демодоступ".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/buy?request
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            # Используем page.get_by_role для точного поиска ссылки "Получить демодоступ"
            demo_link = page.get_by_role("link", name="Получить демодоступ")

            with page.expect_response("**/buy?request**") as response_info:
                demo_link.click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            # Точное сравнение для страницы демодоступа
            expect(page).to_have_url("https://bll.by/buy?request")

        finally:
            page.close()

    @allure.title("Навигация: Мероприятия")
    @allure.description("Проверка перехода в Мероприятия - статус код и ID URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_events_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Мероприятия".

        Проверяет:
        - Статус код: 200
        - URL ID: 471630
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            # Ищем ссылку "Мероприятия" по селектору a.menu_bl_ttl-events
            events_link = page.locator("a.menu_bl_ttl-events").first

            with page.expect_response("**/471630**") as response_info:
                events_link.click()

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            current_url = page.url
            assert burger_menu.compare_docs_url_with_id(current_url, "471630"), \
                f"URL не содержит ожидаемый ID 471630: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Поиск в базе документов")
    @allure.description("Проверка перехода в Поиск в базе документов - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_document_search_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Поиск в базе документов".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/docs
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/docs**") as response_info:
                assert burger_menu.click_link_by_text("Поиск в базе документов"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            # Точное сравнение для страницы поиска документов
            expect(page).to_have_url("https://bll.by/docs")

        finally:
            page.close()

    @allure.title("Навигация: Поиск в сообществе")
    @allure.description("Проверка перехода в Поиск в сообществе - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_community_search_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Поиск в сообществе".

        Проверяет:
        - Статус код: 200
        - URL: https://expert.bll.by/questions (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("https://expert.bll.by/questions") as response_info:
                assert burger_menu.click_link_by_text("Поиск в сообществе"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена сообщества проверяем, что URL содержит expert.bll.by
            current_url = page.url
            assert "expert.bll.by" in current_url, f"URL не содержит expert.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Проверка контрагента")
    @allure.description("Проверка перехода в Проверка контрагента - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_contractor_check_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Проверка контрагента".

        Проверяет:
        - Статус код: 200
        - URL: https://cp.bll.by (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("https://cp.bll.by") as response_info:
                assert burger_menu.click_link_by_text("Проверка контрагента"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена проверяем, что URL содержит cp.bll.by
            current_url = page.url
            assert "cp.bll.by" in current_url, f"URL не содержит cp.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Задать вопрос")
    @allure.description("Проверка перехода в Задать вопрос - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_ask_question_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Задать вопрос".

        Проверяет:
        - Статус код: 200
        - URL: https://expert.bll.by/questions/create (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            # Используем page.get_by_role для точного поиска ссылки
            ask_link = page.get_by_role("banner").get_by_role("link", name="Задать вопрос")

            with page.expect_response("https://expert.bll.by/questions/create") as response_info:
                ask_link.click()

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена проверяем, что URL содержит expert.bll.by
            current_url = page.url
            assert "expert.bll.by" in current_url, f"URL не содержит expert.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Мои вопросы и ответы")
    @allure.description("Проверка перехода в Мои вопросы и ответы - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_my_questions_answers_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Мои вопросы и ответы".

        Проверяет:
        - Статус код: 200
        - URL: https://expert.bll.by/questions/my (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("https://expert.bll.by/questions/my") as response_info:
                assert burger_menu.click_link_by_text("Мои вопросы и ответы"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена проверяем, что URL содержит expert.bll.by
            current_url = page.url
            assert "expert.bll.by" in current_url, f"URL не содержит expert.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Топики на контроле")
    @allure.description("Проверка перехода в Топики на контроле - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_topics_control_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Топики на контроле".

        Проверяет:
        - Статус код: 200
        - URL: https://expert.bll.by/questions/watch (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            # Используем page.get_by_role для точного поиска ссылки
            topics_link = page.get_by_role("banner").get_by_role("link", name="Топики на контроле")

            with page.expect_response("https://expert.bll.by/questions/watch") as response_info:
                topics_link.click()

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена проверяем, что URL содержит expert.bll.by
            current_url = page.url
            assert "expert.bll.by" in current_url, f"URL не содержит expert.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Сообщения от модератора")
    @allure.description("Проверка перехода в Сообщения от модератора - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_moderator_messages_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Сообщения от модератора".

        Проверяет:
        - Статус код: 200
        - URL: https://expert.bll.by/moderator/messages (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("https://expert.bll.by/moderator/messages") as response_info:
                assert burger_menu.click_link_by_text("Сообщения от модератора"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена проверяем, что URL содержит expert.bll.by
            current_url = page.url
            assert "expert.bll.by" in current_url, f"URL не содержит expert.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Мне - эксперту")
    @allure.description("Проверка перехода в Мне - эксперту - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_expert_section_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Мне - эксперту".

        Проверяет:
        - Статус код: 200
        - URL: https://expert.bll.by/questions/expert (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("https://expert.bll.by/questions/expert") as response_info:
                assert burger_menu.click_link_by_text("Мне - эксперту"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена проверяем, что URL содержит expert.bll.by
            current_url = page.url
            assert "expert.bll.by" in current_url, f"URL не содержит expert.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Клуб экспертов")
    @allure.description("Проверка перехода в Клуб экспертов - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_experts_club_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Клуб экспертов".

        Проверяет:
        - Статус код: 200
        - URL: https://expert.bll.by/experts (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("https://expert.bll.by/experts") as response_info:
                assert burger_menu.click_link_by_text("Клуб экспертов"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена проверяем, что URL содержит expert.bll.by
            current_url = page.url
            assert "expert.bll.by" in current_url, f"URL не содержит expert.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Подборки и закладки")
    @allure.description("Проверка перехода в Подборки и закладки - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_collections_bookmarks_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Подборки и закладки".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/favorites
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/favorites**") as response_info:
                assert burger_menu.click_link_by_text("Подборки и закладки"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            # Точное сравнение для страницы подборок
            expect(page).to_have_url("https://bll.by/favorites")

        finally:
            page.close()

    @allure.title("Навигация: Документы на контроле")
    @allure.description("Проверка перехода в Документы на контроле - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_documents_control_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Документы на контроле".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/docs/control
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/docs/control**") as response_info:
                assert burger_menu.click_link_by_text("Документы на контроле"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            # Точное сравнение для страницы документов на контроле
            expect(page).to_have_url("https://bll.by/docs/control")

        finally:
            page.close()

    @allure.title("Навигация: Напоминания")
    @allure.description("Проверка перехода в Напоминания - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_reminders_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Напоминания".

        Проверяет:
        - Статус код: 200
        - URL: https://ca.bll.by/notification/reminder (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("https://ca.bll.by/notification/reminder") as response_info:
                assert burger_menu.click_link_by_text("Напоминания"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена проверяем, что URL содержит ca.bll.by
            current_url = page.url
            assert "ca.bll.by" in current_url, f"URL не содержит ca.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Новые документы")
    @allure.description("Проверка перехода в Новые документы - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_new_documents_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Новые документы".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/docs/new
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("**/docs/new**") as response_info:
                assert burger_menu.click_link_by_text("Новые документы"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            # Точное сравнение для страницы новых документов
            expect(page).to_have_url("https://bll.by/docs/new")

        finally:
            page.close()

    @allure.title("Навигация: Мои данные")
    @allure.description("Проверка перехода в Мои данные - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_my_data_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Мои данные".

        Проверяет:
        - Статус код: 200
        - URL: https://ca.bll.by/user/profile (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            with page.expect_response("https://ca.bll.by/user/profile") as response_info:
                assert burger_menu.click_link_by_text("Мои данные"), "Не удалось кликнуть по ссылке"

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена проверяем, что URL содержит ca.bll.by
            current_url = page.url
            assert "ca.bll.by" in current_url, f"URL не содержит ca.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Я эксперт")
    @allure.description("Проверка перехода в Я эксперт - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_expert_profile_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Я эксперт".

        Проверяет:
        - Статус код: 200
        - URL: https://expert.bll.by/user/expert (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            # Используем специфичный селектор для ссылки в бургер-меню
            expert_link = page.locator("a.menu_item_link[href*='expert.bll.by/user/expert']").first

            with page.expect_response("https://expert.bll.by/user/expert") as response_info:
                expert_link.click()

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена проверяем, что URL содержит expert.bll.by
            current_url = page.url
            assert "expert.bll.by" in current_url, f"URL не содержит expert.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Настройка уведомлений")
    @allure.description("Проверка перехода в Настройка уведомлений - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_notification_settings_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Настройка уведомлений".

        Проверяет:
        - Статус код: 200
        - URL: https://ca.bll.by/notification/settings (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            # Используем специфичный селектор для ссылки в бургер-меню
            settings_link = page.locator("a.menu_item_link[href*='notification/settings']").first

            with page.expect_response("https://ca.bll.by/notification/settings") as response_info:
                settings_link.click()

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена проверяем, что URL содержит ca.bll.by
            current_url = page.url
            assert "ca.bll.by" in current_url, f"URL не содержит ca.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Личный кабинет")
    @allure.description("Проверка перехода в Личный кабинет - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_personal_account_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Личный кабинет".

        Проверяет:
        - Статус код: 200
        - URL: https://business-info.by/pc (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            # Используем специфичный селектор для ссылки в бургер-меню
            account_link = page.locator("a.menu_item_link[href*='business-info.by/pc']").first

            with page.expect_response("https://business-info.by/pc") as response_info:
                account_link.click()

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена проверяем, что URL содержит business-info.by
            current_url = page.url
            assert "business-info.by" in current_url, f"URL не содержит business-info.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Бонусы")
    @allure.description("Проверка перехода в Бонусы - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_bonuses_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Бонусы".

        Проверяет:
        - Статус код: 200
        - URL: https://bonus.bll.by (внешний домен)
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            # Используем специфичный селектор для ссылки в бургер-меню
            bonuses_link = page.locator("a.menu_item_link[href*='bonus.bll.by']").first

            with page.expect_response("https://bonus.bll.by") as response_info:
                bonuses_link.click()

            response = response_info.value
            assert response.status in [200, 201, 301, 302], f"Неверный статус код: {response.status}"

            # Для внешнего домена проверяем, что URL содержит bonus.bll.by
            current_url = page.url
            assert "bonus.bll.by" in current_url, f"URL не содержит bonus.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Телефонный номер")
    @allure.description("Проверка клика по телефонному номеру - открытие приложения")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.refactored
    def test_phone_number_click(self, authenticated_burger_context):
        """
        Проверка клика по телефонному номеру "+375 17 388 32 52".

        Проверяет:
        - Возможность клика по телефонной ссылке
        - Примечание: При клике открывается приложение телефона в Windows
        """
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            assert burger_menu.open_menu(), "Не удалось открыть бургер-меню"

            # Ищем телефонную ссылку по номеру
            phone_link = page.get_by_role("link", name="+375 17 388 32")

            # Проверяем, что ссылка существует и кликабельна
            assert phone_link.is_visible(), "Телефонная ссылка не найдена"

            # Для телефонных ссылок мы можем только проверить наличие и кликабельность
            # Сам клик может открыть внешнее приложение телефона
            # Поэтому просто проверяем, что элемент существует
            phone_href = phone_link.get_attribute("href")
            assert phone_href and phone_href.startswith("tel:"), f"Неверный href для телефонной ссылки: {phone_href}"

            # Примечание: Фактический клик закомментирован, так как открывает внешнее приложение
            # phone_link.click()  # Раскомментировать для реального тестирования

        finally:
            page.close()
