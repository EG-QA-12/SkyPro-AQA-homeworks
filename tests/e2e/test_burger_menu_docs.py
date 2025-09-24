"""
Гибридные E2E тесты валидации бургер-меню на основе реальных сценариев из Codegen.

Эти тесты сочетают проверку URL переходов и валидацию контента страниц:
- Проверка корректности URL и статус кодов (200/201)
- Проверка наличия ожидаемых заголовков на целевых страницах
- Максимальная надежность при приемлемой производительности

Гибридный подход обеспечивает:
- Стабильность URL проверок
- Валидацию правильной загрузки контента
- Быстрое обнаружение проблем с навигацией
"""
import re
import allure
import pytest
from playwright.sync_api import expect


class TestBurgerMenuHybridValidationCodegen:
    """
    Гибридные тесты валидации бургер-меню.

    Каждый тест проверяет:
    1. Корректность URL перехода и статус код
    2. Наличие ожидаемого контента на странице
    3. Работоспособность навигации

    Оптимизация: меню сохраняется на большинстве страниц,
    поэтому не всегда требуется возврат на главную.
    """

    def _ensure_menu_available(self, page):
        """
        Гарантированная подготовка меню для каждого теста.

        Каждый тест должен быть изолированным, поэтому:
        1. Всегда начинаем с главной страницы
        2. Открываем бургер-меню
        3. Проверяем что меню доступно
        """
        # Для изоляции тестов всегда начинаем с главной страницы
        page.goto("https://bll.by/", wait_until="domcontentloaded")

        # Открываем бургер-меню
        page.get_by_role("link").filter(has_text=re.compile(r"^$")).first.click()

        # Проверяем что меню открылось (используем селектор из меню)
        expect(page.get_by_role("banner").get_by_role("link", name="Новости")).to_be_visible()

    @allure.title("Гибридная валидация: Новости")
    @allure.description("Комплексная проверка перехода в Новости с URL и контент валидацией")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    @pytest.mark.critical
    def test_hybrid_news_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Новости".

        Проверяет:
        - URL: https://bll.by/news
        - Статус код: 200
        - Заголовок: "Новости"
        """
        page = authenticated_burger_context.new_page()

        try:
            # Оптимизированная подготовка меню
            self._ensure_menu_available(page)

            # Гибридная проверка: URL + статус код + контент
            with page.expect_response(lambda response: response.url == "https://bll.by/news") as response_info:
                page.get_by_role("banner").get_by_role("link", name="Новости").click()

            # Проверяем статус код
            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"

            # Проверяем URL
            expect(page).to_have_url("https://bll.by/news")

            # Проверяем контент страницы
            expect(page.get_by_role("heading", name="Новости")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Справочная информация")
    @allure.description("Комплексная проверка перехода в Справочную информацию")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    @pytest.mark.critical
    def test_hybrid_reference_info_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Справочная информация".

        Проверяет:
        - URL паттерн: spravochnaya-informatsiya-200083
        - Статус код: 200
        - Заголовок: "Справочная информация"
        """
        page = authenticated_burger_context.new_page()

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.get_by_role("link").filter(has_text=re.compile(r"^$")).first.click()

            with page.expect_response("**/spravochnaya-informatsiya-200083**") as response_info:
                page.get_by_role("banner").get_by_role("link", name="Справочная информация").click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url(re.compile(r".*spravochnaya-informatsiya-200083.*"))
            expect(page.get_by_role("heading", name="Справочная информация")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Кодексы")
    @allure.description("Комплексная проверка перехода в раздел Кодексы")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    @pytest.mark.critical
    def test_hybrid_codes_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Кодексы".

        Проверяет:
        - URL паттерн: kodeksy-dejstvuyushchie-na-territorii-respubliki-belarus-141580
        - Статус код: 200
        - Заголовок: "Кодексы, действующие на территории Республики Беларусь"
        """
        page = authenticated_burger_context.new_page()

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.get_by_role("link").filter(has_text=re.compile(r"^$")).first.click()

            with page.expect_response("**/kodeksy-dejstvuyushchie-na-territorii-respubliki-belarus-141580**") as response_info:
                page.get_by_role("banner").get_by_role("link", name="Кодексы").click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url(re.compile(r".*kodeksy-dejstvuyushchie-na-territorii-respubliki-belarus-141580.*"))
            expect(page.get_by_role("heading", name="Кодексы, действующие на территории Республики Беларусь")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Горячие темы")
    @allure.description("Комплексная проверка перехода в Горячие темы")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    def test_hybrid_hot_topics_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Горячие темы".

        Проверяет:
        - URL паттерн: goryachie-temy-200085
        - Статус код: 200
        - Заголовок: "Горячие темы"
        """
        page = authenticated_burger_context.new_page()

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.get_by_role("link").filter(has_text=re.compile(r"^$")).first.click()

            with page.expect_response("**/goryachie-temy-200085**") as response_info:
                page.get_by_role("banner").get_by_role("link", name="Горячие темы").click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url(re.compile(r".*goryachie-temy-200085.*"))
            expect(page.get_by_role("heading", name="Горячие темы")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Навигаторы")
    @allure.description("Комплексная проверка перехода в раздел Навигаторы")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    def test_hybrid_navigators_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Навигаторы".

        Проверяет:
        - URL паттерн: navigatory-140000
        - Статус код: 200
        - Заголовок: "Навигаторы"
        """
        page = authenticated_burger_context.new_page()

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.get_by_role("link").filter(has_text=re.compile(r"^$")).first.click()

            with page.expect_response("**/navigatory-140000**") as response_info:
                page.get_by_role("banner").get_by_role("link", name="Навигаторы").click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url(re.compile(r".*navigatory-140000.*"))
            expect(page.get_by_role("heading", name="Навигаторы")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Чек-листы")
    @allure.description("Комплексная проверка перехода в раздел Чек-листы")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    def test_hybrid_checklists_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Чек-листы".

        Проверяет:
        - URL паттерн: perechen-tem-chek-list-dokumentov-487105
        - Статус код: 200
        - Заголовок: "Чек-листы документов"
        """
        page = authenticated_burger_context.new_page()

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.get_by_role("link").filter(has_text=re.compile(r"^$")).first.click()

            with page.expect_response("**/perechen-tem-chek-list-dokumentov-487105**") as response_info:
                page.locator(".container").first.click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url(re.compile(r".*perechen-tem-chek-list-dokumentov-487105.*"))
            expect(page.get_by_role("heading", name="Чек-листы документов")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Каталоги форм")
    @allure.description("Комплексная проверка перехода в Каталоги форм")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    def test_hybrid_catalogs_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Каталоги форм".

        Проверяет:
        - URL паттерн: katalogi-form-22555
        - Статус код: 200
        - Заголовок: "Каталоги форм"
        """
        page = authenticated_burger_context.new_page()

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.get_by_role("link").filter(has_text=re.compile(r"^$")).first.click()

            with page.expect_response("**/katalogi-form-22555**") as response_info:
                page.get_by_role("banner").get_by_role("link", name="Каталоги форм").click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url(re.compile(r".*katalogi-form-22555.*"))
            expect(page.get_by_role("heading", name="Каталоги форм")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Конструкторы")
    @allure.description("Комплексная проверка перехода в раздел Конструкторы")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    def test_hybrid_constructors_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Конструкторы".

        Проверяет:
        - URL паттерн: konstruktory-200077
        - Статус код: 200
        - Заголовок: "Конструкторы"
        """
        page = authenticated_burger_context.new_page()

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.get_by_role("link").filter(has_text=re.compile(r"^$")).first.click()

            with page.expect_response("**/konstruktory-200077**") as response_info:
                page.get_by_role("banner").get_by_role("link", name="Конструкторы").click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url(re.compile(r".*konstruktory-200077.*"))
            expect(page.get_by_role("heading", name="Конструкторы")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Справочники")
    @allure.description("Комплексная проверка перехода в раздел Справочники")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    def test_hybrid_directories_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Справочники".

        Проверяет:
        - URL паттерн: spravochniki-220099
        - Статус код: 200
        - Заголовок: "Справочники"
        """
        page = authenticated_burger_context.new_page()

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.get_by_role("link").filter(has_text=re.compile(r"^$")).first.click()

            with page.expect_response("**/spravochniki-220099**") as response_info:
                page.get_by_role("banner").get_by_role("link", name="Справочники").click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url(re.compile(r".*spravochniki-220099.*"))
            expect(page.get_by_role("heading", name="Справочники")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Калькуляторы")
    @allure.description("Комплексная проверка перехода в раздел Калькуляторы")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    def test_hybrid_calculators_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Калькуляторы".

        Проверяет:
        - URL паттерн: kalkulyatory-40171
        - Статус код: 200
        - Заголовок: "Калькуляторы"
        """
        page = authenticated_burger_context.new_page()

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.get_by_role("link").filter(has_text=re.compile(r"^$")).first.click()

            with page.expect_response("**/kalkulyatory-40171**") as response_info:
                page.get_by_role("banner").get_by_role("link", name="Калькуляторы").click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url(re.compile(r".*kalkulyatory-40171.*"))
            expect(page.get_by_role("heading", name="Калькуляторы")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Тесты")
    @allure.description("Комплексная проверка перехода в раздел Тесты")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    def test_hybrid_tests_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Тесты".

        Проверяет:
        - URL паттерн: testy-dlya-proverki-znanij-212555
        - Статус код: 200
        - Заголовок: "Тесты для проверки знаний"
        """
        page = authenticated_burger_context.new_page()

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.get_by_role("link").filter(has_text=re.compile(r"^$")).first.click()

            with page.expect_response("**/testy-dlya-proverki-znanij-212555**") as response_info:
                page.get_by_role("banner").get_by_role("link", name="Тесты").click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url(re.compile(r".*testy-dlya-proverki-znanij-212555.*"))
            expect(page.get_by_role("heading", name="Тесты для проверки знаний")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Полезные ссылки")
    @allure.description("Комплексная проверка перехода в Полезные ссылки")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    def test_hybrid_useful_links_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Полезные ссылки".

        Проверяет:
        - URL паттерн: poleznye-ssylki-219924
        - Статус код: 200
        - Наличие текста "Каталог полезных ссылок"
        """
        page = authenticated_burger_context.new_page()

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.get_by_role("link").filter(has_text=re.compile(r"^$")).first.click()

            with page.expect_response("**/poleznye-ssylki-219924**") as response_info:
                page.get_by_role("banner").get_by_role("link", name="Полезные ссылки").click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url(re.compile(r".*poleznye-ssylki-219924.*"))
            expect(page.get_by_role("cell", name="Дополнительная информацияУстановить закладкуКомментарии Каталог полезных ссылок")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Словарь")
    @allure.description("Комплексная проверка перехода в раздел Словарь")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    def test_hybrid_dictionary_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Словарь".

        Проверяет:
        - URL: https://bll.by/terms
        - Статус код: 200
        - Наличие текста "Поиск в словаре терминов"
        """
        page = authenticated_burger_context.new_page()

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.get_by_role("banner").get_by_role("link").filter(has_text=re.compile(r"^$")).first.click()

            with page.expect_response("**/terms**") as response_info:
                page.get_by_role("link", name="Словарь").click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url("https://bll.by/terms")
            expect(page.get_by_text("Поиск в словаре терминов")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Ваш личный юрист")
    @allure.description("Комплексная проверка перехода к личному юристу")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    def test_hybrid_personal_lawyer_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Ваш личный юрист".

        Проверяет:
        - URL паттерн: vash-lichnyj-yurist-206044
        - Статус код: 200
        - Заголовок: "Ваш личный юрист"
        """
        page = authenticated_burger_context.new_page()

        try:
            self._ensure_menu_available(page)

            with page.expect_response("**/vash-lichnyj-yurist-206044**") as response_info:
                page.get_by_role("banner").get_by_role("link", name="Ваш личный юрист").click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url(re.compile(r".*vash-lichnyj-yurist-206044.*"))
            expect(page.get_by_role("heading", name="Ваш личный юрист")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Всё по одной теме")
    @allure.description("Комплексная проверка перехода в подборки по темам")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    def test_hybrid_topic_collections_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Всё по одной теме".

        Проверяет:
        - URL паттерн: podborki-vsyo-po-odnoj-teme-200084
        - Статус код: 200
        - Заголовок: "Подборки «Всё по одной теме»"
        """
        page = authenticated_burger_context.new_page()

        try:
            self._ensure_menu_available(page)

            with page.expect_response("**/podborki-vsyo-po-odnoj-teme-200084**") as response_info:
                page.get_by_role("banner").get_by_role("link", name="Всё по одной теме").click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url(re.compile(r".*podborki-vsyo-po-odnoj-teme-200084.*"))
            expect(page.get_by_role("heading", name="Подборки «Всё по одной теме»")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Руководство пользователя")
    @allure.description("Комплексная проверка перехода к руководству пользователя")
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    @pytest.mark.hybrid
    def test_hybrid_user_guide_validation(self, authenticated_burger_context):
        """
        Гибридный тест валидации раздела "Руководство пользователя".

        Проверяет:
        - URL паттерн: rukovodstvo-polzovatelya-platformy-biznes-info-436351
        - Статус код: 200
        - Заголовок: "Руководство пользователя платформы «Бизнес-Инфо»"
        """
        page = authenticated_burger_context.new_page()

        try:
            self._ensure_menu_available(page)

            with page.expect_response("**/rukovodstvo-polzovatelya-platformy-biznes-info-436351**") as response_info:
                page.get_by_role("banner").get_by_role("link", name="Руководство пользователя").click()

            response = response_info.value
            assert response.status in [200, 201], f"Неверный статус код: {response.status}"
            expect(page).to_have_url(re.compile(r".*rukovodstvo-polzovatelya-platformy-biznes-info-436351.*"))
            expect(page.get_by_role("heading", name="Руководство пользователя платформы «Бизнес-Инфо»")).to_be_visible()

        finally:
            page.close()

    @allure.title("Гибридная валидация: Производительность открытия меню")
    @allure.description("Комплексная проверка скорости открытия меню с контент валидацией")
    @pytest.mark.burger_menu
    @pytest.mark.performance
    @pytest.mark.hybrid
    def test_hybrid_menu_performance_with_content(self, authenticated_burger_context):
        """
        Гибридный тест производительности открытия меню.

        Проверяет:
        - Время открытия меню (< 3 сек)
        - Корректность загрузки контента меню
        - Доступность основных ссылок
        """
        page = authenticated_burger_context.new_page()

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")

            import time
            start_time = time.time()

            # Открываем бургер-меню
            page.get_by_role("link").filter(has_text=re.compile(r"^$")).first.click()

            # Ждем появления контента меню
            page.get_by_role("link", name="Новости").wait_for(timeout=5000)

            end_time = time.time()
            open_time = end_time - start_time

            # Проверяем производительность
            assert open_time < 3.0, f"Меню открылось слишком медленно: {open_time:.2f} сек"

            # Проверяем контент
            expect(page.get_by_role("link", name="Новости")).to_be_visible()
            expect(page.get_by_role("link", name="Справочная информация")).to_be_visible()

            # Добавляем метрики в отчет
            allure.attach(
                f"Время открытия меню: {open_time:.2f} сек",
                name="Menu Open Performance",
                attachment_type=allure.attachment_type.TEXT
            )

        finally:
            page.close()